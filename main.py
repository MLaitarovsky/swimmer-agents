import os
import json
import csv
import time
import pandas as pd
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process, LLM
from crewai_tools import SerperDevTool

# 1. Load Env
load_dotenv()

if not os.getenv("OPENAI_API_KEY") or not os.getenv("SERPER_API_KEY"):
    print("Error: API keys not found.")
    exit()

# 2. Tool & LLM
search_tool = SerperDevTool()
# Using the cheaper model is still smart to save money
cheap_llm = LLM(model="gpt-4o-mini")

CSV_FILENAME = "swimmers_report_FINAL_RUN.csv"


def get_processed_swimmers():
    processed = []
    if not os.path.exists(CSV_FILENAME):
        return []
    try:
        # Robust reading
        with open(CSV_FILENAME, "r", encoding="utf-8", errors="replace") as f:
            reader = csv.reader(f)
            next(reader, None)  # Skip header
            for row in reader:
                if row and len(row) > 0:
                    name = row[0].strip()
                    if name and name != "Name":
                        processed.append(name)
    except:
        pass
    return list(set(processed))


def save_single_result(result_output):
    with open(CSV_FILENAME, mode="a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        try:
            clean_json = (
                str(result_output).replace("```json", "").replace("```", "").strip()
            )
            data = json.loads(clean_json)
            writer.writerow(
                [
                    data.get("name", "Unknown").strip(),
                    data.get("role", "Unknown"),
                    data.get("company", "Unknown"),
                    data.get("is_key", "Unknown"),
                    data.get("reason", ""),
                    data.get("linkedin_url", "Not Found"),
                ]
            )
        except:
            writer.writerow(
                [str(result_output), "Error", "Error", "Error", "Error", "Error"]
            )


def load_swimmers_from_csv(csv_path):
    try:
        df = pd.read_csv(csv_path)
        if "Name" in df.columns:
            return [str(n).strip() for n in df["Name"].tolist() if str(n).strip()]
    except:
        return []
    return []


# --- MAIN LOOP ---
if __name__ == "__main__":

    if not os.path.exists(CSV_FILENAME):
        with open(CSV_FILENAME, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(
                ["Name", "Role", "Company", "Is Key Position", "Reason", "LinkedIn"]
            )

    all_swimmers = load_swimmers_from_csv("all_swimmers_cleaned.csv")
    processed_names = get_processed_swimmers()
    swimmers_to_run = [n for n in all_swimmers if n not in processed_names]

    print(f"🚀 Starting processing for {len(swimmers_to_run)} swimmers...")

    for index, swimmer_name in enumerate(swimmers_to_run):
        print(f"[{index+1}/{len(swimmers_to_run)}] Processing: {swimmer_name}...")

        # --- RE-DEFINE AGENTS INSIDE LOOP (Prevents memory leaks/duplicates) ---
        researcher = Agent(
            role="Researcher",
            goal=f"Find professional details for {swimmer_name}",
            backstory="You are an expert researcher. You only use data found in the current search. You never invent information.",
            verbose=False,
            tools=[search_tool],
            llm=cheap_llm,
        )

        analyst = Agent(
            role="Analyst",
            goal=f"Analyze career of {swimmer_name}",
            backstory="You analyze job titles. You are strict and factual.",
            verbose=False,
            llm=cheap_llm,
        )

        task_search = Task(
            description=f"""
            Search for the Israeli swimmer: '{swimmer_name}'.
            1. Search query: "{swimmer_name} Israel LinkedIn"
            2. IMPORTANT: Verify the profile belongs to THIS specific person. 
               Do NOT use information about 'Aviv Oren' or anyone else. 
               If you cannot find '{swimmer_name}', return 'Not Found'.
            3. Extract: Current Job Title, Company, LinkedIn URL.
            """,
            expected_output="Profile info or 'Not Found'.",
            agent=researcher,
        )

        task_analyze = Task(
            description=f"""
            Analyze the findings for '{swimmer_name}'.
            Output ONLY valid JSON.
            
            {{
                "name": "{swimmer_name}",
                "role": "...", 
                "company": "...",
                "is_key": "Yes/No",
                "reason": "...",
                "linkedin_url": "..."
            }}
            """,
            expected_output="JSON object.",
            agent=analyst,
            context=[task_search],
        )

        crew = Crew(
            agents=[researcher, analyst],
            tasks=[task_search, task_analyze],
            process=Process.sequential,
        )

        # --- RATE LIMIT PROTECTION ---
        while True:
            try:
                output = crew.kickoff()
                save_single_result(output)
                time.sleep(5)  # Resting to avoid 429
                break  # Success, exit retry loop
            except Exception as e:
                error_msg = str(e).lower()
                if "rate_limit" in error_msg or "429" in error_msg:
                    print("⏳ Rate limit hit. Sleeping for 60 seconds...")
                    time.sleep(60)
                    continue  # Retry the same swimmer
                else:
                    print(f"⚠️ Error with {swimmer_name}: {e}")
                    # Save error and move to next person
                    with open(
                        CSV_FILENAME, mode="a", newline="", encoding="utf-8"
                    ) as f:
                        writer = csv.writer(f)
                        writer.writerow(
                            [swimmer_name, "Script Error", str(e), "Error", "", ""]
                        )
                    break

    print("🎉 DONE!")
