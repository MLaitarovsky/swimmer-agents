import os
import json
import csv
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process
from crewai_tools import SerperDevTool

# 1. Load Keys
load_dotenv()

# Check for keys
if not os.getenv("OPENAI_API_KEY") or not os.getenv("SERPER_API_KEY"):
    print("Error: API keys not found. Check your .env file.")
    exit()

# 2. Setup Tools
search_tool = SerperDevTool()

# 3. Define the Agents (The Workers)
# We must define ALL agents BEFORE using them in the loop

researcher = Agent(
    role="Senior Career Researcher",
    goal="Find current professional details about former swimmers.",
    backstory="""You are an expert headhunter specialized in the Israeli sports industry.
    You know how to track down former athletes and find out what companies they work for
    and what their current job titles are.""",
    verbose=True,
    tools=[search_tool],
)

# --- THIS WAS MISSING IN YOUR CODE ---
analyst = Agent(
    role="Talent Analyst",
    goal='Determine if a candidate holds a "Key Position" in the industry.',
    backstory="""You are a VC investor looking for strong connections. 
    You analyze job titles and company sizes. 
    You are looking for: C-Level (CEO, CTO), VPs, Directors, Founders, or Senior Engineers.""",
    verbose=True,
)
# -------------------------------------


# 4. Define the CSV Saving Function
def save_results_to_csv(results_list):
    filename = "swimmers_report.csv"
    with open(filename, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        # Header
        writer.writerow(["Name", "Role", "Company", "Is Key Position"])

        for result in results_list:
            try:
                # Clean the output string from markdown
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
                    ]
                )
            except:
                # If the AI returns unstructured text, save it safely
                writer.writerow([str(result), "Error", "Error", "Error"])

    print(f"\n✅ Success! Results saved to {filename}")


# 5. The List of Targets
swimmers_list = ["Gal Nevo", "Yakov Toumarkin", "Guy Barnea", "Amit Ivry"]

results = []

print(f"Starting research on {len(swimmers_list)} swimmers...")

# 6. The Execution Loop
for swimmer_name in swimmers_list:
    print(f"\n--- Processing: {swimmer_name} ---")

    # Task 1: Search
    task_search = Task(
        description=f"""
        Search for the former Israeli swimmer '{swimmer_name}'. 
        Verification: Ensure the result matches the athlete profile (Swimming/Israel).
        Find their current Job Title and Company.
        """,
        expected_output="Profile with Name, Role, and Company.",
        agent=researcher,
    )

    # Task 2: Analyze
    task_analyze = Task(
        description=f"""
        Analyze the role found for '{swimmer_name}'.
        Is it a 'Key Position' (VP, CEO, Director, Founder, Senior Tech)?
        
        Output ONLY a JSON format:
        {{
            "name": "{swimmer_name}",
            "role": "...",
            "company": "...",
            "is_key": "Yes/No"
        }}
        """,
        expected_output="JSON object.",
        agent=analyst,
        context=[task_search],
    )

    # Create Crew
    crew = Crew(
        agents=[researcher, analyst],
        tasks=[task_search, task_analyze],
        process=Process.sequential,
    )

    # Run
    output = crew.kickoff()
    results.append(output)

# 7. Final Step: Save to File
save_results_to_csv(results)
