# 🤖 Autonomous Multi-Agent Job Application Pipeline

An end-to-end, stateful agentic system built to automate the job application process. Powered by **LangGraph**, **Groq (Llama 3)**, **Google Gemini 1.5 Flash (Vision)**, **browser-use**, **Playwright**, and **Streamlit**, this pipeline scouts entry-level roles, dynamically tailors resumes under strict zero-hallucination guardrails, self-corrects for ATS optimization, and visually navigates web portals to submit applications.

---

## 🏛️ System Architecture

The workflow is engineered as a stateful graph using **LangGraph**. Each stage operates as a specialized node that inspects, modifies, and passes an isolated state dictionary through the pipeline.

```mermaid
graph TD
    A[Target Job / JD Input] --> B[Scout Filter Node]
    B -- Non-Matching Role --> C[Exit / Skip]
    B -- Role Approved --> D[Tailor Agent <br/> <i>Groq / Llama 3</i>]
    
    subgraph Refinement Loop
        D --> E[ATS Evaluator <br/> <i>LLM-as-a-Judge</i>]
        E -- Score < 90 --> D
    end

    E -- Score ≥ 90 --> F[Playwright Compiler]
    F -- PDF Generated --> G[Human-in-the-Loop <br/> <i>Pre-Submit Review</i>]
    G -- Approved --> H[Browser Applier <br/> <i>Gemini 1.5 Flash Vision</i>]
    G -- Rejected --> C
    H --> I[CSV Logger & Streamlit Dashboard]

### Node Breakdown

1. **Scout Filter Node:** Evaluates raw job descriptions against structured target criteria (e.g., fresher/entry-level keywords) before invoking heavy LLM processing, optimizing execution speed and API resource usage.
2. **Tailor Agent (Groq / Llama 3 120B):** Reads `master_profile.json` and maps verified technical skills, project metrics, and internship experiences to match the job description. Operates under strict prompt constraints that prevent invented credentials.
3. **ATS Evaluator (LLM-as-a-Judge):** Benchmarks generated resume drafts against a 100-point rubric covering Hard Skills Coverage, Contextual Alignment, and Formatting.
4. **Self-Correction Loop:** If the ATS Evaluator score falls below 90/100, the graph automatically routes the critique back to the Tailor Agent for focused revisions (capped at a maximum iteration threshold).
5. **PDF Compiler:** Uses **Playwright** to compile the approved Markdown document into a clean, single-page, ATS-readable PDF artifact (`job_<ID>_tailored.pdf`).
6. **Human-in-the-Loop (HITL) Guardrail:** Pauses execution state, prompting terminal confirmation (`y/n`) and allowing manual visual inspection of generated PDFs prior to web submission.
7. **Browser Applier (Gemini 1.5 Flash Vision & `browser-use`):** Launches a persistent Google Chrome session. Uses multimodal visual reasoning to locate input fields, attach generated PDFs, solve dynamic UI challenges, and complete form submissions on platforms such as LinkedIn and Naukri.
8. **Telemetry & Logging:** Formats execution results, ATS scores, and application timestamps into `data/applications_log.csv` for real-time tracking in the dashboard.

---

## ✨ Engineering Highlights

* **Deterministic Zero-Hallucination Policy:** The Tailor Agent is strictly bound to data extracted from `master_profile.json`. It rephrases and highlights matching experience without fabricating tools, dates, or titles.
* **LLM-as-a-Judge Pattern:** Implements autonomous self-correction via an evaluation loop that enforces production-ready resume quality prior to submission.
* **Persistent Authentication:** Leverages local Google Chrome debugging profiles to inherit pre-authenticated web sessions, completely bypassing login screens and 2FA walls.
* **Multimodal DOM Navigation:** Uses vision-augmented agents to interpret UI elements rendered on screen, avoiding fragile XPath/CSS selector dependencies that fail during website updates.
* **Real-Time Telemetry Dashboard:** Integrated **Streamlit** dashboard visualizing total throughput, success rates, average ATS scores, and historical logs.

---

## 🛠 Tech Stack

| Domain | Technologies |
| :--- | :--- |
| **Agent Orchestration** | LangGraph, LangChain Core |
| **Language Models** | Groq API (`llama-3.3-70b` / `llama3-70b-8192`), Google GenAI (`gemini-1.5-flash`) |
| **Browser Automation** | `browser-use`, Playwright, Asyncio |
| **Data & Dashboard** | Streamlit, Pandas, Python 3.11+ |
| **Document Processing** | Python-Markdown, HTML-to-PDF via Headless Chromium |

---

## 📂 Project Structure

```text
autonomous-job-agent/
├── data/
│   ├── master_profile.json       # Central database of skills, projects & experience
│   ├── applications_log.csv      # Persistent application metrics log
│   └── generated_resumes/        # Output PDF artifacts directory
├── src/
│   ├── agents/
│   │   ├── scout.py              # Filtering and pre-qualification logic
│   │   ├── tailor.py             # Llama-3 resume tailoring agent
│   │   ├── evaluator.py          # LLM-as-a-Judge ATS scoring node
│   │   ├── compiler.py           # Playwright PDF rendering engine
│   │   └── applier.py            # Gemini Vision browser navigation agent
│   ├── graph.py                  # LangGraph state machine definition
│   └── main.py                   # CLI entrypoint & execution loop
├── dashboard.py                  # Streamlit analytics dashboard
├── .env.example                  # Template for required environment variables
├── .gitignore                    # Version control exclusions
├── requirements.txt              # Dependency specifications
└── README.md                     # Project documentation
🚀 Getting Started
1. Prerequisites
Python 3.11 or higher

Google Chrome installed locally

Active API keys for Groq and Google AI Studio

2. Environment Setup
Clone the repository and install dependencies:

Bash
git clone [https://github.com/santhoshvemuluri/autonomous-job-agent.git](https://github.com/santhoshvemuluri/autonomous-job-agent.git)
cd autonomous-job-agent

python -m venv venv
# On Windows PowerShell:
.\venv\Scripts\Activate.ps1

pip install -r requirements.txt
playwright install chromium
3. Configure Credentials
Create a .env file in the root directory:

Code snippet
GROQ_API_KEY=your_groq_api_key_here
GOOGLE_API_KEY=your_google_api_key_here
4. Personalize Candidate Data
Populate data/master_profile.json with your technical skills, internship experiences, projects, and credentials using explicit key-value structures.

5. Execution
Run the primary application pipeline:

Bash
python -m src.main
Launch the telemetry dashboard in a secondary terminal:

Bash
streamlit run dashboard.py
📜 License
Distributed under the MIT License. See LICENSE for details.


<FollowUp label="Want to add an automated GitHub Actions workflow to check code quality?" query
