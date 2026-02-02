import os
import json
import csv
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

# --- AGENT 2: ANALYST (FIXED LOGIC) ---
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


def save_results_to_csv(results_list):
    filename = "swimmers_report_final.csv"
    with open(filename, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["Name", "Role", "Company", "Is Key Position", "Reason"])

        for result in results_list:
            try:
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


# --- LOAD NAMES FROM FILE ---
# This reads the list you just scraped!
try:
    with open("swimmers_list.txt", "r", encoding="utf-8") as f:
        # Read lines and strip whitespace (limit to first 5 for testing to save time/money)
        swimmers_list = [line.strip() for line in f.readlines() if line.strip()]

        # PRO TIP: Uncomment this line to run ALL names (warning: takes a long time)
        # swimmers_list = swimmers_list

        # For now, let's just do the first 5 to test the logic
        print(f"Loaded {len(swimmers_list)} names. Running test on the first 5...")
        swimmers_list = swimmers_list[:5]

except FileNotFoundError:
    print("Error: 'swimmers_list.txt' not found. Did you run scraper.py?")
    exit()

results = []

for swimmer_name in swimmers_list:
    print(f"\n--- Processing: {swimmer_name} ---")

    task_search = Task(
        description=f"""
        Search for '{swimmer_name}' (Israeli Olympic Swimmer). 
        Find their current Job Title and Company.
        Verification: Ensure it is the swimmer, not a different person.
        """,
        expected_output="Profile with Name, Role, and Company.",
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
