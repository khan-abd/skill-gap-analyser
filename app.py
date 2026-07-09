"""
app.py - SkillBridge v2
========================
Warm beige/brown editorial theme.
Two-column layout: left = full audit + roadmap, right = Coach Bridge panel.
No static SQL database - all intelligence is RAG-grounded via Gemini.
"""

import streamlit as st
from resume_parser import extract_text_from_pdf
from agent_optimizer import AgenticCareerCoach, SCORECARD_AXES

# ---------------------------------------------------------------------------- #
# Page Config
# ---------------------------------------------------------------------------- #
st.set_page_config(
    page_title="SkillBridge - Career War Room",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------- #
# CSS - Warm Beige / Brown Theme
# ---------------------------------------------------------------------------- #
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Lora:ital,wght@0,400;0,600;0,700;1,400&family=Inter:wght@300;400;500;600;700&display=swap');

/* Style the header bar to be a premium dark espresso brown strip on top */
header, 
[data-testid="stHeader"], 
[data-testid="stAppHeader"], 
.stAppHeader,
[data-testid="stAppHeader"] > div,
.stAppHeader > div {
    background-color: #2C1A0E !important;
    background: #2C1A0E !important;
    border-bottom: 1px solid #1A0F08 !important;
}
[data-testid="stDecoration"] { display: none !important; }
footer { display: none !important; }

/* Keep header buttons visible and force them to render clean white elements (chevrons, Deploy button, etc.) */
header *, 
[data-testid="stHeader"] *, 
[data-testid="stAppHeader"] *, 
.stAppHeader * {
    color: #FFFFFF !important;
}
header svg, header svg path, header svg polyline,
[data-testid="stHeader"] svg, [data-testid="stHeader"] svg path, [data-testid="stHeader"] svg polyline,
[data-testid="stAppHeader"] svg, [data-testid="stAppHeader"] svg path, [data-testid="stAppHeader"] svg polyline,
.stAppHeader svg, .stAppHeader svg path, .stAppHeader svg polyline {
    color: #FFFFFF !important;
    fill: #FFFFFF !important;
    stroke: #FFFFFF !important;
}

/* Sidebar collapse/expand chevron button - style in clean white on the dark strip */
[data-testid="collapsedControl"], 
[data-testid="stSidebarCollapseButton"],
button[data-testid="collapsedControl"],
button[data-testid="stSidebarCollapseButton"] {
    color: #FFFFFF !important;
    background-color: transparent !important;
    border: none !important;
    display: flex !important;
    visibility: visible !important;
    opacity: 1 !important;
    z-index: 100000 !important;
}
[data-testid="collapsedControl"]:hover,
[data-testid="stSidebarCollapseButton"]:hover {
    background-color: rgba(255, 255, 255, 0.15) !important;
    border-radius: 8px !important;
}

.main .block-container {
    padding-top: 0.5rem !important;
    padding-bottom: 1rem !important;
    max-width: 100% !important;
}

/* Global typography & readability */
html, body { background-color: #F5F0E8 !important; }
.stApp { background-color: #F5F0E8 !important; font-family: 'Inter', sans-serif !important; }

/* Force standard text to use Inter and be legible */
p, li, td, th, label, small {
    color: #2C1A0E !important;
    font-family: 'Inter', sans-serif !important;
}

/* Sidebar structure */
[data-testid="stSidebar"] {
    background-color: #EDE7D9 !important;
    border-right: 2px solid #D4C5B0 !important;
}
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span:not([class*="icon"]) {
    color: #2C1A0E !important;
}
[data-testid="stSidebar"] a {
    color: #8B5E3C !important;
}

/* Typography */
h1, h2, h3, h4 { font-family: 'Lora', serif !important; color: #2C1A0E !important; }
h1 { font-size: 1.85rem !important; font-weight: 700 !important; }
h2 { font-size: 1.4rem !important; font-weight: 600 !important; }
h3 { font-size: 1.1rem !important; font-weight: 600 !important; }

/* Cards */
.card {
    background: #FFFFFF;
    border-radius: 16px;
    padding: 1.4rem 1.6rem;
    box-shadow: 0 2px 16px rgba(44, 26, 14, 0.07);
    margin-bottom: 1.25rem;
    border: 1px solid #E4DDD3;
}

/* Section labels */
.section-label {
    font-family: 'Lora', serif;
    font-size: 0.95rem;
    font-weight: 700;
    color: #8B5E3C !important;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    margin-bottom: 0.8rem;
    display: block;
}

/* Tags */
.tag { display:inline-block; background:#F0EBE3; color:#6F4A2E !important; border-radius:20px; padding:4px 14px; font-size:0.9rem; font-weight:500; margin:3px 4px 3px 0; border:1px solid #D4C5B0; }
.tag-gold { background:#FFF8EE; color:#A0622A !important; border:1px solid #F0C87A; }
.tag-blue { background:#EFF6FF; color:#1E40AF !important; border:1px solid #BFDBFE; }

/* Score bars */
.score-wrap { margin-bottom: 1.25rem; }
.score-label-row { display:flex; justify-content:space-between; align-items:baseline; margin-bottom:6px; }
.score-label-text { font-size:1.05rem; font-weight:600; color:#3D2810 !important; }
.score-num { font-family:'Lora',serif; font-size:1.25rem; font-weight:700; }
.score-bar-bg { background:#EDE7D9; border-radius:99px; height:11px; overflow:hidden; }
.score-bar-fill { height:11px; border-radius:99px; }
.score-insight { font-size:1.05rem; color:#4A3525 !important; margin-top:8px; line-height:1.5; }

/* Chat bubbles */
.user-bubble { background:#8B5E3C; color:#FFFFFF !important; border-radius:18px 18px 4px 18px; padding:0.75rem 1.1rem; margin:0.4rem 0 0.4rem 10%; font-size:1.05rem; line-height:1.5; word-wrap:break-word; }
.coach-bubble { background:#F5F0E8; color:#2C1A0E !important; border-radius:18px 18px 18px 4px; padding:0.75rem 1.1rem; margin:0.4rem 10% 0.4rem 0; font-size:1.05rem; line-height:1.5; border:1px solid #E4DDD3; word-wrap:break-word; }

/* Highlight / alert boxes */
.highlight-box { background:linear-gradient(135deg,#FFF8EE,#FFF2DD); border-left:5px solid #C4956A; border-radius:0 12px 12px 0; padding:1rem 1.25rem; margin-bottom:1.25rem; font-size:1.1rem; color:#5C3A1E !important; line-height:1.6; }
.redflag-box { background:#FFF5F5; border-left:5px solid #F87171; border-radius:0 10px 10px 0; padding:0.6rem 1rem; font-size:1.05rem; color:#7F1D1D !important; margin:0.35rem 0; line-height:1.5; }

/* Expander styling to remove white rectangle */
[data-testid="stExpander"] {
    background-color: transparent !important;
    border: none !important;
    box-shadow: none !important;
}
[data-testid="stExpander"] div[role="button"] {
    background-color: transparent !important;
    border: 1px solid #E4DDD3 !important;
    border-radius: 12px !important;
}
[data-testid="stExpander"] div[data-testid="stExpanderDetails"] {
    background-color: #FFFFFF !important;
    border-radius: 16px !important;
    padding: 1.5rem !important;
    box-shadow: 0 2px 16px rgba(44, 26, 14, 0.07) !important;
    border: 1px solid #E4DDD3 !important;
    margin-top: 0.5rem !important;
}

/* Timeline Flowchart Styling */
.timeline-container {
    position: relative;
    padding-left: 2rem;
    margin-top: 1rem;
    margin-bottom: 2rem;
}
.timeline-container::before {
    content: '';
    position: absolute;
    top: 0;
    bottom: 0;
    left: 8px;
    width: 3px;
    background: #E4DDD3;
    border-radius: 3px;
}
.timeline-item {
    position: relative;
    margin-bottom: 2rem;
}
.timeline-marker {
    position: absolute;
    left: -2rem;
    top: 0.25rem;
    width: 19px;
    height: 19px;
    border-radius: 50%;
    background: #8B5E3C;
    border: 3px solid #FFF8EE;
    box-shadow: 0 0 0 2px #E4DDD3;
    z-index: 1;
}
.timeline-content {
    background: #FFFFFF;
    border: 1px solid #E4DDD3;
    border-radius: 12px;
    padding: 1.2rem 1.5rem;
    box-shadow: 0 2px 10px rgba(44, 26, 14, 0.05);
}
.timeline-timeframe {
    font-size: 0.85rem;
    font-weight: 700;
    color: #C4956A;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-bottom: 0.4rem;
}
.timeline-title {
    font-family: 'Lora', serif;
    font-size: 1.25rem;
    font-weight: 700;
    color: #2C1A0E;
    margin-bottom: 0.75rem;
}
.timeline-task {
    font-size: 1rem;
    color: #4A3525;
    line-height: 1.6;
    margin-bottom: 0.4rem;
    padding-left: 1.2rem;
    position: relative;
}
.timeline-task::before {
    content: '→';
    position: absolute;
    left: 0;
    color: #8B5E3C;
    font-weight: 700;
}

/* Buttons styling (with readable text) */
.stButton > button[kind="primary"] {
    background-color: #8B5E3C !important;
    color: #FFFFFF !important;
    border-radius: 12px !important;
    border: none !important;
    font-family: 'Inter', sans-serif !important;
    font-weight: 600 !important;
    box-shadow: 0 2px 8px rgba(139,94,60,0.2) !important;
}
.stButton > button[kind="primary"]:hover {
    background-color: #6F4A2E !important;
}
.stButton > button[kind="secondary"], .stButton > button:not([kind="primary"]) {
    background-color: #FFFFFF !important;
    color: #2C1A0E !important;
    border: 1px solid #C4A882 !important;
    border-radius: 10px !important;
    font-family: 'Inter', sans-serif !important;
}
.stButton > button[kind="secondary"]:hover {
    border-color: #8B5E3C !important;
    color: #8B5E3C !important;
}

/* Form submit button (Send button) styling - make it readable and warm brown */
[data-testid="stFormSubmitButton"] button, 
button[data-testid="stFormSubmitButton"] {
    background-color: #8B5E3C !important;
    color: #FFFFFF !important;
    border: none !important;
    border-radius: 10px !important;
    font-family: 'Inter', sans-serif !important;
    font-weight: 600 !important;
    padding: 0.55rem 1.2rem !important;
}
[data-testid="stFormSubmitButton"] button *, 
button[data-testid="stFormSubmitButton"] * {
    color: #FFFFFF !important;
}
[data-testid="stFormSubmitButton"] button:hover, 
button[data-testid="stFormSubmitButton"]:hover {
    background-color: #6F4A2E !important;
}

/* Inputs styling */
input[type=text], .stTextInput input, .stTextArea textarea {
    background: #FFFFFF !important;
    border: 1px solid #C4A882 !important;
    border-radius: 10px !important;
    color: #2C1A0E !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.88rem !important;
}
.stTextInput input::placeholder, .stTextArea textarea::placeholder { color: #B8A898 !important; }
.stTextInput input:focus, .stTextArea textarea:focus {
    border-color: #8B5E3C !important;
    box-shadow: 0 0 0 2px rgba(139,94,60,0.15) !important;
}

/* Multiselect style overrides */
[data-testid="stMultiSelect"] > div {
    background: #FFFFFF !important;
    border: 1px solid #C4A882 !important;
    border-radius: 10px !important;
}
[data-testid="stMultiSelect"] span { color: #2C1A0E !important; }

/* Force dropdown menu popup options to have light-coloured text on their default dark backgrounds */
div[role="listbox"] li,
div[data-baseweb="menu"] li,
[data-baseweb="popover"] li,
div[role="listbox"] [role="option"],
div[data-baseweb="menu"] [role="option"] {
    color: #F5F0E8 !important;
}
div[role="listbox"] li *,
div[data-baseweb="menu"] li *,
[data-baseweb="popover"] li *,
div[role="listbox"] [role="option"] *,
div[data-baseweb="menu"] [role="option"] * {
    color: #F5F0E8 !important;
}
/* Selected/Hover state in the dropdown list */
div[role="listbox"] li:hover,
div[data-baseweb="menu"] li:hover,
[data-baseweb="popover"] li:hover,
div[role="listbox"] [role="option"]:hover,
div[data-baseweb="menu"] [role="option"]:hover {
    background-color: #313A43 !important;
    color: #FFFFFF !important;
}
div[role="listbox"] li:hover *,
div[data-baseweb="menu"] li:hover *,
[data-baseweb="popover"] li:hover *,
div[role="listbox"] [role="option"]:hover *,
div[data-baseweb="menu"] [role="option"]:hover * {
    color: #FFFFFF !important;
}

/* File Uploader styling */
[data-testid="stFileUploader"] section {
    background: #FFFFFF !important;
    border: 2px dashed #C4A882 !important;
    border-radius: 12px !important;
    padding: 1.5rem !important;
}
[data-testid="stFileUploader"] button {
    background-color: #8B5E3C !important;
    color: #FFFFFF !important;
    border-radius: 8px !important;
    padding: 0.4rem 1rem !important;
    border: none !important;
}
[data-testid="stFileUploader"] button * {
    color: #FFFFFF !important;
}
[data-testid="stFileUploader"] label {
    font-weight: 600 !important;
    color: #2C1A0E !important;
}

/* Expander custom design */
[data-testid="stExpander"] {
    background: #FFFFFF !important;
    border: 1px solid #E4DDD3 !important;
    border-radius: 14px !important;
}
[data-testid="stExpander"] summary {
    font-weight: 600 !important;
    color: #3D2810 !important;
    background: #FFFFFF !important;
}

/* Status widget */
[data-testid="stStatusWidget"] {
    background: #FFFFFF !important;
    border: 1px solid #E4DDD3 !important;
    border-radius: 14px !important;
}

/* Markdown typography details */
.stMarkdown p, .stMarkdown li, .stMarkdown strong { color: #2C1A0E !important; }
.stMarkdown a { color: #8B5E3C !important; }
.stMarkdown code { background: #F0EBE3 !important; color: #5C3A1E !important; border-radius: 4px; padding: 1px 5px; }

/* Caption rules */
.stCaption, [data-testid="stCaption"] { color: #7A6353 !important; font-size: 0.8rem !important; }

/* Dividers & Custom scrollbars */
hr { border-color: #D4C5B0 !important; opacity: 0.5 !important; }
::-webkit-scrollbar { width: 5px; }
::-webkit-scrollbar-track { background: #F5F0E8; }
::-webkit-scrollbar-thumb { background: #C4A882; border-radius: 99px; }
</style>
""", unsafe_allow_html=True)



# ---------------------------------------------------------------------------- #
# Constants
# ---------------------------------------------------------------------------- #
POPULAR_COMPANIES = sorted([
    "Bain & Company", "McKinsey & Company", "BCG", "ZS Associates",
    "Deloitte", "PwC", "EY", "KPMG", "Accenture", "Oyo",
    "Zomato", "Swiggy", "Flipkart", "Amazon", "Google", "Microsoft",
    "Goldman Sachs", "JP Morgan", "Morgan Stanley", "Mastercard", "American Express",
    "Gartner", "Meesho", "PayTM", "Landmark Group"
])

POPULAR_ROLES = sorted([
    "Data Scientist", "Product Manager", "Software Engineer", "Management Consultant",
    "Business Analyst", "Marketing Manager", "HR Manager", "Financial Analyst",
    "Machine Learning Engineer", "Frontend Developer", "Backend Developer", "Full Stack Developer",
    "UI/UX Designer", "Product Designer", "Operations Manager", "Sales Manager",
    "Supply Chain Analyst", "Investment Banker", "Electronics Engineer", "Hardware Engineer",
    "Cloud Architect", "DevOps Engineer", "Cybersecurity Analyst", "Data Analyst",
    "Data Engineer", "Growth Hacker", "Project Manager", "Scrum Master",
    "Technical Program Manager", "Corporate Strategist", "Risk Analyst"
])

# ---------------------------------------------------------------------------- #
# Session State
# ---------------------------------------------------------------------------- #
for key, default in {
    "analyzed": False, "profile": None, "scorecard": None, "roadmap": None,
    "coach_history": [], "coach_init_done": False,
    "stored_api_key": "", "stored_companies": [], "stored_timeline": "4 Weeks",
    "stored_roles": [],
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

# ---------------------------------------------------------------------------- #
# Sidebar
# ---------------------------------------------------------------------------- #
with st.sidebar:
    st.markdown("## 🎯 SkillBridge")
    st.caption("Your personal career war room")
    st.divider()

    st.markdown('<span class="section-label">📄 Your Resume</span>', unsafe_allow_html=True)
    uploaded_file = st.file_uploader(
        "Upload PDF resume", type=["pdf"], label_visibility="collapsed",
        help="We extract your full story — projects, leadership, CGPA, everything.",
    )
    st.divider()

    st.markdown('<span class="section-label">🏢 Target Companies</span>', unsafe_allow_html=True)
    st.caption("Pick from the list or type any company not shown")
    try:
        target_companies = st.multiselect(
            "Companies", options=POPULAR_COMPANIES, default=[],
            placeholder="Bain, PwC, Zomato...", label_visibility="collapsed",
            accept_new_options=True,
        )
    except TypeError:
        target_companies = st.multiselect(
            "Companies", options=POPULAR_COMPANIES, default=[],
            placeholder="Bain, PwC, Zomato...", label_visibility="collapsed",
        )
        extra = st.text_input("Add another company", placeholder="Type any firm...")
        if extra.strip():
            target_companies = list(target_companies) + [extra.strip()]
    st.divider()

    st.markdown('<span class="section-label">🎯 Target Role</span>', unsafe_allow_html=True)
    st.caption("What job are you aiming for?")
    try:
        target_roles = st.multiselect(
            "Roles", options=POPULAR_ROLES, default=[],
            placeholder="e.g. Data Scientist, HR Manager...", label_visibility="collapsed",
            accept_new_options=True,
        )
    except TypeError:
        target_roles = st.multiselect(
            "Roles", options=POPULAR_ROLES, default=[],
            placeholder="e.g. Data Scientist, HR Manager...", label_visibility="collapsed",
        )
        extra_role = st.text_input("Add another role", placeholder="Type any role...")
        if extra_role.strip():
            target_roles = list(target_roles) + [extra_role.strip()]
    st.divider()

    st.markdown('<span class="section-label">🔑 API Key (Gemini, Groq, or OpenAI)</span>', unsafe_allow_html=True)
    st.caption("Auto-detects: starts with `sk-` (OpenAI), `gsk_` (Groq), otherwise Gemini")
    api_key = st.text_input(
        "API Key", type="default", placeholder="Paste key here...", label_visibility="collapsed",
    )
    st.divider()

    st.markdown('<span class="section-label">⏳ Preparation Timeline</span>', unsafe_allow_html=True)
    st.caption("How much time do you have?")
    prep_timeline = st.selectbox(
        "Timeline", 
        options=["1 Week", "2 Weeks", "4 Weeks", "3 Months", "6 Months"], 
        index=2, label_visibility="collapsed"
    )
    st.divider()

    analyze_btn = st.button("🚀 Run Full Analysis", use_container_width=True, type="primary")
    if analyze_btn:
        if not api_key.strip():
            st.error("Please paste your API Key first.")
            st.stop()
        st.session_state.stored_api_key = api_key.strip()
        st.session_state.stored_companies = list(target_companies)
        st.session_state.stored_timeline = prep_timeline
        st.session_state.stored_roles = list(target_roles)
        st.session_state.profile = None
        st.session_state.scorecard = None
        st.session_state.roadmap = None
        st.session_state.coach_history = []
        st.session_state.coach_init_done = False
        st.session_state.analyzed = True

# ---------------------------------------------------------------------------- #
# Landing Page
# ---------------------------------------------------------------------------- #
if not st.session_state.analyzed:
    _, mid, _ = st.columns([1, 4, 1])
    with mid:
        st.markdown(
            "<div style='text-align:center; padding:3rem 0 1.5rem;'>"
            "<div style='font-size:4.5rem; margin-bottom:0.8rem;'>🎯</div>"
            "<div style='font-family:\"Lora\",serif; font-size:3.2rem; font-weight:700;"
            " color:#2C1A0E; margin-bottom:0.35rem; line-height:1.15;'>SkillBridge</div>"
            "<div style='font-family:\"Lora\",serif; font-size:1.5rem; font-weight:600;"
            " color:#8B5E3C; letter-spacing:0.05em; margin-bottom:1.3rem;'>Career War Room</div>"
            "<p style='font-size:1.05rem; color:#5C3A1E; max-width:520px; margin:0 auto;"
            " line-height:1.8; font-family:Inter,sans-serif;'>"
            "Upload your resume, pick your target companies, and get a "
            "<strong>360&#176; audit of your entire story</strong> &mdash; "
            "leadership, projects, academics &mdash; not just a skills checklist."
            "</p></div>",
            unsafe_allow_html=True,
        )

        c1, c2, c3, c4 = st.columns(4)
        _card = "background:#FFFFFF;border-radius:16px;padding:1.4rem 1rem;border:1px solid #E4DDD3;box-shadow:0 2px 14px rgba(44,26,14,0.07);text-align:center;"
        for col, icon, title, desc in [
            (c1, "📄", "Upload Resume",    "PDF parsed holistically — every section, every achievement"),
            (c2, "🏢", "Pick Companies",   "Type any firm — Bain, PwC, Zomato or beyond"),
            (c3, "📊", "5-Axis Scorecard", "Calibrated to each company's real hiring bar"),
            (c4, "🤝", "Career Coach",     "Always-on AI coach in a live right panel"),
        ]:
            with col:
                st.markdown(
                    f"<div style='{_card}'>"
                    f"<div style='font-size:2rem;margin-bottom:0.6rem;'>{icon}</div>"
                    f"<div style='font-weight:700;font-size:0.88rem;color:#3D2810;margin-bottom:0.4rem;'>{title}</div>"
                    f"<div style='font-size:0.76rem;color:#7A6353;line-height:1.5;'>{desc}</div>"
                    f"</div>",
                    unsafe_allow_html=True,
                )

        st.markdown(
            "<div style='text-align:center;margin-top:2rem;font-size:0.95rem;color:#8B5E3C;font-weight:500;'>"
            "&#8592; Upload your resume &amp; pick companies in the sidebar to begin"
            "</div>",
            unsafe_allow_html=True,
        )
    st.stop()

# ---------------------------------------------------------------------------- #
# Restore session values (persists through chat reruns)
# ---------------------------------------------------------------------------- #
_api_key   = st.session_state.stored_api_key or api_key.strip()
_companies = st.session_state.stored_companies or list(target_companies)
_timeline  = st.session_state.stored_timeline or "4 Weeks"
_roles     = st.session_state.stored_roles or []
coach_obj  = AgenticCareerCoach(_api_key)

# ---------------------------------------------------------------------------- #
if st.session_state.profile is None:
    # Pre-analysis Health Check: Test if the model and API key are working
    is_healthy, health_err = coach_obj.check_health()
    if not is_healthy:
        st.error(
            f"⚠️ **AI Server is not responsive right now.**\n\n"
            f"**Error Details:** `{health_err}`\n\n"
            f"**How to solve this:**\n"
            f"1. **Wait and Retry:** If using Gemini free tier, Google's server is temporarily overloaded (503). Wait 1–2 minutes and click **'Run Full Analysis'** again.\n"
            f"2. **Switch Key:** You can paste a free **Groq** API key (starts with `gsk_`) or an **OpenAI** key (starts with `sk-`) in the sidebar to bypass Google's rate limits instantly."
        )
        st.session_state.analyzed = False  # Reset landing page state so they can edit inputs
        st.stop()

    resume_text = ""
    if uploaded_file is not None:
        try:
            resume_text = extract_text_from_pdf(uploaded_file.read())
        except Exception as e:
            st.warning(f"Could not read PDF: {e}. Running without resume text.")

    if not resume_text.strip():
        resume_text = "No resume provided. Evaluate as a general university student targeting first placement."

    with st.status("🔍 Analysing your full profile...", expanded=True) as status:
        st.write("📖 Extracting your story from the resume...")
        profile = coach_obj.extract_full_profile(resume_text)
        st.session_state.profile = profile
        st.write("✅ Profile extracted — name, CGPA, skills, leadership, projects")

        companies_label = ", ".join(_companies) if _companies else "top MNCs"
        roles_label = ", ".join(_roles) if _roles else "General Role"
        st.write(f"📊 Scoring against {companies_label} hiring bar for {roles_label}...")
        scorecard = coach_obj.generate_scorecard(profile, _companies, _roles)
        st.session_state.scorecard = scorecard
        st.write("✅ Scorecard ready")

        st.write(f"🗺 Building your personalised {_timeline} roadmap...")
        roadmap = coach_obj.generate_roadmap(profile, _companies, _timeline, _roles)
        st.session_state.roadmap = roadmap
        st.write("✅ Roadmap complete")

        status.update(label="✅ Analysis complete!", state="complete", expanded=False)

# ---------------------------------------------------------------------------- #
# Pull cached data
# ---------------------------------------------------------------------------- #
profile   = st.session_state.profile   or {}
scorecard = st.session_state.scorecard or {}
roadmap   = st.session_state.roadmap   or {}
name      = profile.get("name") or "Candidate"
companies_label = ", ".join(_companies) if _companies else "top MNCs"
role_label = ", ".join(_roles) if _roles else ""

# ---------------------------------------------------------------------------- #
# Page Header
# ---------------------------------------------------------------------------- #
hc1, _ = st.columns([3, 1])
with hc1:
    st.markdown(f"## 👋 Hello, {name}!")
    eval_text = f"Evaluated for: **{role_label}** at **{companies_label}**" if role_label else f"Evaluated against: **{companies_label}**"
    if _companies or role_label:
        st.caption(eval_text)
st.divider()

# ---------------------------------------------------------------------------- #
# Two-Column Layout
# ---------------------------------------------------------------------------- #
col_left, col_right = st.columns([3, 2], gap="large")

# ============================= LEFT PANEL ====================================
with col_left:

    # --- Full Profile Card ---
    st.markdown('<span class="section-label">Your Full Profile</span>', unsafe_allow_html=True)
    
    degree = profile.get("degree") or "Degree not found"
    college = profile.get("college") or ""
    grad = profile.get("graduation_year") or ""
    cgpa = profile.get("cgpa")
    cgpa_str = f"{float(cgpa):.2f} / 10.0" if cgpa else "N/A"
    
    profile_html = f'<div class="card">'
    profile_html += f'<div style="display:flex; justify-content:space-between; align-items:baseline; margin-bottom:1rem; border-bottom:1px solid #F0EBE3; padding-bottom:0.75rem;">'
    profile_html += f'  <div>'
    profile_html += f'    <div style="font-size:1.3rem; font-weight:700; color:#2C1A0E;">{degree}</div>'
    if college:
        profile_html += f'    <div style="font-size:1.1rem; color:#7A6353; margin-top:4px;">🏛 {college}' + (f' · Class of {grad}' if grad else '') + f'</div>'
    profile_html += f'  </div>'
    profile_html += f'  <div style="font-size:1.15rem; font-weight:700; color:#2C1A0E;">CGPA: <span style="color:#8B5E3C;">{cgpa_str}</span></div>'
    profile_html += f'</div>'
    
    skills = profile.get("skills", [])
    if skills:
        profile_html += f'<div style="margin-bottom:1.2rem;">'
        profile_html += f'  <div style="font-size:0.95rem; font-weight:700; color:#8B5E3C; text-transform:uppercase; letter-spacing:0.05em; margin-bottom:0.6rem;">Skills</div>'
        profile_html += "".join(f'<span class="tag">{s}</span>' for s in skills)
        profile_html += f'</div>'
        
    leadership = profile.get("leadership", [])
    if leadership:
        profile_html += f'<div style="margin-bottom:1.2rem;">'
        profile_html += f'  <div style="font-size:0.95rem; font-weight:700; color:#8B5E3C; text-transform:uppercase; letter-spacing:0.05em; margin-bottom:0.6rem;">Leadership & Positions of Responsibility</div>'
        profile_html += "".join(f'<span class="tag tag-gold">🏅 {item}</span>' for item in leadership)
        profile_html += f'</div>'
        
    projects = profile.get("projects", [])
    if projects:
        profile_html += f'<div style="margin-bottom:1.2rem;">'
        profile_html += f'  <div style="font-size:0.95rem; font-weight:700; color:#8B5E3C; text-transform:uppercase; letter-spacing:0.05em; margin-bottom:0.6rem;">Projects</div>'
        profile_html += f'  <ul style="margin:0; padding-left:1.2rem; font-size:1.05rem; color:#2C1A0E; line-height:1.6;">'
        for p in projects:
            if isinstance(p, dict):
                n = p.get("name", "Untitled")
                d = (p.get("description") or "")
                d_trunc = f"{d[:140]}..." if len(d)>140 else d
                profile_html += f'    <li style="margin-bottom:0.3rem;"><strong>{n}</strong> — {d_trunc}</li>'
            else:
                profile_html += f'    <li style="margin-bottom:0.3rem;">{p}</li>'
        profile_html += f'  </ul>'
        profile_html += f'</div>'
        
    cols_data = []
    for key, label in [("internships", "Internships"), ("certifications", "Certifications"), ("awards", "Awards")]:
        items = profile.get(key, [])
        if items:
            cols_data.append((label, items))
            
    if cols_data:
        profile_html += f'<div style="display:flex; gap:1.5rem; margin-bottom:1.2rem;">'
        for label, items in cols_data:
            profile_html += f'  <div style="flex:1; min-width:0;">'
            profile_html += f'    <div style="font-size:0.95rem; font-weight:700; color:#8B5E3C; text-transform:uppercase; letter-spacing:0.05em; margin-bottom:0.6rem;">{label}</div>'
            profile_html += f'    <ul style="margin:0; padding-left:1.1rem; font-size:1.0rem; color:#2C1A0E; line-height:1.5;">'
            for it in items:
                profile_html += f'      <li style="margin-bottom:0.25rem;">{it}</li>'
            profile_html += f'    </ul>'
            profile_html += f'  </div>'
        profile_html += f'</div>'
        
    extras = profile.get("extracurriculars", [])
    if extras:
        profile_html += f'<div style="margin-bottom:0.8rem;">'
        profile_html += f'  <div style="font-size:0.95rem; font-weight:700; color:#8B5E3C; text-transform:uppercase; letter-spacing:0.05em; margin-bottom:0.6rem;">Extracurriculars</div>'
        profile_html += "".join(f'<span class="tag tag-blue">{e}</span>' for e in extras)
        profile_html += f'</div>'
        
    profile_html += f'</div>'
    st.markdown(profile_html, unsafe_allow_html=True)

    # --- Scorecard ---
    st.markdown('<span class="section-label">Scorecard</span>', unsafe_allow_html=True)
    
    scorecard_html = f'<div class="card">'
    
    # Semicircle Donut Gauge for Skill Match
    match_pct = scorecard.get("skill_match_percentage", 50)
    dash_offset = 125.66 * (1 - (match_pct / 100.0))
    donut_color = "#22C55E" if match_pct >= 78 else ("#F59E0B" if match_pct >= 58 else "#EF4444")
    
    scorecard_html += (
        f'<div style="display:flex; justify-content:center; align-items:center; flex-direction:column; margin-bottom:2rem; padding-bottom:1.5rem; border-bottom:1px solid #F0EBE3;">'
        f'  <div style="position:relative; width:220px; height:110px; overflow:hidden;">'
        f'    <svg viewBox="0 0 100 50" style="width:100%; height:100%;">'
        f'      <!-- Background Track -->'
        f'      <path d="M 10 50 A 40 40 0 0 1 90 50" fill="none" stroke="#EDE7D9" stroke-width="11" stroke-linecap="round"/>'
        f'      <!-- Filled Track -->'
        f'      <path d="M 10 50 A 40 40 0 0 1 90 50" fill="none" stroke="{donut_color}" stroke-width="11" stroke-linecap="round"'
        f'            stroke-dasharray="125.66" stroke-dashoffset="{dash_offset}"'
        f'            style="transition: stroke-dashoffset 0.6s ease-out;"/>'
        f'    </svg>'
        f'    <!-- Center Text (Perfectly centered vertically and horizontally inside the container) -->'
        f'    <div style="position:absolute; top:75%; left:50%; transform:translate(-50%, -50%); text-align:center;">'
        f'      <span style="font-family:\'Lora\',serif; font-size:2.4rem; font-weight:700; color:#2C1A0E; line-height:1;">{match_pct}%</span>'
        f'      <div style="font-size:0.95rem; color:#7A6353; font-weight:600; text-transform:uppercase; letter-spacing:0.05em; margin-top:2px;">Skill Match</div>'
        f'    </div>'
        f'  </div>'
        f'</div>'
    )
    
    highlight = scorecard.get("highlight_bullet", "")
    if highlight:
        scorecard_html += f'<div class="highlight-box">⭐ <strong>Your strongest point:</strong> {highlight}</div>'
        
    scores_data = scorecard.get("scores", {})
    for ax in SCORECARD_AXES:
        ax_data = scores_data.get(ax) or next(
            (v for k, v in scores_data.items() if ax.split(" ")[0].lower() in k.lower()), {}
        )
        sc      = int(ax_data.get("score", 50)) if isinstance(ax_data, dict) else 50
        insight = ax_data.get("insight", "")  if isinstance(ax_data, dict) else ""
        colour  = "#22C55E" if sc >= 78 else ("#F59E0B" if sc >= 58 else "#EF4444")
        insight_html = f'<div class="score-insight">{insight}</div>' if insight else ""
        
        scorecard_html += (
            f'<div class="score-wrap">'
            f'  <div class="score-label-row">'
            f'    <span class="score-label-text">{ax}</span>'
            f'    <span class="score-num" style="color:{colour}">{sc}'
            f'      <span style="font-size:0.7rem;color:#9CA3AF">/100</span>'
            f'    </span>'
            f'  </div>'
            f'  <div class="score-bar-bg">'
            f'    <div class="score-bar-fill" style="width:{sc}%; background:linear-gradient(90deg,{colour}88,{colour})"></div>'
            f'  </div>'
            f'  {insight_html}'
            f'</div>'
        )
        
    overall = scorecard.get("overall_assessment", "")
    if overall:
        scorecard_html += f'<div style="border-top: 1px solid #E4DDD3; padding-top:1rem; margin-top:1.25rem; font-size:1.1rem; color:#2C1A0E; line-height:1.6;">'
        scorecard_html += f'  <strong>Overall Assessment:</strong> {overall}'
        scorecard_html += f'</div>'
        
    red_flags = scorecard.get("red_flags", [])
    if red_flags:
        scorecard_html += f'<div style="margin-top:1.25rem;">'
        scorecard_html += f'  <div style="font-size:0.95rem; font-weight:700; color:#8B5E3C; text-transform:uppercase; letter-spacing:0.05em; margin-bottom:0.6rem;">Areas to address:</div>'
        for rf in red_flags:
            scorecard_html += f'<div class="redflag-box">&#9888; {rf}</div>'
        scorecard_html += f'</div>'
        
    # Categorized Skill Gaps
    must_learn = scorecard.get("must_learn_immediately", [])
    may_learn = scorecard.get("may_learn_future", [])
    if must_learn or may_learn:
        scorecard_html += f'<div style="border-top: 1px solid #E4DDD3; margin-top:1.25rem; padding-top:1.25rem;">'
        scorecard_html += f'  <div style="font-size:1.0rem; font-weight:700; color:#8B5E3C; text-transform:uppercase; letter-spacing:0.05em; margin-bottom:0.8rem;">🎯 Skill Gap Analysis</div>'
        
        if must_learn:
            scorecard_html += f'  <div style="margin-bottom:1rem;">'
            scorecard_html += f'    <div style="font-size:1.05rem; font-weight:600; color:#EF4444; margin-bottom:0.5rem;">⚠️ Must Learn Immediately:</div>'
            scorecard_html += "".join(f'<span class="tag" style="background:#FEF2F2; color:#991B1B !important; border:1px solid #FCA5A5; margin-right:6px; margin-bottom:6px; padding:4px 12px; font-size:0.95rem;">🔥 {skill}</span>' for skill in must_learn)
            scorecard_html += f'  </div>'
            
        if may_learn:
            scorecard_html += f'  <div>'
            scorecard_html += f'    <div style="font-size:1.05rem; font-weight:600; color:#4B5563; margin-bottom:0.5rem;">⏳ Future Growth Skills:</div>'
            scorecard_html += "".join(f'<span class="tag" style="background:#F3F4F6; color:#1F2937 !important; border:1px solid #D1D5DB; margin-right:6px; margin-bottom:6px; padding:4px 12px; font-size:0.95rem;">💎 {skill}</span>' for skill in may_learn)
            scorecard_html += f'  </div>'
            
        scorecard_html += f'</div>'
        
    scorecard_html += f'</div>'
    st.markdown(scorecard_html, unsafe_allow_html=True)

    # --- Roadmap Visual Flowchart ---
    st.markdown(f'<span class="section-label">🗺 Your {_timeline} Learning Roadmap</span>', unsafe_allow_html=True)
    
    if isinstance(roadmap, dict) and "phases" in roadmap:
        phases = roadmap.get("phases", [])
        final_project = roadmap.get("final_project", "")
        
        flowchart_html = f'<div class="timeline-container">'
        for phase in phases:
            timeframe = phase.get("timeframe", "")
            title = phase.get("title", "")
            tasks = phase.get("tasks", [])
            
            flowchart_html += f'<div class="timeline-item">'
            flowchart_html += f'  <div class="timeline-marker"></div>'
            flowchart_html += f'  <div class="timeline-content">'
            flowchart_html += f'    <div class="timeline-timeframe">{timeframe}</div>'
            flowchart_html += f'    <div class="timeline-title">{title}</div>'
            for task in tasks:
                flowchart_html += f'    <div class="timeline-task">{task}</div>'
            flowchart_html += f'  </div>'
            flowchart_html += f'</div>'
            
        if final_project:
            flowchart_html += f'<div class="timeline-item">'
            flowchart_html += f'  <div class="timeline-marker" style="background:#22C55E; border-color:#DCFCE7;"></div>'
            flowchart_html += f'  <div class="timeline-content" style="border-left:4px solid #22C55E;">'
            flowchart_html += f'    <div class="timeline-timeframe" style="color:#166534;">Final Capstone</div>'
            flowchart_html += f'    <div class="timeline-title">Project Idea</div>'
            flowchart_html += f'    <div class="timeline-task" style="color:#14532D; font-weight:500;">{final_project}</div>'
            flowchart_html += f'  </div>'
            flowchart_html += f'</div>'
            
        flowchart_html += f'</div>'
        st.markdown(flowchart_html, unsafe_allow_html=True)
    else:
        # Fallback if old markdown roadmap was cached
        roadmap_text = roadmap if isinstance(roadmap, str) else "_No valid roadmap generated._"
        st.markdown(f'<div class="card" style="font-size:1.05rem; line-height:1.6; padding-top:1rem; padding-bottom:1rem;">\n\n{roadmap_text}\n\n</div>', unsafe_allow_html=True)

# ============================= RIGHT PANEL - Career Coach ====================
with col_right:
    st.markdown('<span class="section-label">🤝 Career Coach</span>', unsafe_allow_html=True)
    st.caption(f"Personal advisor for {companies_label}")

    if not st.session_state.coach_init_done:
        role_mention = f"a {role_label} role at " if role_label else ""
        leadership_mention = f"Your **{leadership[0]}** is a standout — exactly what {companies_label} looks for. " if leadership else ""
        greeting = (
            f"Hi {name}! 👋 I've read your full profile. "
            f"{leadership_mention}"
            f"I can help you prep for interviews, walk through case frameworks, or sharpen your story for {role_mention}{companies_label}. "
            f"What would you like to work on?"
        )
        st.session_state.coach_history.append({"role": "assistant", "content": greeting})
        st.session_state.coach_init_done = True

    try:
        chat_box = st.container(height=420)
    except TypeError:
        chat_box = st.container()

    with chat_box:
        for msg in st.session_state.coach_history:
            css_class = "user-bubble" if msg["role"] == "user" else "coach-bubble"
            st.markdown(f'<div class="{css_class}">{msg["content"]}</div>', unsafe_allow_html=True)

    with st.form("coach_form", clear_on_submit=True):
        user_input = st.text_input(
            "coach_input", placeholder="Ask Career Coach anything...", label_visibility="collapsed",
        )
        send_btn = st.form_submit_button("Send →", use_container_width=True)

    if send_btn and user_input.strip():
        st.session_state.coach_history.append({"role": "user", "content": user_input.strip()})
        with st.spinner("Career Coach is thinking..."):
            reply = coach_obj.chat_coach(
                st.session_state.coach_history, user_input.strip(), profile, _companies, _roles
            )
        st.session_state.coach_history.append({"role": "assistant", "content": reply})
        st.rerun()

# ---------------------------------------------------------------------------- #
# Footer
# ---------------------------------------------------------------------------- #
st.divider()
st.markdown(
    '<div style="text-align:center;color:#B8A898;font-size:0.76rem;padding-bottom:0.5rem;">'
    "SkillBridge &middot; Built for placement season &middot; Made with <3 by Abd"
    "</div>",
    unsafe_allow_html=True,
)
