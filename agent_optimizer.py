"""
agent_optimizer.py — SkillBridge v2 Agentic Engine
====================================================
4 specialised agents, all RAG-grounded, no SQL database dependency:

  1. extract_full_profile   — holistic story extraction (not just CGPA/skills)
  2. generate_scorecard     — 5-axis company-calibrated scoring
  3. generate_roadmap       — 4-week plan grounded in real course data
  4. chat_coach             — always-on Coach Bridge conversational advisor

Uses raw HTTP requests only. Works with Gemini and OpenAI keys.
"""

import os
import json
import re
import requests
import pandas as pd

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")

SCORECARD_AXES = [
    "Technical Depth",
    "Leadership & Initiative",
    "Communication & Presentation",
    "Business Acumen",
    "Role Fit",
]


class AgenticCareerCoach:
    def __init__(self, api_key: str):
        """
        Constructor to initialize the career coach agent.
        It auto-detects the provider based on the API key prefix:
          - Starts with 'sk-': OpenAI (uses gpt-4o-mini)
          - Starts with 'gsk_': Groq (uses llama-3.3-70b-versatile)
          - Default: Gemini (uses gemini-2.5-flash-lite)
        """
        self.api_key = api_key.strip()
        if self.api_key.startswith("sk-"):
            self.provider = "openai"
            self.model = "gpt-4o-mini"
        elif self.api_key.startswith("gsk_"):
            self.provider = "groq"
            self.model = "llama-3.3-70b-versatile"
        else:
            self.provider = "gemini"
            self.model = "gemini-2.5-flash-lite"

    def check_health(self) -> tuple[bool, str]:
        """
        HEALTH CHECK FEATURE:
        Sends a tiny 1-word prompt to test if the API key and model server are active.
        This prevents the app from failing mid-way through a long analysis.
        Returns:
          - (True, "") if the model responds successfully.
          - (False, "Error message") if the server returns a 503 (busy) or 429 (rate-limited).
        """
        try:
            test_response = self._call_llm(
                system_instruction="You are a health checker. Respond ONLY with the word 'OK'.",
                prompt="Ping test",
                json_mode=False
            )
            # If the response starts with the warning emoji, it means the API call failed
            if test_response.strip().startswith("⚠"):
                return False, test_response
            return True, ""
        except Exception as e:
            return False, str(e)

    # ── Core LLM caller with model fallback chain ──────────────────────────────
    def _call_llm(self, system_instruction: str, prompt: str, json_mode: bool = False) -> str:
        """
        The central router that sends prompts to the selected AI provider.
        It handles formatting, JSON payloads, and error catching.
        """
        try:
            # --- PROVIDER 1: GEMINI ---
            if self.provider == "gemini":
                from google import genai
                from google.genai import types
                
                # Connect to Gemini using the official Google GenAI SDK client
                client = genai.Client(api_key=self.api_key)
                
                # Bundle system instruction inside the prompt to support all API versions safely
                combined_prompt = f"System Instruction:\n{system_instruction}\n\nCandidate Input:\n{prompt}"
                
                # Fallback models list in case the primary one is busy or has rate-limit issues
                models_to_try = [self.model, "gemini-2.5-flash", "gemini-2.0-flash"]
                
                config = None
                if json_mode:
                    config = types.GenerateContentConfig(
                        response_mime_type="application/json"
                    )

                primary_error = ""
                for i, m in enumerate(models_to_try):
                    try:
                        resp = client.models.generate_content(
                            model=m,
                            contents=combined_prompt,
                            config=config
                        )
                        if resp.text:
                            return resp.text
                    except Exception as e:
                        err_msg = str(e)
                        # Save the error of the primary model (index 0) so we can show it to the user
                        if i == 0:
                            primary_error = err_msg
                            
                return f"⚠ LLM Error on {self.model}: {primary_error or 'Connection failed'}"

            # --- PROVIDER 2: GROQ (Uses OpenAI-compatible endpoint) ---
            elif self.provider == "groq":
                resp = requests.post(
                    "https://api.groq.com/openai/v1/chat/completions",
                    headers={
                        "Content-Type": "application/json",
                        "Authorization": f"Bearer {self.api_key}",
                    },
                    json={
                        "model": self.model,
                        "messages": [
                            {"role": "system", "content": system_instruction},
                            {"role": "user", "content": prompt},
                        ],
                        "temperature": 0.3,
                        # If JSON output is requested, tell Groq to structure the output as a JSON object
                        **({"response_format": {"type": "json_object"}} if json_mode else {}),
                    },
                    timeout=60,
                )
                if resp.status_code != 200:
                    return f"⚠ Groq Error {resp.status_code}: {resp.text[:250]}"
                return resp.json()["choices"][0]["message"]["content"]

            # --- PROVIDER 3: OPENAI ---
            else:  # openai
                resp = requests.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers={
                        "Content-Type": "application/json",
                        "Authorization": f"Bearer {self.api_key}",
                    },
                    json={
                        "model": self.model,
                        "messages": [
                            {"role": "system", "content": system_instruction},
                            {"role": "user", "content": prompt},
                        ],
                        "temperature": 0.3,
                        **({"response_format": {"type": "json_object"}} if json_mode else {}),
                    },
                    timeout=60,
                )
                if resp.status_code != 200:
                    return f"⚠ OpenAI Error {resp.status_code}: {resp.text[:250]}"
                return resp.json()["choices"][0]["message"]["content"]

        except Exception as e:
            return f"⚠ Connection Error: {str(e)}"

    def _safe_json(self, raw: str, fallback: dict) -> dict:
        """Parse LLM JSON output, stripping code fences if present."""
        cleaned = re.sub(r"```(?:json)?|```", "", raw).strip()
        try:
            return json.loads(cleaned)
        except Exception:
            return {**fallback, "_parse_error": cleaned[:400]}

    # ── RAG: Load course context from courses.csv ──────────────────────────────
    def _load_course_context(self, skills: list, top_n: int = 12) -> str:
        try:
            df = pd.read_csv(os.path.join(DATA_DIR, "courses.csv"))
            str_cols = [c for c in df.columns if df[c].dtype == object]

            if skills:
                def score_row(row):
                    txt = " ".join(
                        str(row[c]) for c in str_cols if pd.notna(row.get(c))
                    ).lower()
                    return sum(1 for s in skills if s.lower() in txt)

                df["_sc"] = df.apply(score_row, axis=1)
                sample = df.sort_values("_sc", ascending=False).head(top_n)
            else:
                sample = df.head(top_n)

            lines = []
            for _, row in sample.iterrows():
                name = next(
                    (str(row[c]) for c in ["course_name", "name", "title"] if c in row and pd.notna(row.get(c))),
                    str(row.iloc[0]),
                )
                platform = next(
                    (str(row[c]) for c in ["platform", "organization", "university"] if c in row and pd.notna(row.get(c))),
                    "Online",
                )
                rating = next(
                    (str(row[c]) for c in ["course_rating", "rating", "score"] if c in row and pd.notna(row.get(c))),
                    "N/A",
                )
                lines.append(f'- "{name}" | {platform} | ⭐ {rating}')
            return "\n".join(lines) or "No course data found."
        except Exception as e:
            return f"[Course data unavailable: {e}]"

    # ── RAG: Load job context from job_postings.csv ────────────────────────────
    def _load_job_context(self, companies: list, top_n: int = 15) -> str:
        try:
            df = pd.read_csv(os.path.join(DATA_DIR, "job_postings.csv"))
            str_cols = [c for c in df.columns if df[c].dtype == object]

            if companies:
                def score_row(row):
                    txt = " ".join(
                        str(row[c]) for c in str_cols if pd.notna(row.get(c))
                    ).lower()
                    return sum(1 for co in companies if co.lower().split()[0] in txt)

                df["_sc"] = df.apply(score_row, axis=1)
                filtered = df[df["_sc"] > 0].head(top_n)
                if filtered.empty:
                    filtered = df.head(top_n)
            else:
                filtered = df.head(top_n)

            lines = []
            for _, row in filtered.iterrows():
                title = next(
                    (str(row[c]) for c in ["title", "job_title", "position"] if c in row and pd.notna(row.get(c))),
                    "Role",
                )
                company = next(
                    (str(row[c]) for c in ["company_name", "company", "employer"] if c in row and pd.notna(row.get(c))),
                    "Company",
                )
                desc_col = next(
                    (c for c in ["description", "job_description", "summary"] if c in df.columns),
                    None,
                )
                desc = str(row[desc_col])[:180] if desc_col and pd.notna(row.get(desc_col)) else ""
                lines.append(f"- '{title}' at {company}: {desc}")
            return "\n".join(lines) or "No job data found."
        except Exception as e:
            return f"[Job data unavailable: {e}]"

    # ═══════════════════════════════════════════════════════════════════════════
    # Agent 1: Full-Story Profile Extractor
    # ═══════════════════════════════════════════════════════════════════════════
    def extract_full_profile(self, resume_text: str) -> dict:
        """
        Holistic resume extraction — captures everything, not just CGPA and skills.
        Includes leadership, social initiatives, positions of responsibility, awards, etc.
        """
        system = (
            "You are a thorough resume parser. Extract ALL information from this resume holistically. "
            "Do NOT omit any section. Specifically look for and capture: "
            "leadership positions (President, Secretary, Club Head, Society Member), "
            "social entrepreneurship or NGO initiatives, positions of responsibility, "
            "technical AND soft skills, all projects with descriptions, internships, "
            "certifications, awards, extracurricular activities, and any other achievements. "
            "Return ONLY valid JSON with exactly these keys:\n"
            "  name (str), cgpa (float or null), degree (str), college (str), graduation_year (str),\n"
            "  skills (list of str), projects (list of {name: str, description: str}),\n"
            "  leadership (list of str), internships (list of str), certifications (list of str),\n"
            "  extracurriculars (list of str), awards (list of str)"
        )
        raw = self._call_llm(system, f"Resume text:\n\n{resume_text}", json_mode=True)
        return self._safe_json(
            raw,
            {
                "name": "", "cgpa": None, "degree": "", "college": "", "graduation_year": "",
                "skills": [], "projects": [], "leadership": [], "internships": [],
                "certifications": [], "extracurriculars": [], "awards": [],
            },
        )

    # ═══════════════════════════════════════════════════════════════════════════
    # Agent 2: Scorecard Generator (RAG-grounded)
    # ═══════════════════════════════════════════════════════════════════════════
    def generate_scorecard(self, profile: dict, target_companies: list) -> dict:
        """
        5-axis scorecard calibrated to the hiring bar of the selected companies.
        Grounded in real job postings via RAG.
        """
        companies_str = ", ".join(target_companies) if target_companies else "top MNCs"
        job_ctx = self._load_job_context(target_companies)

        system = (
            f"You are a veteran recruiter at {companies_str}. Evaluate this candidate holistically and honestly. "
            f"Score 0–100 on five axes: Technical Depth, Leadership & Initiative, "
            f"Communication & Presentation, Business Acumen, Role Fit. "
            f"Be calibrated — a score of 80+ should be genuinely rare and impressive. "
            f"Consider ALL aspects of their profile, not just technical skills. "
            f"Leadership roles like 'President of Enactus' are HIGHLY valued by consulting and business firms. "
            f"CRITICAL: For each axis, write a very short (max 1-2 sentences) 'insight' in an informal, punchy, and conversational tone. "
            f"Talk to the candidate directly (using 'you'/'your') about what makes them stand out or what they are lacking. Avoid dry or verbose academic reporting. "
            f"Return ONLY valid JSON:\n"
            f"{{\"scores\": {{\"Technical Depth\": {{\"score\": int, \"insight\": str}}, ...}}, "
            f"\"highlight_bullet\": str, \"overall_assessment\": str, \"red_flags\": [str]}}"
        )

        prompt = (
            f"Candidate Profile:\n{json.dumps(profile, indent=2)}\n\n"
            f"Target companies: {companies_str}\n\n"
            f"Real job postings from these companies (RAG context):\n{job_ctx}\n\n"
            f"Evaluate the candidate against this hiring bar. Be specific — reference their actual achievements."
        )

        raw = self._call_llm(system, prompt, json_mode=True)
        return self._safe_json(
            raw,
            {
                "scores": {ax: {"score": 50, "insight": "Analysis pending."} for ax in SCORECARD_AXES},
                "highlight_bullet": "",
                "overall_assessment": "",
                "red_flags": [],
            },
        )

    # ═══════════════════════════════════════════════════════════════════════════
    # Agent 3: RAG Learning Roadmap
    # ═══════════════════════════════════════════════════════════════════════════
    def generate_roadmap(self, profile: dict, target_companies: list) -> str:
        """
        4-week preparation plan tailored to the companies' actual hiring process.
        Course recommendations sourced from courses.csv via RAG.
        """
        companies_str = ", ".join(target_companies) if target_companies else "top MNCs"
        course_ctx = self._load_course_context(profile.get("skills", []))
        name = profile.get("name", "the candidate")

        system = (
            f"You are an elite career mentor who has placed hundreds of students at {companies_str}. "
            f"Design a personalised 4-week preparation plan for {name} based on their full profile. "
            f"Tailor the plan to {companies_str}'s specific interview process and hiring bar. "
            f"Recommend specific courses from the provided list. "
            f"Format in clean markdown with Week 1–4 as headers, practical daily tasks, and a project idea for the end."
        )

        projects_str = ", ".join(
            p.get("name", "") if isinstance(p, dict) else str(p)
            for p in profile.get("projects", [])
        )
        leadership_str = ", ".join(profile.get("leadership", []))

        prompt = (
            f"Profile:\n"
            f"  Name: {name}\n"
            f"  Degree: {profile.get('degree')} from {profile.get('college')}, CGPA: {profile.get('cgpa')}\n"
            f"  Skills: {', '.join(profile.get('skills', [])[:25])}\n"
            f"  Leadership: {leadership_str}\n"
            f"  Projects: {projects_str}\n"
            f"  Internships: {', '.join(profile.get('internships', []))}\n\n"
            f"Target companies: {companies_str}\n\n"
            f"Available courses (RAG — recommend these where relevant):\n{course_ctx}\n\n"
            f"Generate the 4-week roadmap."
        )

        return self._call_llm(system, prompt, json_mode=False)

    # ═══════════════════════════════════════════════════════════════════════════
    # Agent 4: Career Coach — Conversational Career Advisor
    # ═══════════════════════════════════════════════════════════════════════════
    def chat_coach(
        self, history: list, user_message: str, profile: dict, target_companies: list
    ) -> str:
        """
        Always-on conversational coach with full profile and company context.
        Adapts its style based on which companies the user is targeting.
        """
        companies_str = ", ".join(target_companies) if target_companies else "top MNCs"
        name = profile.get("name", "you")
        leadership_str = ", ".join(profile.get("leadership", []))

        system = (
            f"You are 'Career Coach', a sharp and encouraging personal career advisor for {name}. "
            f"You know their complete profile and they are targeting {companies_str}. "
            f"Adapt your advice style to the companies:\n"
            f"  • Consulting (Bain, McKinsey, BCG, PwC, EY, Deloitte, KPMG, Accenture): "
            f"Case frameworks (MECE, Issue Trees), guesstimates, behavioral STAR stories.\n"
            f"  • Analytics (ZS, KPMG Analytics): SQL queries, Excel modelling, business analytics.\n"
            f"  • Product (Zomato, Amazon, Flipkart, Swiggy): Product metrics, root-cause analysis, "
            f"user stories, GTM strategy.\n"
            f"  • Finance (Goldman Sachs, JP Morgan, Mastercard, Amex): Markets, financial modelling, "
            f"valuation, investment thesis.\n"
            f"Reference their actual achievements when relevant (e.g. their leadership as {leadership_str or 'a student leader'}, "
            f"specific projects). Be concise, structured using markdown, and genuinely helpful."
        )

        history_str = ""
        for msg in history[-8:]:
            role = "Candidate" if msg["role"] == "user" else "Career Coach"
            history_str += f"{role}: {msg['content']}\n"

        projects_str = ", ".join(
            p.get("name", "") if isinstance(p, dict) else str(p)
            for p in profile.get("projects", [])
        )

        profile_ctx = (
            f"Candidate: {name} | {profile.get('degree','')} from {profile.get('college','')} "
            f"| CGPA: {profile.get('cgpa','N/A')}\n"
            f"Skills: {', '.join(profile.get('skills', [])[:25])}\n"
            f"Leadership: {leadership_str}\n"
            f"Projects: {projects_str}\n"
            f"Internships: {', '.join(profile.get('internships', []))}\n"
            f"Target companies: {companies_str}"
        )

        prompt = (
            f"{profile_ctx}\n\n"
            f"Conversation so far:\n{history_str}\n"
            f"Candidate: {user_message}\n"
            f"Career Coach:"
        )

        return self._call_llm(system, prompt, json_mode=False)
