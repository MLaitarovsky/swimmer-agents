import os
import json
import csv
import pandas as pd  # <--- New Import
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process
from crewai_tools import SerperDevTool

load_dotenv()

# Setup
if not os.getenv("OPENAI_API_KEY") or not os.getenv("SERPER_API_KEY"):
    print("Error: API keys not found.")
    exit()

search_tool = SerperDevTool()

# --- AGENT 1: RESEARCHER ---
researcher = Agent(
    role="Senior Career Researcher",
    goal="Find current professional details about former swimmers.",
    backstory="""You are an expert headhunter. You find accurate career info on former athletes.
    You are persistent. If you find a LinkedIn profile, you extract the headline.""",
    verbose=True,
    tools=[search_tool],
)

# --- AGENT 2: ANALYST ---
analyst = Agent(
    role="Talent Analyst",
    goal='Determine if a candidate holds a "Key Position" in the industry.',
    backstory="""You are a VC investor looking for decision-makers.
    You analyze job titles carefully.
    
    CRITICAL RULES FOR "KEY POSITION":
    1. YES: Co-founder, Founder, Owner, Partner.
    2. YES: C-Level (CEO, CTO, COO, CMO, CFO).
    3. YES: VP (Vice President), Director, Head of [Department].
    4. YES: Senior/Lead roles in Tech/Engineering (e.g., Senior Backend Engineer, Team Lead).
    5. NO: Manager (if not senior), Associate, Student, Coach, Retired.""",
    verbose=True,
)


def load_swimmers_from_csv(csv_path):
    """Loads the list of names from your new CSV"""
    try:
        df = pd.read_csv(csv_path)
        # Ensure the column name matches your CSV (it was 'Name')
        if "Name" in df.columns:
            return df["Name"].tolist()
        else:
            print(f"❌ Error: Column 'Name' not found in {csv_path}")
            return []
    except Exception as e:
        print(f"❌ Error reading CSV: {e}")
        return []


def save_results_to_csv(results_list):
    filename = "swimmers_report_final.csv"
    with open(filename, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["Name", "Role", "Company", "Is Key Position", "Reason"])

        for result in results_list:
            try:
                # Clean the output string to ensure valid JSON
                clean_json = (
                    str(result).replace("```json", "").replace("```", "").strip()
                )
                data = json.loads(clean_json)
                writer.writerow(
                    [
                        data.get("name", "Unknown"),
                        data.get("role", "Unknown"),
                        data.get("company", "Unknown"),
                        data.get("is_key", "Unknown"),
                        data.get("reason", ""),
                    ]
                )
            except:
                writer.writerow([str(result), "Error", "Error", "Error", ""])
    print(f"\n✅ Success! Results saved to {filename}")


# --- MAIN EXECUTION ---
if __name__ == "__main__":

    # 1. Load the names from your new CSV file
    csv_file = "all_swimmers_cleaned.csv"
    print(f"📂 Loading swimmers from {csv_file}...")
    swimmers_list = load_swimmers_from_csv(csv_file)

    # 🛑 BATCH CONTROL (Very Important!)
    # Change this number to 100 or 1000 later when you are ready.
    BATCH_SIZE = 10

    if swimmers_list:
        swimmers_list = swimmers_list[:BATCH_SIZE]
        print(f"🚀 Starting Research on first {len(swimmers_list)} swimmers...")
    else:
        print("❌ No swimmers found. Exiting.")
        exit()

    results = []

    for swimmer_name in swimmers_list:
        print(f"\n--- Processing: {swimmer_name} ---")

        # UPDATED TASK: Changed "Olympic Swimmer" to "Israeli Swimmer"
        # to handle the national-level athletes in your new list.
        task_search = Task(
            description=f"""
            Conduct a deep investigation for the Israeli swimmer: '{swimmer_name}'.
            
            STEP 1: TRANSLITERATE & SEARCH
            - Search in Hebrew: "{swimmer_name} LinkedIn"
            - Search in English: Guess the English spelling (e.g., '{swimmer_name}' -> 'Name Surname') and search "Name Surname Israel swimmer LinkedIn".
            
            STEP 2: VERIFICATION (CRITICAL)
            - You MUST confirm this is the swimmer, not a random person with the same name.
            - Look for these "Identity Anchors" in their profile:
              * Mention of "Swimming", "Swimmer", "Olympic", "National Team".
              * Education at "Wingate Institute" or a US University (common for Israeli athletes).
              * Volunteering or past roles involving "Maccabi", "Hapoel", or sports associations.
            
            STEP 3: EXTRACT
            - If confirmed, extract: Current Job Title, Company, and LinkedIn URL.
            - If you are unsure (e.g., found 3 "Avi Cohens" and none mention swimming), return "Unverified".
            """,
            expected_output="Profile with English Name, Current Role, Company, and Verification Method.",
            agent=researcher,
        )

        task_analyze = Task(
            description=f"""
            Analyze the role found for '{swimmer_name}'.
            Is it a 'Key Position' based on your rules?
            
            Output ONLY a JSON format:
            {{
                "name": "{swimmer_name}",
                "role": "...",
                "company": "...",
                "is_key": "Yes/No",
                "reason": "Why you decided Yes or No"
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

        output = crew.kickoff()
        results.append(output)

    save_results_to_csv(results)
