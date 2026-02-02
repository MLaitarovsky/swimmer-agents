# 🏊 Olympic Swimmer Career Tracker (AI Agents)

## 📌 Project Overview
This project uses **AI Agents (CrewAI)** to analyze the post-retirement careers of elite Israeli swimmers. 
The system automates the process of "Headhunting" by:
1.  **Scraping** a dynamic list of Olympic athletes from Wikipedia.
2.  **Deploying a Researcher Agent** to find their current roles via Google Search & Serper API.
3.  **Deploying an Analyst Agent** to evaluate if they hold "Key Positions" (C-Level, VP, Founders) in the Tech/Business sectors.

## 🛠️ Tech Stack
* **Python 3.10+**
* **CrewAI** (Multi-Agent Orchestration)
* **LangChain** (LLM Logic)
* **BeautifulSoup4** (Web Scraping)
* **OpenAI API** (Intelligence)
* **Serper API** (Google Search capability)
* **Docker** (Containerization)

## ⚙️ How it Works
1.  `scraper.py`: Fetches the latest list of swimmers using a custom User-Agent to bypass protections.
2.  `main.py`: Initiates the Agent Crew.
    * **Agent A (Researcher):** searches for professional footprints.
    * **Agent B (Analyst):** applies strict logic to classify "Key Positions".
3.  **Output:** Generates a structured `swimmers_report_final.csv` for analysis.

## 🚀 Installation (Local)
1. Clone the repo
2. Install dependencies: `pip install -r requirements.txt`
3. Add API keys to `.env`
4. Run `python main.py`

## 🐳 Docker Support
Don't want to mess with Python environments? You can run the entire system in a container.

1. **Build the image:**
```bash
docker build -t swimmer-agent .
