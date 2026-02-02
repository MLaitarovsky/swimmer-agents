import os
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process
from crewai_tools import SerperDevTool

# 1. Load environment variables(secret keys) from .env file
load_dotenv()

# Check if the keys are loaded (for debugging purposes)
if not os.getenv("OPENAI_API_KEY") or not os.getenv("SERPER_API_KEY"):
    print("Error: API keys not found. Please check your .env file.")
    exit()

# 2. Set up search Tool
# This is the "browser" the agent will use to look up information
search_tool = SerperDevTool()

# 3. Create the research Agent
researcher = Agent(
    role='Senior Career Researcher',
    goal='Find current professional details about former swimmers.',
    backstory="""You are an expert headhunter specialized in the Israeli sports industry.
    You know how to track down former athletes and find out what companies they work for
    and what their current job titles are.""",
    verbose=True,  # This lets you see the agent "thinking" in the terminal
    allow_delegation=False,
    tools=[search_tool] # We give the agent the Google Search tool
)

# 4. Define the Task
# We will use "Gal Nevo" (famous Israeli swimmer) as our test subject.
find_swimmer_task = Task(
    description="""
    1. Search for the former Israeli swimmer 'Gal Nevo'. 
    2. Verification: The person MUST be the former Olympic swimmer. Do not accept results for other people named Gal Nevo.
    3. Find his current professional role (Job Title) and the Company he works for.
    4. Key Focus: Look for roles in the Tech, Startup, or Sports-Tech sectors.
    5. If you find multiple profiles, prioritize the one that mentions 'Swimming', 'Olympics', or 'SenSwim'.
    """,
    expected_output="A summary including: Name, Current Job Title, Company, and a One-sentence verification (e.g., 'Confirmed this is the swimmer because...').",
    agent=researcher
)

# 5. Form the Crew and Kickoff
crew = Crew(
    agents=[researcher],
    tasks=[find_swimmer_task],
    process=Process.sequential
)

print("### Starting the Agent... ###")
result = crew.kickoff()

print("\n\n########################")
print("## Here is the result ##")
print("########################\n")
print(result)