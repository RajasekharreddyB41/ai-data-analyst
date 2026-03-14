# 📊 AI Data Analyst Agent

An AI-powered data analysis agent that converts natural language queries into automated data analysis workflows, generating visualizations and insights from uploaded datasets.

🔗 **[Live Demo](https://ai-data-analyst-rb06.streamlit.app)**

## Features

- **Upload CSV / Excel** — Supports both file formats
- **Natural Language Queries** — Ask questions in plain English
- **Auto-Profiling** — Instant dataset insights on upload (stats, correlations, missing values)
- **Smart Routing** — Agent decides whether to analyze, visualize, or both
- **Automatic Charts** — Generates Plotly visualizations from your questions
- **Self-Healing Code** — Auto-fixes generated code when errors occur (up to 3 retries)
- **Multi-Turn Memory** — Agent remembers previous questions for follow-up queries
- **Downloadable PDF Report** — Export your analysis as a professional report

## Tech Stack

- **LangGraph** — Agent orchestration with conditional routing
- **Streamlit** — Interactive web UI
- **Groq (Llama 3.3 70B)** — Fast LLM inference
- **Pandas** — Data analysis
- **Plotly** — Interactive visualizations
- **FPDF2** — PDF report generation

## Architecture
```
User Query → Router Node → Analyze / Visualize / Both → Self-Healing Execution → Summarizer → Response
```

The agent uses a LangGraph state graph with conditional edges:
- **Router Node** — Classifies query intent
- **Analyzer Node** — Generates and executes pandas code
- **Visualizer Node** — Generates Plotly charts
- **Summarizer Node** — Explains results in plain English
- **Self-Healing** — Catches errors, sends traceback to LLM, retries with fixed code

## Getting Started

### Prerequisites
- Python 3.11+
- Free Groq API key from [console.groq.com](https://console.groq.com)

### Local Setup
```bash
git clone https://github.com/RajasekharreddyB41/ai-data-analyst.git
cd ai-data-analyst
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

### Usage
1. Enter your Groq API key in the sidebar
2. Upload a CSV or Excel file
3. Ask questions like:
   - "What is the total revenue?"
   - "Show monthly revenue trend"
   - "Which region has the highest sales?"
   - "Now break that down by product" (follow-up)
4. Download PDF report from the sidebar

## Example Queries

| Query | Route |
|-------|-------|
| "What is the total revenue?" | Analyze |
| "Show monthly revenue trend" | Visualize |
| "Compare revenue by region with a chart" | Both |
| "Now filter that by Q4" | Analyze (with memory) |

## License
MIT
```

Save the file. Now push this update:
```
git add .
git commit -m "Add professional README"
git push