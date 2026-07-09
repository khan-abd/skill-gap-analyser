# SkillBridge v2: Agentic Career War Room 🚀

**🌍 Access the live web app:** [https://skill-gap-analyser.streamlit.app/](https://skill-gap-analyser.streamlit.app/)

SkillBridge has been completely rebuilt from the ground up as an AI-powered, agentic career readiness platform. It bridges the gap between your resume and the actual hiring bar of top-tier companies. Powered by Gemini (or Groq/OpenAI), SkillBridge intelligently analyzes your profile, scores your readiness, builds an interactive timeline flowchart for preparation, and provides an always-on Career Coach.

## ✨ Features

* **📄 Intelligent Resume Parsing:** Upload your PDF resume. The system uses an LLM to extract your technical skills, soft skills, CGPA, leadership experience, and projects.
* **🏢 Target Companies & Roles:** Select any combination of top MNCs (Bain, Google, Zomato, etc.) and target roles (Data Scientist, Hardware Engineer, HR Manager). You can even type in your own custom roles!
* **📊 5-Axis Scorecard:** Your profile is evaluated holistically against the actual hiring bar of your selected companies. You receive a dynamic, color-coded score (0-100) across:
  * Technical Depth
  * Leadership & Initiative
  * Communication & Presentation
  * Business Acumen
  * Role Fit
* **🗺️ Interactive Preparation Flowchart:** Based on your chosen timeline (e.g., 1 Week, 3 Months), the agent builds a structured JSON roadmap. The app visually renders this into a beautiful, step-by-step interactive vertical flowchart complete with course recommendations.
* **🤖 Always-On Career Coach:** Chat directly with an AI coach that remembers your entire profile, your targeted companies, and your roles. Ask it to run mock cases, optimize your STAR stories, or grill you on your weaknesses.

## 🛠️ Tech Stack

* **Frontend / UI:** [Streamlit](https://streamlit.io/) with a custom editorial warm beige/brown theme and dynamic CSS styling.
* **LLM Engine:** Multi-provider support via `google-genai`, `groq`, or OpenAI REST endpoints.
* **RAG (Retrieval-Augmented Generation):** Custom prompt injection grounding the LLM in real course datasets and job market context.
* **Data Processing:** Pandas
* **Text Extraction:** PyPDF

## 🚀 How to Run Locally

### 1. Clone the repository
```bash
git clone https://github.com/khan-abd/skill-gap-analyzer.git
cd skill-gap-analyzer
```

### 2. Install dependencies
Make sure you have Python 3.9+ installed.
```bash
pip install -r requirements.txt
```

### 3. Run the application
```bash
streamlit run app.py
```
The app will automatically open in your default web browser at `http://localhost:8501`.

## 🔑 API Keys
You can paste your API key directly into the app sidebar. It supports:
- **Gemini** (default)
- **Groq** (starts with `gsk_`)
- **OpenAI** (starts with `sk-`)

## 🤝 Contributing
Contributions, issues, and feature requests are welcome! Feel free to check the issues page.

---
*Built with ❤️ for placement season.*
