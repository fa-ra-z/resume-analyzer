import streamlit as st
import plotly.graph_objects as go
import plotly.express as px

from modules.pdf_parser import extract_text_from_pdf
from modules.analyzer import (
    analyze_resume,
    predict_job_roles,
    generate_interview_questions,
    evaluate_answer,
    optimize_resume
)
from modules.resume_builder import build_resume_pdf
from modules.ats_scorer import calculate_rule_based_ats

# ─────────────────────────────────────────────
# PAGE CONFIGURATION
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="ResumeIQ — AI Resume Analyzer",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ─────────────────────────────────────────────
# CUSTOM STYLING
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

/* Hide Streamlit default UI elements */
#MainMenu { visibility: hidden !important; }
footer { visibility: hidden !important; }
header { visibility: hidden !important; }
[data-testid="stToolbar"] { visibility: hidden !important; display: none !important; }
[data-testid="stDecoration"] { visibility: hidden !important; display: none !important; }
[data-testid="stStatusWidget"] { visibility: hidden !important; display: none !important; }
.viewerBadge_container__1QSob,
.viewerBadge_link__1S137,
.styles_viewerBadge__1yB5_,
[class*="viewerBadge"] {
    display: none !important;
}
button[kind="header"] { display: none !important; }

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

/* HIDE SIDEBAR COMPLETELY */
[data-testid="stSidebar"] { display: none !important; }
[data-testid="collapsedControl"] { display: none !important; }

/* Background with subtle gradient */
.stApp {
    background:
        radial-gradient(circle at 15% 10%, rgba(99, 102, 241, 0.08) 0%, transparent 40%),
        radial-gradient(circle at 85% 80%, rgba(59, 130, 246, 0.06) 0%, transparent 40%),
        #0a0a14 !important;
}
[data-testid="stAppViewContainer"] { background: transparent !important; }
[data-testid="stHeader"] { background: transparent !important; }

.main .block-container {
    padding: 1.5rem 2rem 3rem;
    max-width: 1200px;
}

