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
    layout="wide"
)

# ─────────────────────────────────────────────
# CUSTOM STYLING
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    background-color: #0a0a0f;
}

[data-testid="stSidebar"] {
    background: #0f0f18 !important;
    border-right: 1px solid #1e1e30 !important;
}
[data-testid="stSidebar"] * { color: #94a3b8; }
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 { color: #e2e8f0; }
[data-testid="stSidebarContent"] { padding: 1.5rem 1rem; }

.main .block-container {
    background: #0a0a0f;
    padding: 2rem 2.5rem;
    max-width: 1100px;
}

.score-card {
    background: #0f0f18;
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
    height: 2px;
    background: linear-gradient(90deg, #6366f1, #a78bfa);
}
.score-num {
    font-size: 2.4rem;
    font-weight: 700;
    color: #e2e8f0;
    line-height: 1.1;
    margin: 8px 0 4px;
}
.score-label {
    font-size: 0.75rem;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: #4b5563;
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
    background: #1e1e30;
}
.section-hdr-text {
    font-size: 0.78rem;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: #6366f1;
    font-weight: 600;
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
    background: #0a0a0f;
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
    background: #1e1b4b;
    color: #a78bfa;
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
    color: #6b7280;
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
.diff-easy   { color: #4ade80; font-size: 0.72rem; font-weight: 600; }
.diff-medium { color: #fbbf24; font-size: 0.72rem; font-weight: 600; }
.diff-hard   { color: #f87171; font-size: 0.72rem; font-weight: 600; }

.feedback-box {
    background: #0c1526;
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
    background: #0f0f18;
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
    color: #a78bfa;
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

[data-testid="stFileUploader"] {
    border: 1px dashed #312e81 !important;
    border-radius: 12px !important;
    background: #0a0a14 !important;
}

.stButton > button {
    background: linear-gradient(135deg, #4f46e5, #7c3aed) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 10px 22px !important;
    font-weight: 600 !important;
    font-size: 0.85rem !important;
    letter-spacing: 0.02em !important;
    transition: opacity 0.2s !important;
}
.stButton > button:hover { opacity: 0.88 !important; }

.stTextInput > div > div > input {
    background: #0f0f18 !important;
    border: 1px solid #1e1e30 !important;
    border-radius: 8px !important;
    color: #e2e8f0 !important;
    font-size: 0.85rem !important;
}
.stTextInput > div > div > input:focus {
    border-color: #6366f1 !important;
    box-shadow: 0 0 0 3px rgba(99,102,241,0.15) !important;
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
    background: #1e1b4b !important;
    color: #a78bfa !important;
    font-weight: 600 !important;
}

[data-testid="stMetricValue"] {
    color: #a78bfa !important;
    font-size: 1.6rem !important;
    font-weight: 700 !important;
}
[data-testid="stMetricLabel"] {
    color: #4b5563 !important;
    font-size: 0.75rem !important;
    text-transform: uppercase !important;
    letter-spacing: 0.08em !important;
}

::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: #0a0a0f; }
::-webkit-scrollbar-thumb { background: #1e1e30; border-radius: 4px; }
::-webkit-scrollbar-thumb:hover { background: #6366f1; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────
if "resume_text" not in st.session_state:
    st.session_state.resume_text = ""
if "analysis" not in st.session_state:
    st.session_state.analysis = None
if "ats_local" not in st.session_state:
    st.session_state.ats_local = None
if "job_roles" not in st.session_state:
    st.session_state.job_roles = None
if "questions" not in st.session_state:
    st.session_state.questions = None

# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🎯 ResumeIQ")
    st.markdown("*AI-powered resume analysis & interview prep*")
    st.divider()

    page = st.radio("📌 Go to", [
        "📄 Resume Analysis",
        "💼 Job Role Prediction",
        "🎤 Interview Practice",
        "✨ ATS Resume Builder"
    ])

    st.divider()

    target_role = st.text_input(
        "🎯 Target Job Role",
        placeholder="e.g. Data Analyst, SDE"
    )

    uploaded_file = st.file_uploader("📎 Upload Resume (PDF only)", type=["pdf"])

    if uploaded_file is not None:
        if st.session_state.resume_text == "":
            with st.spinner("Reading PDF..."):
                st.session_state.resume_text = extract_text_from_pdf(uploaded_file)
            st.success("✅ Resume loaded!")
        else:
            st.success("✅ Resume ready!")

    st.divider()
    st.caption("Built by S.F.A.")


# ═══════════════════════════════════════════════════════
# PAGE 1 — RESUME ANALYSIS
# ═══════════════════════════════════════════════════════
if page == "📄 Resume Analysis":

    st.title("📄 Resume Analysis")
    st.markdown("Upload your resume and get an instant AI-powered ATS analysis.")

    if not uploaded_file:
        st.info("👈 Please upload your resume PDF from the sidebar to begin.")
        st.stop()

    if st.button("🔍 Analyze My Resume", type="primary"):
        with st.spinner("🤖 Gemini AI is reading your resume... this takes ~10 seconds"):
            st.session_state.analysis = analyze_resume(
                st.session_state.resume_text,
                target_role if target_role else "General"
            )
            st.session_state.ats_local = calculate_rule_based_ats(
                st.session_state.resume_text,
                target_role if target_role else "general"
            )

    if st.session_state.analysis:
        data = st.session_state.analysis
        local = st.session_state.ats_local

        if "error" in data:
            st.error(f"❌ Error: {data['error']}")
            st.stop()

        # ── Score Cards ──
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

        # ── Strengths & Weaknesses ──
        col_a, col_b = st.columns(2)

        with col_a:
            st.markdown('<div class="section-hdr"><div class="section-hdr-text">✦ Strengths</div><div class="section-hdr-line"></div></div>', unsafe_allow_html=True)
            for item in data.get("strengths", []):
                st.markdown(f'<span class="tag tag-green">✓ {item}</span>', unsafe_allow_html=True)

        with col_b:
            st.markdown('<div class="section-hdr"><div class="section-hdr-text">✦ Weaknesses</div><div class="section-hdr-line"></div></div>', unsafe_allow_html=True)
            for item in data.get("weaknesses", []):
                st.markdown(f'<span class="tag tag-red">✗ {item}</span>', unsafe_allow_html=True)

        # ── Missing Skills ──
        st.markdown('<div class="section-hdr"><div class="section-hdr-text">✦ Skills to Add</div><div class="section-hdr-line"></div></div>', unsafe_allow_html=True)
        st.caption("These keywords are missing — adding them increases your ATS score.")

        all_missing = list(set(
            data.get("missing_skills", []) +
            local.get("missing_keywords", [])
        ))
        for skill in all_missing:
            st.markdown(f'<span class="tag tag-purple">+ {skill}</span>', unsafe_allow_html=True)

        # ── Formatting Issues ──
        if data.get("formatting_issues"):
            st.markdown('<div class="section-hdr"><div class="section-hdr-text">✦ Formatting Issues</div><div class="section-hdr-line"></div></div>', unsafe_allow_html=True)
            for issue in data.get("formatting_issues", []):
                st.warning(f"⚠️ {issue}")

        # ── Improvement Suggestions ──
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

        # ── Resume Checklist ──
        st.markdown('<div class="section-hdr"><div class="section-hdr-text">✦ Resume Checklist</div><div class="section-hdr-line"></div></div>', unsafe_allow_html=True)
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Email",    "✅" if local.get("has_email")    else "❌")
        c2.metric("Phone",    "✅" if local.get("has_phone")    else "❌")
        c3.metric("GitHub",   "✅" if local.get("has_github")   else "❌")
        c4.metric("LinkedIn", "✅" if local.get("has_linkedin") else "❌")

        # ── AI Summary ──
        st.markdown('<div class="section-hdr"><div class="section-hdr-text">✦ AI Summary</div><div class="section-hdr-line"></div></div>', unsafe_allow_html=True)
        st.info(data.get("summary", "No summary available."))


# ═══════════════════════════════════════════════════════
# PAGE 2 — JOB ROLE PREDICTION
# ═══════════════════════════════════════════════════════
elif page == "💼 Job Role Prediction":

    st.title("💼 Best Job Roles for You")
    st.markdown("AI will match your resume skills to real job market roles.")

    if not uploaded_file:
        st.info("👈 Please upload your resume PDF from the sidebar first.")
        st.stop()

    if st.button("🔮 Find My Best Job Matches", type="primary"):
        with st.spinner("Analyzing your profile against job market..."):
            st.session_state.job_roles = predict_job_roles(
                st.session_state.resume_text
            )

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
                badge = "tag-green" if pct >= 75 else "tag-amber" if pct >= 50 else "tag-red"
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
elif page == "🎤 Interview Practice":

    st.title("🎤 Interview Practice")
    st.markdown("Practice with AI-generated questions from your own resume. Get instant feedback on your answers.")

    if not uploaded_file:
        st.info("👈 Please upload your resume PDF from the sidebar first.")
        st.stop()

    role = target_role if target_role else "Software Engineer"
    st.caption(f"Generating questions for: **{role}**  *(Set target role in sidebar)*")

    if st.button("🎯 Generate My Interview Questions", type="primary"):
        with st.spinner("Crafting personalized questions from your resume..."):
            st.session_state.questions = generate_interview_questions(
                st.session_state.resume_text,
                role
            )

    if st.session_state.questions:
        q_data = st.session_state.questions

        if "error" in q_data:
            st.error(f"❌ {q_data['error']}")
            st.stop()

        tab1, tab2, tab3 = st.tabs(["⚙️ Technical", "🧠 Behavioral", "💬 HR Round"])

        # ── Technical Questions ──
        with tab1:
            st.markdown("Answer these questions and get instant AI feedback on your response.")
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
                        "Your answer:",
                        key=f"tech_ans_{i}",
                        height=130,
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

        # ── Behavioral Questions ──
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
                        "Your answer:",
                        key=f"beh_ans_{i}",
                        height=130,
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

        # ── HR Questions ──
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
elif page == "✨ ATS Resume Builder":

    st.title("✨ ATS Resume Builder")
    st.markdown("AI rewrites your entire resume optimized for your target role — then generates a downloadable PDF.")

    if not uploaded_file:
        st.info("👈 Please upload your resume PDF from the sidebar first.")
        st.stop()

    if not target_role:
        st.warning("⚠️ Please enter a **Target Job Role** in the sidebar before optimizing.")
        st.stop()

    # Show what will happen
    st.markdown('<div class="section-hdr"><div class="section-hdr-text">✦ What AI Will Do</div><div class="section-hdr-line"></div></div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        <div class="sugg-card">
            <div class="sugg-num">1</div>
            <div>
                <div class="sugg-area">Rewrite Content</div>
                <div class="sugg-text">Every bullet rewritten with strong action verbs and quantified results.</div>
            </div>
        </div>""", unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="sugg-card">
            <div class="sugg-num">2</div>
            <div>
                <div class="sugg-area">Inject Keywords</div>
                <div class="sugg-text">Missing ATS keywords for your target role added naturally throughout.</div>
            </div>
        </div>""", unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div class="sugg-card">
            <div class="sugg-num">3</div>
            <div>
                <div class="sugg-area">Generate PDF</div>
                <div class="sugg-text">Clean professional PDF ready to download and submit to recruiters.</div>
            </div>
        </div>""", unsafe_allow_html=True)

    st.markdown("")

    # Get missing keywords from analysis if it exists
    missing_kw = []
    if st.session_state.analysis:
        missing_kw = st.session_state.analysis.get("missing_skills", [])
    if st.session_state.ats_local:
        missing_kw += st.session_state.ats_local.get("missing_keywords", [])
    missing_kw = list(set(missing_kw))

    if missing_kw:
        st.caption(f"📌 Keywords to inject: " + "  ".join([f"`{k}`" for k in missing_kw[:8]]))
    else:
        st.caption("💡 Run Resume Analysis first to detect missing keywords automatically.")

    # Optimize button
    if st.button("🚀 Optimize & Generate PDF", type="primary"):
        with st.spinner("🤖 AI is rewriting your resume... this takes 15–20 seconds"):
            optimized = optimize_resume(
                st.session_state.resume_text,
                target_role,
                missing_kw
            )
            st.session_state.optimized_resume = optimized

    # Show result
    if "optimized_resume" in st.session_state and st.session_state.optimized_resume:
        data = st.session_state.optimized_resume

        if "error" in data:
            st.error(f"❌ Error: {data['error']}")
            st.stop()

        st.success("✅ Resume optimized successfully!")

        # ── Preview the rewritten content ──
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
            skills = data.get("skills", [])
            for skill in skills:
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

        # ── Generate & Download PDF ──
        st.markdown('<div class="section-hdr"><div class="section-hdr-text">✦ Download Your Optimized Resume</div><div class="section-hdr-line"></div></div>', unsafe_allow_html=True)

        with st.spinner("Generating PDF..."):
            pdf_bytes = build_resume_pdf(data)

        fname = f"{data.get('name','Resume').replace(' ','_')}_{target_role.replace(' ','_')}_ATS.pdf"

        st.download_button(
            label="⬇️ Download Optimized Resume PDF",
            data=pdf_bytes,
            file_name=fname,
            mime="application/pdf",
            type="primary",
            use_container_width=True
        )

        st.caption("✅ This PDF is ATS-friendly — clean fonts, no tables in main content, keyword-optimized.")               