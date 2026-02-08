# 🏊 Elite Talent Scout: AI-Powered Athlete Career Intelligence

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![AI Agents](https://img.shields.io/badge/CrewAI-Multi--Agent-orange)](https://crewai.com)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue)](https://www.docker.com/)

## 📌 Project Overview
This project is an **automated intelligence pipeline** designed to identify high-potential talent for the Tech and VC sectors by tracking the post-retirement careers of over **2,000 elite Israeli swimmers**.

Unlike simple web scrapers, this system ingests raw, unstructured data (historical PDF competition results), applies complex text processing algorithms to handle Hebrew language formatting, and deploys a **Multi-Agent AI System (CrewAI)** to locate and analyze professional profiles.

**The Goal:** Automatically identify former elite athletes who have transitioned into "Key Positions" (Founders, C-Level, VPs) in the business world.

## 🚀 Key Features
* **Unstructured Data Ingestion:** Custom parser using `pdfplumber` to extract data from legacy PDF tables (2004-2015).
* **Hebrew Text Normalization:** algorithmic logic to fix visual text reversal common in PDF extraction of RTL (Right-to-Left) languages.
* **Resilient Architecture:** Implements a "Smart Resume" feature. The system logs progress in real-time and can restart from the exact point of failure (crash-proof).
* **Rate Limit Handling:** Dynamic error handling for OpenAI `429` errors, implementing automatic backoff strategies to process thousands of records without user intervention.
* **Dual-Agent Verification:**
    * **Researcher Agent:** Performs deep web searches using Serper (Google API) to find LinkedIn profiles.
    * **Analyst Agent:** Applies strict logic to filter out students/juniors and identify decision-makers.

## 🛠️ Tech Stack
* **Core:** Python 3.11+, Pandas
* **AI Orchestration:** CrewAI (Multi-Agent Systems)
* **LLM:** OpenAI GPT-4o-mini (Optimized for cost/performance balance)
* **Data Extraction:** PDFPlumber, Custom RegEx
* **Search Intelligence:** Serper API (Google Search Wrapper)
* **DevOps:** Docker, Python-Dotenv

## ⚙️ Architecture & Workflow

1.  **Data Extraction (`extract_hebrew_names.py`):**
    * Parses raw PDFs.
    * Reverses Hebrew strings (e.g., converts `ןהכ יבא` to `אבי כהן`).
    * Cleans and dedupes data into `all_swimmers_cleaned.csv`.

2.  **Agent Orchestration (`main.py`):**
    * Loads the dataset and checks the `processed` log to skip completed records.
    * Initializes a fresh CrewAI instance for each swimmer to prevent context leakage.
    * **Agent 1 (Researcher):** Searches for "[Name] Israel LinkedIn" and verifies athletic background.
    * **Agent 2 (Analyst):** Analyzes job titles against "Key Position" heuristics (e.g., Is "VP of R&D" a key role? -> Yes).

3.  **Output:**
    * Data is streamed to `swimmers_report_FINAL_RUN.csv` in real-time.

## 🚀 Installation (Local)

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/YourUsername/swimmer-agents.git](https://github.com/YourUsername/swimmer-agents.git)
    cd swimmer-agents
    ```

2.  **Set up the environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    pip install -r requirements.txt
    ```

3.  **Configure API Keys:**
    Create a `.env` file in the root directory:
    ```env
    OPENAI_API_KEY=sk-your-key-here
    SERPER_API_KEY=your-serper-key-here
    ```

4.  **Run the Pipeline:**
    ```bash
    python main.py
    ```

## 🐳 Docker Support
Run the entire system in an isolated container.

1.  **Build the image:**
    ```bash
    docker build -t swimmer-agent .
    ```

2.  **Run the container:**
    ```bash
    docker run --env-file .env -v $(pwd)/data:/app/data swimmer-agent
    ```

## 📄 License
Distributed under the MIT License. See `LICENSE` for more information.