/* ───────── TOP NAV BAR ───────── */
.top-nav {
    background: rgba(15, 15, 24, 0.7);
    backdrop-filter: blur(12px);
    border: 1px solid #1e1e30;
    border-radius: 16px;
    padding: 14px 22px;
    margin-bottom: 28px;
    display: flex;
    align-items: center;
    justify-content: space-between;
}
.brand {
    display: flex;
    align-items: center;
    gap: 10px;
    font-size: 1.25rem;
    font-weight: 700;
    background: linear-gradient(135deg, #818cf8, #38bdf8);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}
.brand-icon {
    width: 32px; height: 32px;
    background: linear-gradient(135deg, #6366f1, #3b82f6);
    border-radius: 8px;
    display: flex; align-items: center; justify-content: center;
    font-size: 1rem;
}

/* Style Streamlit's radio as pill nav */
div[role="radiogroup"] {
    flex-direction: row !important;
    gap: 6px !important;
    background: #0a0a14;
    padding: 5px;
    border-radius: 12px;
    border: 1px solid #1e1e30;
}
div[role="radiogroup"] label {
    background: transparent !important;
    border-radius: 9px !important;
    padding: 8px 16px !important;
    cursor: pointer !important;
    transition: all 0.2s !important;
    margin: 0 !important;
    border: 1px solid transparent !important;
}
div[role="radiogroup"] label:hover {
    background: #14142a !important;
}
div[role="radiogroup"] label[data-checked="true"] {
    background: linear-gradient(135deg, #4f46e5, #3b82f6) !important;
    border: 1px solid #6366f1 !important;
    box-shadow: 0 4px 14px rgba(99, 102, 241, 0.35) !important;
}
div[role="radiogroup"] label > div:first-child { display: none !important; }
div[role="radiogroup"] label p {
    font-size: 0.82rem !important;
    font-weight: 500 !important;
    color: #94a3b8 !important;
    margin: 0 !important;
}
div[role="radiogroup"] label[data-checked="true"] p {
    color: white !important;
    font-weight: 600 !important;
}

/* ───────── PAGE TITLE ───────── */
.page-hero {
    text-align: center;
    margin: 8px 0 30px;
}
.page-hero h1 {
    font-size: 2.4rem !important;
    font-weight: 800 !important;
    background: linear-gradient(135deg, #ffffff, #94a3b8);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 8px !important;
}
.page-hero p {
    color: #6b7280;
    font-size: 0.95rem;
    margin: 0;
}

/* ───────── 3-STEP PROGRESS ───────── */
.stepper {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0;
    margin: 0 auto 36px;
    max-width: 600px;
}
.step {
    display: flex;
    align-items: center;
    gap: 10px;
}
.step-circle {
    width: 38px; height: 38px;
    border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-weight: 700;
    font-size: 0.9rem;
    border: 2px solid #1e1e30;
    background: #0f0f18;
    color: #4b5563;
    transition: all 0.3s;
}
.step-label {
    font-size: 0.8rem;
    font-weight: 500;
    color: #4b5563;
    white-space: nowrap;
}
.step.active .step-circle {
    background: linear-gradient(135deg, #6366f1, #3b82f6);
    border-color: #6366f1;
    color: white;
    box-shadow: 0 0 0 5px rgba(99, 102, 241, 0.15);
}
.step.active .step-label {
    color: #e2e8f0;
    font-weight: 600;
}
.step.done .step-circle {
    background: #14532d;
    border-color: #16a34a;
    color: #4ade80;
}
.step.done .step-label { color: #6b7280; }
.step-line {
    flex: 1;
    height: 2px;
    background: #1e1e30;
    margin: 0 14px;
    min-width: 50px;
    border-radius: 2px;
}
.step-line.done {
    background: linear-gradient(90deg, #16a34a, #6366f1);
}

/* ───────── WIZARD STEP CARD ───────── */
.wizard-card {
    background: linear-gradient(135deg, rgba(99, 102, 241, 0.04), rgba(59, 130, 246, 0.03));
    border: 1px solid #1e1e30;
    border-radius: 18px;
    padding: 32px;
    margin-bottom: 18px;
    max-width: 720px;
    margin-left: auto;
    margin-right: auto;
}
.wizard-step-label {
    display: inline-block;
    background: linear-gradient(135deg, #312e81, #1e3a8a);
    color: #a5b4fc;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 0.7rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin-bottom: 14px;
}
.wizard-title {
    font-size: 1.5rem;
    font-weight: 700;
    color: #e2e8f0;
    margin-bottom: 6px;
}
.wizard-sub {
    color: #6b7280;
    font-size: 0.88rem;
    margin-bottom: 20px;
}

/* File uploader — large dropzone */
[data-testid="stFileUploader"] {
    background: linear-gradient(135deg, rgba(99, 102, 241, 0.05), rgba(59, 130, 246, 0.03)) !important;
    border: 2px dashed #4338ca !important;
    border-radius: 14px !important;
    padding: 20px !important;
    transition: all 0.3s !important;
}
[data-testid="stFileUploader"]:hover {
    border-color: #6366f1 !important;
    background: linear-gradient(135deg, rgba(99, 102, 241, 0.08), rgba(59, 130, 246, 0.05)) !important;
}
[data-testid="stFileUploader"] section { padding: 1.5rem 1rem !important; }
[data-testid="stFileUploader"] label, [data-testid="stFileUploader"] small {
    color: #cbd5e1 !important;
}
[data-testid="stFileUploaderDropzone"] {
    background: transparent !important;
}

/* PDF preview card */
.pdf-preview {
    background: #0f0f18;
    border: 1px solid #312e81;
    border-radius: 12px;
    padding: 16px 20px;
    margin-top: 16px;
    display: flex;
    align-items: center;
    gap: 14px;
}
.pdf-icon {
    width: 48px; height: 56px;
    background: linear-gradient(135deg, #4f46e5, #3b82f6);
    border-radius: 8px;
    display: flex; align-items: center; justify-content: center;
    color: white;
    font-weight: 700;
    font-size: 0.7rem;
    flex-shrink: 0;
}
.pdf-name {
    color: #e2e8f0;
    font-weight: 600;
    font-size: 0.9rem;
    margin-bottom: 3px;
    word-break: break-all;
}
.pdf-meta {
    color: #6b7280;
    font-size: 0.75rem;
}
.pdf-status {
    color: #4ade80;
    font-size: 0.75rem;
    font-weight: 600;
    margin-left: auto;
    white-space: nowrap;
}

/* Text input */
.stTextInput > div > div > input {
    background: #0f0f18 !important;
    border: 1px solid #1e1e30 !important;
    border-radius: 10px !important;
    color: #e2e8f0 !important;
    font-size: 0.9rem !important;
    padding: 12px 16px !important;
    height: auto !important;
}
.stTextInput > div > div > input:focus {
    border-color: #6366f1 !important;
    box-shadow: 0 0 0 3px rgba(99,102,241,0.18) !important;
}
.stTextInput label {
    color: #cbd5e1 !important;
    font-weight: 500 !important;
    font-size: 0.85rem !important;
}

/* Buttons */
.stButton > button {
    background: linear-gradient(135deg, #4f46e5, #3b82f6) !important;
    color: white !important;
    border: none !important;
    border-radius: 11px !important;
    padding: 12px 28px !important;
    font-weight: 600 !important;
    font-size: 0.9rem !important;
    letter-spacing: 0.02em !important;
    transition: all 0.2s !important;
    box-shadow: 0 4px 14px rgba(99, 102, 241, 0.3) !important;
}
.stButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 20px rgba(99, 102, 241, 0.45) !important;
}
.stButton > button:disabled {
    background: #1e1e30 !important;
    color: #4b5563 !important;
    box-shadow: none !important;
    cursor: not-allowed !important;
}
[data-testid="stDownloadButton"] > button {
    background: linear-gradient(135deg, #059669, #10b981) !important;
    box-shadow: 0 4px 14px rgba(16, 185, 129, 0.3) !important;
}

/* ───────── RESULT CARDS ───────── */
.score-card {
    background: linear-gradient(135deg, #0f0f18, #14142a);
    border: 1px solid #1e1e30;
    border-radius: 14px;
    padding: 20px 22px;
    position: relative;
    overflow: hidden;
}
.score-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    background: linear-gradient(90deg, #6366f1, #3b82f6);
}
.score-num {
    font-size: 2.4rem;
    font-weight: 700;
    background: linear-gradient(135deg, #ffffff, #94a3b8);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    line-height: 1.1;
    margin: 8px 0 4px;
}
.score-label {
    font-size: 0.75rem;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: #6b7280;
    font-weight: 500;
}
.score-icon {
    width: 36px; height: 36px;
    border-radius: 8px;
    display: flex; align-items: center; justify-content: center;
    font-size: 1.1rem;
}

.section-hdr {
    display: flex;
    align-items: center;
    gap: 10px;
    margin: 28px 0 14px;
}
.section-hdr-line {
    flex: 1;
    height: 1px;
    background: linear-gradient(90deg, #1e1e30, transparent);
}
.section-hdr-text {
    font-size: 0.78rem;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    background: linear-gradient(135deg, #818cf8, #38bdf8);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    font-weight: 700;
    white-space: nowrap;
}

.tag {
    display: inline-block;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 500;
    margin: 3px;
}
.tag-green  { background: #052e16; color: #4ade80; border: 1px solid #14532d; }
.tag-red    { background: #1c0a0a; color: #f87171; border: 1px solid #450a0a; }
.tag-purple { background: #1e1b4b; color: #a78bfa; border: 1px solid #312e81; }
.tag-amber  { background: #1c1002; color: #fbbf24; border: 1px solid #451a03; }
.tag-blue   { background: #0c1a3a; color: #93c5fd; border: 1px solid #1e3a5f; }

.sugg-card {
    background: #0f0f18;
    border: 1px solid #1e1e30;
    border-radius: 10px;
    padding: 14px 16px;
    margin-bottom: 8px;
    display: flex;
    gap: 12px;
    align-items: flex-start;
}
.sugg-num {
    width: 22px; height: 22px;
    background: linear-gradient(135deg, #4f46e5, #3b82f6);
    color: white;
    border-radius: 50%;
    font-size: 0.7rem;
    font-weight: 700;
    display: flex; align-items: center; justify-content: center;
    flex-shrink: 0;
    margin-top: 1px;
}
.sugg-area {
    font-size: 0.78rem;
    font-weight: 600;
    color: #a78bfa;
    margin-bottom: 3px;
}
.sugg-text {
    font-size: 0.8rem;
    color: #94a3b8;
    line-height: 1.5;
}

.q-card {
    background: #0f0f18;
    border: 1px solid #1e1e30;
    border-left: 3px solid #6366f1;
    border-radius: 10px;
    padding: 14px 16px;
    margin-bottom: 10px;
}
.q-meta {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 8px;
}
.q-text {
    font-size: 0.85rem;
    color: #cbd5e1;
    line-height: 1.6;
}
.diff-easy   { color: #4ade80; font-size: 0.72rem; font-weight: 700; }
.diff-medium { color: #fbbf24; font-size: 0.72rem; font-weight: 700; }
.diff-hard   { color: #f87171; font-size: 0.72rem; font-weight: 700; }

.feedback-box {
    background: linear-gradient(135deg, #0c1526, #0f1a2e);
    border: 1px solid #1e3a5f;
    border-radius: 12px;
    padding: 18px 20px;
    margin-top: 10px;
}
.fb-score {
    font-size: 1.6rem;
    font-weight: 700;
    margin-bottom: 10px;
}
.fb-row {
    margin-bottom: 8px;
    font-size: 0.82rem;
    line-height: 1.5;
    color: #94a3b8;
}
.fb-row strong { color: #e2e8f0; }

.job-card {
    background: linear-gradient(135deg, #0f0f18, #14142a);
    border: 1px solid #1e1e30;
    border-radius: 14px;
    padding: 18px;
    margin-bottom: 10px;
    display: flex;
    align-items: center;
    justify-content: space-between;
}
.job-pct {
    font-size: 1.6rem;
    font-weight: 700;
    background: linear-gradient(135deg, #818cf8, #38bdf8);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    min-width: 64px;
    text-align: right;
}
.job-name {
    font-size: 0.95rem;
    font-weight: 600;
    color: #e2e8f0;
    margin-bottom: 4px;
}
.job-reason {
    font-size: 0.78rem;
    color: #6b7280;
}

.streamlit-expanderHeader {
    background: #0f0f18 !important;
    border: 1px solid #1e1e30 !important;
    border-radius: 10px !important;
    color: #a78bfa !important;
    font-size: 0.82rem !important;
}

.stTabs [data-baseweb="tab-list"] {
    background: #0f0f18;
    border-radius: 10px;
    padding: 4px;
    gap: 4px;
    border: 1px solid #1e1e30;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    border-radius: 8px !important;
    color: #6b7280 !important;
    font-size: 0.82rem !important;
    padding: 6px 16px !important;
}
.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #4f46e5, #3b82f6) !important;
    color: white !important;
    font-weight: 600 !important;
}

[data-testid="stMetricValue"] {
    background: linear-gradient(135deg, #818cf8, #38bdf8) !important;
    -webkit-background-clip: text !important;
    -webkit-text-fill-color: transparent !important;
    background-clip: text !important;
    font-size: 1.6rem !important;
    font-weight: 700 !important;
}
[data-testid="stMetricLabel"] {
    color: #6b7280 !important;
    font-size: 0.75rem !important;
    text-transform: uppercase !important;
    letter-spacing: 0.08em !important;
}

::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: #0a0a14; }
::-webkit-scrollbar-thumb {
    background: linear-gradient(180deg, #4f46e5, #3b82f6);
    border-radius: 4px;
}

/* All text */
p, span, label, div { color: #cbd5e1; }
h1, h2, h3, h4 { color: #e2e8f0 !important; }

/* Footer credit */
.footer-credit {
    text-align: center;
    color: #4b5563;
    font-size: 0.75rem;
    margin-top: 40px;
    padding-top: 20px;
    border-top: 1px solid #1e1e30;
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────
if "resume_text" not in st.session_state:
    st.session_state.resume_text = ""
if "resume_filename" not in st.session_state:
    st.session_state.resume_filename = ""
if "target_role" not in st.session_state:
    st.session_state.target_role = ""
if "analysis" not in st.session_state:
    st.session_state.analysis = None
if "ats_local" not in st.session_state:
    st.session_state.ats_local = None
if "job_roles" not in st.session_state:
    st.session_state.job_roles = None
if "questions" not in st.session_state:
    st.session_state.questions = None
if "current_page" not in st.session_state:
    st.session_state.current_page = "📄 Analysis"


# ─────────────────────────────────────────────
# TOP NAVIGATION BAR
# ─────────────────────────────────────────────
nav_col1, nav_col2 = st.columns([1, 3])

with nav_col1:
    st.markdown("""
    <div style="display:flex;align-items:center;gap:10px;padding-top:8px">
        <div class="brand-icon">🎯</div>
        <div class="brand">ResumeIQ</div>
    </div>
    """, unsafe_allow_html=True)

with nav_col2:
    page = st.radio(
        "navigation",
        ["📄 Analysis", "💼 Job Roles", "🎤 Interview", "✨ Builder"],
        horizontal=True,
        label_visibility="collapsed",
        key="nav_radio"
    )

st.markdown("<div style='height:1px;background:#1e1e30;margin-bottom:24px'></div>", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────
def render_stepper(steps, current):
    """Render the 3-step progress indicator.
       steps: list of labels  | current: index of active step (0-based)"""
    html = '<div class="stepper">'
    for i, label in enumerate(steps):
        if i < current:
            state = "done"
            icon = "✓"
        elif i == current:
            state = "active"
            icon = str(i + 1)
        else:
            state = ""
            icon = str(i + 1)
        html += f'''
        <div class="step {state}">
            <div class="step-circle">{icon}</div>
            <div class="step-label">{label}</div>
        </div>'''
        if i < len(steps) - 1:
            line_class = "done" if i < current else ""
            html += f'<div class="step-line {line_class}"></div>'
    html += '</div>'
    st.markdown(html, unsafe_allow_html=True)


def render_upload_step():
    """Step 1 — Upload card."""
    st.markdown("""
    <div class="wizard-card">
        <div class="wizard-step-label">Step 1 of 3</div>
        <div class="wizard-title">📎 Upload your resume</div>
        <div class="wizard-sub">Drop your PDF below — we'll extract everything automatically.</div>
    </div>
    """, unsafe_allow_html=True)

    col = st.container()
    with col:
        uploaded = st.file_uploader(
            "Drop PDF here or click to browse",
            type=["pdf"],
            label_visibility="collapsed",
            key="main_uploader"
        )

    if uploaded is not None:
        if (st.session_state.resume_text == ""
                or st.session_state.resume_filename != uploaded.name):
            with st.spinner("Reading PDF..."):
                st.session_state.resume_text = extract_text_from_pdf(uploaded)
                st.session_state.resume_filename = uploaded.name

        size_kb = round(uploaded.size / 1024, 1)
        st.markdown(f"""
        <div class="pdf-preview">
            <div class="pdf-icon">PDF</div>
            <div>
                <div class="pdf-name">{uploaded.name}</div>
                <div class="pdf-meta">{size_kb} KB · Ready for analysis</div>
            </div>
            <div class="pdf-status">✓ Loaded</div>
        </div>
        """, unsafe_allow_html=True)
        return True
    return False


def render_role_step(required=True):
    """Step 2 — Target role input."""
    st.markdown(f"""
    <div class="wizard-card">
        <div class="wizard-step-label">Step 2 of 3</div>
        <div class="wizard-title">🎯 Enter your target role</div>
        <div class="wizard-sub">
            {'Required — helps us tailor keywords and questions for your dream job.'
             if required else 'Optional — adds extra context to the analysis.'}
        </div>
    </div>
    """, unsafe_allow_html=True)

    role = st.text_input(
        "Target Job Role",
        value=st.session_state.target_role,
        placeholder="e.g. Data Analyst, Software Engineer, Product Manager",
        label_visibility="collapsed",
        key="role_input"
    )
    st.session_state.target_role = role
    return role


# ═══════════════════════════════════════════════════════
# PAGE 1 — RESUME ANALYSIS
# ═══════════════════════════════════════════════════════
if page == "📄 Analysis":

    st.markdown("""
    <div class="page-hero">
        <h1>Resume Analysis</h1>
        <p>Get an instant AI-powered ATS score and actionable feedback</p>
    </div>
    """, unsafe_allow_html=True)

    # Determine current step
    has_pdf = st.session_state.resume_text != ""
    has_role = st.session_state.target_role.strip() != ""
    has_analysis = st.session_state.analysis is not None

    if not has_pdf:
        current_step = 0
    elif not has_role:
        current_step = 1
    else:
        current_step = 2

    render_stepper(["Upload Resume", "Target Role", "Analyze"], current_step)

    # ── STEP 1: Upload ──
    if not has_pdf:
        render_upload_step()
        st.stop()

    # Show compact upload status if already done
    st.markdown(f"""
    <div class="pdf-preview" style="max-width:720px;margin:0 auto 18px">
        <div class="pdf-icon">PDF</div>
        <div>
            <div class="pdf-name">{st.session_state.resume_filename}</div>
            <div class="pdf-meta">Resume loaded successfully</div>
        </div>
        <div class="pdf-status">✓ Ready</div>
    </div>
    """, unsafe_allow_html=True)

    # ── STEP 2: Role ──
    role = render_role_step(required=False)
    if not role:
        st.caption("👆 Enter a target role above, or click Analyze to use general analysis.")

    # ── STEP 3: Analyze button ──
    st.markdown("""
    <div class="wizard-card">
        <div class="wizard-step-label">Step 3 of 3</div>
        <div class="wizard-title">🔍 Run AI Analysis</div>
        <div class="wizard-sub">Gemini AI will analyze your resume in ~10 seconds.</div>
    </div>
    """, unsafe_allow_html=True)

    btn_col = st.columns([1, 2, 1])[1]
    with btn_col:
        if st.button("🚀 Analyze My Resume", type="primary", use_container_width=True):
            with st.spinner("🤖 Gemini AI is reading your resume..."):
                st.session_state.analysis = analyze_resume(
                    st.session_state.resume_text,
                    role if role else "General"
                )
                st.session_state.ats_local = calculate_rule_based_ats(
                    st.session_state.resume_text,
                    role if role else "general"
                )
            st.rerun()

    # ── RESULTS ──
    if st.session_state.analysis:
        data = st.session_state.analysis
        local = st.session_state.ats_local

        if "error" in data:
            st.error(f"❌ Error: {data['error']}")
            st.stop()

        st.markdown('<div class="section-hdr"><div class="section-hdr-text">✦ Your Scores</div><div class="section-hdr-line"></div></div>', unsafe_allow_html=True)
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.markdown(f"""
            <div class="score-card">
                <div class="score-icon" style="background:#1e1b4b">🎯</div>
                <div class="score-num">{data.get('ats_score', '?')}</div>
                <div class="score-label">ATS Score</div>
            </div>""", unsafe_allow_html=True)
        with col2:
            st.markdown(f"""
            <div class="score-card">
                <div class="score-icon" style="background:#052e16">🔑</div>
                <div class="score-num">{local.get('rule_based_score', '?')}</div>
                <div class="score-label">Keyword Score</div>
            </div>""", unsafe_allow_html=True)
        with col3:
            st.markdown(f"""
            <div class="score-card">
                <div class="score-icon" style="background:#1c1002">🏅</div>
                <div class="score-num" style="font-size:1.6rem">{data.get('overall_rating', '?')}</div>
                <div class="score-label">Overall Rating</div>
            </div>""", unsafe_allow_html=True)
        with col4:
            st.markdown(f"""
            <div class="score-card">
                <div class="score-icon" style="background:#1c0a0a">👤</div>
                <div class="score-num" style="font-size:1.6rem">{data.get('experience_level', '?')}</div>
                <div class="score-label">Experience Level</div>
            </div>""", unsafe_allow_html=True)

        # ── ATS Gauge ──
        st.markdown('<div class="section-hdr"><div class="section-hdr-text">✦ ATS Compatibility Gauge</div><div class="section-hdr-line"></div></div>', unsafe_allow_html=True)
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=data.get('ats_score', 0),
            gauge={
                'axis': {'range': [0, 100], 'tickcolor': '#94a3b8'},
                'bar': {'color': "#6366f1"},
                'steps': [
                    {'range': [0, 40],   'color': '#3b1a1a'},
                    {'range': [40, 70],  'color': '#3b3a1a'},
                    {'range': [70, 100], 'color': '#1a3b1e'},
                ],
                'threshold': {
                    'value': 70,
                    'line': {'color': '#6ee7b7', 'width': 3}
                }
            },
            title={'text': "Score above 70 is ATS-safe ✅", 'font': {'color': '#94a3b8', 'size': 14}}
        ))
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font={'color': '#e2e8f0'},
            height=260,
            margin=dict(t=40, b=10)
        )
        st.plotly_chart(fig, use_container_width=True)

        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown('<div class="section-hdr"><div class="section-hdr-text">✦ Strengths</div><div class="section-hdr-line"></div></div>', unsafe_allow_html=True)
            for item in data.get("strengths", []):
                st.markdown(f'<span class="tag tag-green">✓ {item}</span>', unsafe_allow_html=True)
        with col_b:
            st.markdown('<div class="section-hdr"><div class="section-hdr-text">✦ Weaknesses</div><div class="section-hdr-line"></div></div>', unsafe_allow_html=True)
            for item in data.get("weaknesses", []):
                st.markdown(f'<span class="tag tag-red">✗ {item}</span>', unsafe_allow_html=True)

        st.markdown('<div class="section-hdr"><div class="section-hdr-text">✦ Skills to Add</div><div class="section-hdr-line"></div></div>', unsafe_allow_html=True)
        st.caption("These keywords are missing — adding them increases your ATS score.")
        all_missing = list(set(
            data.get("missing_skills", []) +
            local.get("missing_keywords", [])
        ))
        for skill in all_missing:
            st.markdown(f'<span class="tag tag-purple">+ {skill}</span>', unsafe_allow_html=True)

        if data.get("formatting_issues"):
            st.markdown('<div class="section-hdr"><div class="section-hdr-text">✦ Formatting Issues</div><div class="section-hdr-line"></div></div>', unsafe_allow_html=True)
            for issue in data.get("formatting_issues", []):
                st.warning(f"⚠️ {issue}")

        st.markdown('<div class="section-hdr"><div class="section-hdr-text">✦ How to Improve</div><div class="section-hdr-line"></div></div>', unsafe_allow_html=True)
        for i, item in enumerate(data.get("improvement_suggestions", [])):
            st.markdown(f"""
            <div class="sugg-card">
                <div class="sugg-num">{i+1}</div>
                <div>
                    <div class="sugg-area">{item.get('area', 'Suggestion')}</div>
                    <div class="sugg-text">{item.get('suggestion', '')}</div>
                </div>
            </div>""", unsafe_allow_html=True)

        st.markdown('<div class="section-hdr"><div class="section-hdr-text">✦ Resume Checklist</div><div class="section-hdr-line"></div></div>', unsafe_allow_html=True)
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Email",    "✅" if local.get("has_email")    else "❌")
        c2.metric("Phone",    "✅" if local.get("has_phone")    else "❌")
        c3.metric("GitHub",   "✅" if local.get("has_github")   else "❌")
        c4.metric("LinkedIn", "✅" if local.get("has_linkedin") else "❌")

        st.markdown('<div class="section-hdr"><div class="section-hdr-text">✦ AI Summary</div><div class="section-hdr-line"></div></div>', unsafe_allow_html=True)
        st.info(data.get("summary", "No summary available."))


# ═══════════════════════════════════════════════════════
# PAGE 2 — JOB ROLE PREDICTION
# ═══════════════════════════════════════════════════════
elif page == "💼 Job Roles":

    st.markdown("""
    <div class="page-hero">
        <h1>Job Role Prediction</h1>
        <p>Discover which roles best match your resume profile</p>
    </div>
    """, unsafe_allow_html=True)

    has_pdf = st.session_state.resume_text != ""
    current_step = 0 if not has_pdf else 1

    render_stepper(["Upload Resume", "Predict Matches"], current_step)

    if not has_pdf:
        render_upload_step()
        st.stop()

    st.markdown(f"""
    <div class="pdf-preview" style="max-width:720px;margin:0 auto 18px">
        <div class="pdf-icon">PDF</div>
        <div>
            <div class="pdf-name">{st.session_state.resume_filename}</div>
            <div class="pdf-meta">Resume loaded successfully</div>
        </div>
        <div class="pdf-status">✓ Ready</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="wizard-card">
        <div class="wizard-step-label">Step 2 of 2</div>
        <div class="wizard-title">🔮 Find Your Best Job Matches</div>
        <div class="wizard-sub">AI matches your skills to real-world job roles.</div>
    </div>
    """, unsafe_allow_html=True)

    btn_col = st.columns([1, 2, 1])[1]
    with btn_col:
        if st.button("🔮 Predict My Best Roles", type="primary", use_container_width=True):
            with st.spinner("Analyzing your profile against the job market..."):
                st.session_state.job_roles = predict_job_roles(
                    st.session_state.resume_text
                )
            st.rerun()

    if st.session_state.job_roles:
        result = st.session_state.job_roles
        if "error" in result:
            st.error(f"❌ {result['error']}")
            st.stop()

        roles = result.get("predicted_roles", [])
        if roles:
            fig = px.bar(
                x=[r["match_percentage"] for r in roles],
                y=[r["role"] for r in roles],
                orientation='h',
                color=[r["match_percentage"] for r in roles],
                color_continuous_scale="Viridis",
                labels={"x": "Match %", "y": ""}
            )
            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font={'color': '#e2e8f0'},
                height=320,
                showlegend=False,
                margin=dict(l=10, r=10, t=20, b=10)
            )
            st.plotly_chart(fig, use_container_width=True)

            st.markdown('<div class="section-hdr"><div class="section-hdr-text">✦ Role Breakdown</div><div class="section-hdr-line"></div></div>', unsafe_allow_html=True)
            for i, role in enumerate(roles):
                pct = role['match_percentage']
                st.markdown(f"""
                <div class="job-card">
                    <div>
                        <div class="job-name">#{i+1} {role['role']}</div>
                        <div class="job-reason">{role['reason']}</div>
                    </div>
                    <div class="job-pct">{pct}%</div>
                </div>""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════
# PAGE 3 — INTERVIEW PRACTICE
# ═══════════════════════════════════════════════════════
elif page == "🎤 Interview":

    st.markdown("""
    <div class="page-hero">
        <h1>Interview Practice</h1>
        <p>Practice with AI-generated questions from your own resume</p>
    </div>
    """, unsafe_allow_html=True)

    has_pdf = st.session_state.resume_text != ""
    has_role = st.session_state.target_role.strip() != ""

    if not has_pdf:
        current_step = 0
    elif not has_role:
        current_step = 1
    else:
        current_step = 2

    render_stepper(["Upload Resume", "Target Role", "Generate Questions"], current_step)

    if not has_pdf:
        render_upload_step()
        st.stop()

    st.markdown(f"""
    <div class="pdf-preview" style="max-width:720px;margin:0 auto 18px">
        <div class="pdf-icon">PDF</div>
        <div>
            <div class="pdf-name">{st.session_state.resume_filename}</div>
            <div class="pdf-meta">Resume loaded successfully</div>
        </div>
        <div class="pdf-status">✓ Ready</div>
    </div>
    """, unsafe_allow_html=True)

    role = render_role_step(required=False)
    final_role = role if role else "Software Engineer"

    st.markdown(f"""
    <div class="wizard-card">
        <div class="wizard-step-label">Step 3 of 3</div>
        <div class="wizard-title">🎯 Generate Interview Questions</div>
        <div class="wizard-sub">For role: <strong style="color:#a78bfa">{final_role}</strong></div>
    </div>
    """, unsafe_allow_html=True)

    btn_col = st.columns([1, 2, 1])[1]
    with btn_col:
        if st.button("🎯 Generate Questions", type="primary", use_container_width=True):
            with st.spinner("Crafting personalized questions from your resume..."):
                st.session_state.questions = generate_interview_questions(
                    st.session_state.resume_text,
                    final_role
                )
            st.rerun()

    if st.session_state.questions:
        q_data = st.session_state.questions
        if "error" in q_data:
            st.error(f"❌ {q_data['error']}")
            st.stop()

        tab1, tab2, tab3 = st.tabs(["⚙️ Technical", "🧠 Behavioral", "💬 HR Round"])

        with tab1:
            st.markdown("Answer these questions and get instant AI feedback.")
            for i, q in enumerate(q_data.get("technical_questions", [])):
                diff = q.get("difficulty", "Medium")
                diff_class = diff.lower()
                st.markdown(f"""
                <div class="q-card">
                    <div class="q-meta">
                        <span class="diff-{diff_class}">{diff.upper()}</span>
                        <span class="tag tag-blue">{q.get('topic', '')}</span>
                    </div>
                    <div class="q-text"><strong>Q{i+1}:</strong> {q.get('question', '')}</div>
                </div>""", unsafe_allow_html=True)

                with st.expander(f"✍️ Type your answer for Q{i+1}"):
                    user_answer = st.text_area(
                        "Your answer:", key=f"tech_ans_{i}", height=130,
                        placeholder="Type your answer here in detail..."
                    )
                    if st.button("📊 Get AI Feedback", key=f"tech_btn_{i}"):
                        if user_answer.strip() == "":
                            st.warning("Please type an answer first.")
                        else:
                            with st.spinner("Evaluating your answer..."):
                                fb = evaluate_answer(q.get("question", ""), user_answer)
                            if "error" not in fb:
                                score = fb.get("score", 0)
                                score_color = "#4ade80" if score >= 7 else "#fbbf24" if score >= 5 else "#f87171"
                                st.markdown(f"""
                                <div class="feedback-box">
                                    <div class="fb-score" style="color:{score_color}">{score}/10</div>
                                    <div class="fb-row"><strong>📝 Feedback:</strong> {fb.get('feedback', '')}</div>
                                    <div class="fb-row"><strong>✅ What was good:</strong> {fb.get('what_was_good', '')}</div>
                                    <div class="fb-row"><strong>📈 Improve this:</strong> {fb.get('what_to_improve', '')}</div>
                                    <div class="fb-row" style="border-top:1px solid #1e3a5f;padding-top:10px;margin-top:4px">
                                        <strong>💡 Model answer:</strong> {fb.get('sample_better_answer', '')}
                                    </div>
                                </div>""", unsafe_allow_html=True)

        with tab2:
            st.markdown("Use the **STAR method**: Situation → Task → Action → Result")
            for i, q in enumerate(q_data.get("behavioral_questions", [])):
                st.markdown(f"""
                <div class="q-card">
                    <div class="q-meta">
                        <span class="tag tag-amber">STAR Method</span>
                    </div>
                    <div class="q-text"><strong>Q{i+1}:</strong> {q.get('question', '')}</div>
                </div>""", unsafe_allow_html=True)

                with st.expander(f"✍️ Answer Q{i+1}"):
                    user_answer = st.text_area(
                        "Your answer:", key=f"beh_ans_{i}", height=130,
                        placeholder="Situation: ...\nTask: ...\nAction: ...\nResult: ..."
                    )
                    if st.button("📊 Get Feedback", key=f"beh_btn_{i}"):
                        if user_answer.strip() == "":
                            st.warning("Please type an answer first.")
                        else:
                            with st.spinner("Evaluating..."):
                                fb = evaluate_answer(q.get("question", ""), user_answer)
                            if "error" not in fb:
                                score = fb.get("score", 0)
                                score_color = "#4ade80" if score >= 7 else "#fbbf24" if score >= 5 else "#f87171"
                                st.markdown(f"""
                                <div class="feedback-box">
                                    <div class="fb-score" style="color:{score_color}">{score}/10</div>
                                    <div class="fb-row"><strong>📝 Feedback:</strong> {fb.get('feedback', '')}</div>
                                    <div class="fb-row"><strong>✅ What was good:</strong> {fb.get('what_was_good', '')}</div>
                                    <div class="fb-row"><strong>📈 Improve this:</strong> {fb.get('what_to_improve', '')}</div>
                                    <div class="fb-row" style="border-top:1px solid #1e3a5f;padding-top:10px;margin-top:4px">
                                        <strong>💡 Model answer:</strong> {fb.get('sample_better_answer', '')}
                                    </div>
                                </div>""", unsafe_allow_html=True)

        with tab3:
            st.markdown("Common HR questions — think through your answers out loud.")
            for i, q in enumerate(q_data.get("hr_questions", [])):
                st.markdown(f"""
                <div class="q-card">
                    <div class="q-meta">
                        <span class="tag tag-purple">HR Round</span>
                    </div>
                    <div class="q-text"><strong>Q{i+1}:</strong> {q}</div>
                </div>""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════
# PAGE 4 — ATS RESUME BUILDER
# ═══════════════════════════════════════════════════════
elif page == "✨ Builder":

    st.markdown("""
    <div class="page-hero">
        <h1>ATS Resume Builder</h1>
        <p>AI injects missing keywords into your resume — downloadable as a clean PDF</p>
    </div>
    """, unsafe_allow_html=True)

    has_pdf = st.session_state.resume_text != ""
    has_role = st.session_state.target_role.strip() != ""

    if not has_pdf:
        current_step = 0
    elif not has_role:
        current_step = 1
    else:
        current_step = 2

    render_stepper(["Upload Resume", "Target Role", "Generate PDF"], current_step)

    if not has_pdf:
        render_upload_step()
        st.stop()

    st.markdown(f"""
    <div class="pdf-preview" style="max-width:720px;margin:0 auto 18px">
        <div class="pdf-icon">PDF</div>
        <div>
            <div class="pdf-name">{st.session_state.resume_filename}</div>
            <div class="pdf-meta">Resume loaded successfully</div>
        </div>
        <div class="pdf-status">✓ Ready</div>
    </div>
    """, unsafe_allow_html=True)

    role = render_role_step(required=True)
    if not role:
        st.warning("⚠️ Target role is required for ATS optimization.")
        st.stop()

    st.markdown("""
    <div class="wizard-card">
        <div class="wizard-step-label">Step 3 of 3</div>
        <div class="wizard-title">🚀 Optimize & Generate PDF</div>
        <div class="wizard-sub">AI will inject missing keywords and produce a downloadable PDF.</div>
    </div>
    """, unsafe_allow_html=True)

    missing_kw = []
    if st.session_state.analysis:
        missing_kw = st.session_state.analysis.get("missing_skills", [])
    if st.session_state.ats_local:
        missing_kw += st.session_state.ats_local.get("missing_keywords", [])
    missing_kw = list(set(missing_kw))

    if missing_kw:
        st.caption("📌 Keywords to inject: " + "  ".join([f"`{k}`" for k in missing_kw[:8]]))
    else:
        st.caption("💡 Run Resume Analysis first to detect missing keywords automatically.")

    btn_col = st.columns([1, 2, 1])[1]
    with btn_col:
        if st.button("🚀 Optimize & Generate PDF", type="primary", use_container_width=True):
            with st.spinner("🤖 AI is rewriting your resume... ~15-20s"):
                optimized = optimize_resume(
                    st.session_state.resume_text,
                    role,
                    missing_kw
                )
                st.session_state.optimized_resume = optimized
            st.rerun()

    if "optimized_resume" in st.session_state and st.session_state.optimized_resume:
        data = st.session_state.optimized_resume
        if "error" in data:
            st.error(f"❌ Error: {data['error']}")
            st.stop()

        st.success("✅ Resume optimized successfully!")

        st.markdown('<div class="section-hdr"><div class="section-hdr-text">✦ Preview — Rewritten Content</div><div class="section-hdr-line"></div></div>', unsafe_allow_html=True)
        tab1, tab2, tab3, tab4 = st.tabs(["📝 Summary", "🛠 Skills", "💼 Experience", "🔨 Projects"])

        with tab1:
            st.markdown(f"""
            <div class="sugg-card" style="display:block">
                <div class="sugg-text" style="font-size:0.9rem;line-height:1.7;color:#e2e8f0">
                    {data.get('summary', '')}
                </div>
            </div>""", unsafe_allow_html=True)

        with tab2:
            for skill in data.get("skills", []):
                st.markdown(f'<span class="tag tag-purple">✓ {skill}</span>', unsafe_allow_html=True)

        with tab3:
            for exp in data.get("experience", []):
                st.markdown(f"""
                <div class="q-card">
                    <div class="q-meta">
                        <span class="tag tag-blue">{exp.get('company','')}</span>
                        <span class="tag tag-amber">{exp.get('duration','')}</span>
                    </div>
                    <div class="q-text" style="font-weight:600;margin-bottom:8px">{exp.get('title','')}</div>
                    {''.join([f'<div class="q-text">• {b}</div>' for b in exp.get('bullets',[])])}
                </div>""", unsafe_allow_html=True)

        with tab4:
            for proj in data.get("projects", []):
                st.markdown(f"""
                <div class="q-card">
                    <div class="q-meta">
                        <span class="tag tag-purple">{proj.get('name','')}</span>
                        <span style="font-size:0.75rem;color:#6b7280">{proj.get('tech','')}</span>
                    </div>
                    {''.join([f'<div class="q-text">• {b}</div>' for b in proj.get('bullets',[])])}
                </div>""", unsafe_allow_html=True)

        st.markdown('<div class="section-hdr"><div class="section-hdr-text">✦ Download Your Optimized Resume</div><div class="section-hdr-line"></div></div>', unsafe_allow_html=True)

        with st.spinner("Generating PDF..."):
            pdf_bytes = build_resume_pdf(data)

        fname = f"{data.get('name','Resume').replace(' ','_')}_{role.replace(' ','_')}_ATS.pdf"

        st.download_button(
            label="⬇️ Download Optimized Resume PDF",
            data=pdf_bytes,
            file_name=fname,
            mime="application/pdf",
            type="primary",
            use_container_width=True
        )

        st.caption("✅ This PDF is ATS-friendly — clean fonts, keyword-optimized, recruiter-ready.")


# ─────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────
st.markdown('<div class="footer-credit">Built by S.F.A. · Powered by Gemini AI</div>', unsafe_allow_html=True)