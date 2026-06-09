import streamlit as st
import plotly.graph_objects as go
import plotly.express as px

# Import our own modules
from modules.pdf_parser import extract_text_from_pdf
from modules.analyzer import (
    analyze_resume,
    predict_job_roles,
    generate_interview_questions,
    evaluate_answer
)
from modules.ats_scorer import calculate_rule_based_ats

# ─────────────────────────────────────────────
# PAGE CONFIGURATION (must be the FIRST st command)
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
}

/* Score Cards */
.score-card {
    background: linear-gradient(135deg, #1e1e2e, #2d2d44);
    border: 1px solid #3d3d5c;
    border-radius: 16px;
    padding: 24px;
    text-align: center;
    margin: 8px 0;
}
.score-number {
    font-size: 2.8rem;
    font-weight: 700;
    background: linear-gradient(90deg, #6366f1, #a78bfa);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    line-height: 1.2;
}
.score-label {
    color: #94a3b8;
    font-size: 0.85rem;
    margin-top: 6px;
}

/* Tags */
.tag-green {
    background: #064e3b; color: #6ee7b7;
    padding: 5px 14px; border-radius: 20px;
    font-size: 0.8rem; margin: 3px;
    display: inline-block;
}
.tag-red {
    background: #450a0a; color: #fca5a5;
    padding: 5px 14px; border-radius: 20px;
    font-size: 0.8rem; margin: 3px;
    display: inline-block;
}
.tag-blue {
    background: #1e3a5f; color: #93c5fd;
    padding: 5px 14px; border-radius: 20px;
    font-size: 0.8rem; margin: 3px;
    display: inline-block;
}

/* Section Headers */
.section-title {
    font-size: 1.2rem;
    font-weight: 600;
    color: #e2e8f0;
    border-bottom: 2px solid #6366f1;
    padding-bottom: 8px;
    margin: 28px 0 16px 0;
}

/* Question Cards */
.q-card {
    background: #1e1e2e;
    border-left: 4px solid #6366f1;
    border-radius: 8px;
    padding: 16px;
    margin: 10px 0;
    color: #e2e8f0;
}

/* Feedback Box */
.feedback-box {
    background: #1a2744;
    border: 1px solid #3b82f6;
    border-radius: 12px;
    padding: 20px;
    margin: 12px 0;
    color: #e2e8f0;
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# SESSION STATE SETUP
# (Stores data between button clicks)
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

    # Navigation
    page = st.radio("📌 Go to", [
        "📄 Resume Analysis",
        "💼 Job Role Prediction",
        "🎤 Interview Practice"
    ])

    st.divider()

    # Target job role input
    target_role = st.text_input(
        "🎯 Target Job Role",
        placeholder="e.g. Data Analyst, SDE"
    )

    # PDF Upload
    uploaded_file = st.file_uploader("📎 Upload Resume (PDF only)", type=["pdf"])

    # When a file is uploaded, extract text immediately
    if uploaded_file is not None:
        if st.session_state.resume_text == "":
            with st.spinner("Reading PDF..."):
                st.session_state.resume_text = extract_text_from_pdf(uploaded_file)
            st.success("✅ Resume loaded!")
        else:
            st.success("✅ Resume ready!")

    st.divider()
    st.caption("Built for Tata Technologies InnoVent-27")


# ═══════════════════════════════════════════════════════
# PAGE 1 — RESUME ANALYSIS
# ═══════════════════════════════════════════════════════
if page == "📄 Resume Analysis":

    st.title("📄 Resume Analysis")
    st.markdown("Upload your resume and get an instant AI-powered ATS analysis.")

    # Show message if no file uploaded yet
    if not uploaded_file:
        st.info("👈 Please upload your resume PDF from the sidebar to begin.")
        st.stop()

    # Analyze button
    if st.button("🔍 Analyze My Resume", type="primary", use_container_width=False):
        with st.spinner("🤖 Gemini AI is reading your resume... this takes ~10 seconds"):
            # Call both Gemini and local ATS scorer
            st.session_state.analysis = analyze_resume(
                st.session_state.resume_text,
                target_role if target_role else "General"
            )
            st.session_state.ats_local = calculate_rule_based_ats(
                st.session_state.resume_text,
                target_role if target_role else "general"
            )

    # Show results if analysis exists
    if st.session_state.analysis:
        data = st.session_state.analysis
        local = st.session_state.ats_local

        # Handle API errors
        if "error" in data:
            st.error(f"❌ Error: {data['error']}")
            st.stop()

        # ── Score Cards Row ──
        st.markdown('<div class="section-title">📊 Your Scores</div>', unsafe_allow_html=True)
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.markdown(f"""<div class="score-card">
                <div class="score-number">{data.get('ats_score', '?')}</div>
                <div class="score-label">AI ATS Score</div>
            </div>""", unsafe_allow_html=True)

        with col2:
            st.markdown(f"""<div class="score-card">
                <div class="score-number">{local.get('rule_based_score', '?')}</div>
                <div class="score-label">Keyword Score</div>
            </div>""", unsafe_allow_html=True)

        with col3:
            st.markdown(f"""<div class="score-card">
                <div class="score-number" style="font-size:1.8rem">{data.get('overall_rating', '?')}</div>
                <div class="score-label">Overall Rating</div>
            </div>""", unsafe_allow_html=True)

        with col4:
            st.markdown(f"""<div class="score-card">
                <div class="score-number" style="font-size:1.8rem">{data.get('experience_level', '?')}</div>
                <div class="score-label">Experience Level</div>
            </div>""", unsafe_allow_html=True)

        # ── ATS Gauge Chart ──
        st.markdown('<div class="section-title">🎯 ATS Compatibility Gauge</div>', unsafe_allow_html=True)

        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=data.get('ats_score', 0),
            gauge={
                'axis': {'range': [0, 100], 'tickcolor': '#94a3b8'},
                'bar': {'color': "#6366f1"},
                'steps': [
                    {'range': [0, 40],  'color': '#3b1a1a'},
                    {'range': [40, 70], 'color': '#3b3a1a'},
                    {'range': [70, 100],'color': '#1a3b1e'},
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
            st.markdown('<div class="section-title">✅ Strengths</div>', unsafe_allow_html=True)
            for item in data.get("strengths", []):
                st.markdown(f'<span class="tag-green">✓ {item}</span>', unsafe_allow_html=True)

        with col_b:
            st.markdown('<div class="section-title">⚠️ Weaknesses</div>', unsafe_allow_html=True)
            for item in data.get("weaknesses", []):
                st.markdown(f'<span class="tag-red">✗ {item}</span>', unsafe_allow_html=True)

        # ── Missing Skills ──
        st.markdown('<div class="section-title">🔍 Skills to Add to Your Resume</div>', unsafe_allow_html=True)
        st.caption("These keywords are missing — adding them increases your ATS score.")

        all_missing = list(set(
            data.get("missing_skills", []) +
            local.get("missing_keywords", [])
        ))
        for skill in all_missing:
            st.markdown(f'<span class="tag-blue">+ {skill}</span>', unsafe_allow_html=True)

        # ── Formatting Issues ──
        if data.get("formatting_issues"):
            st.markdown('<div class="section-title">📐 Formatting Issues</div>', unsafe_allow_html=True)
            for issue in data.get("formatting_issues", []):
                st.warning(f"⚠️ {issue}")

        # ── Improvement Suggestions ──
        st.markdown('<div class="section-title">💡 How to Improve</div>', unsafe_allow_html=True)
        for item in data.get("improvement_suggestions", []):
            with st.expander(f"📌 {item.get('area', 'Suggestion')}"):
                st.write(item.get("suggestion", ""))

        # ── Contact Info Check ──
        st.markdown('<div class="section-title">📋 Resume Checklist</div>', unsafe_allow_html=True)
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Email", "✅" if local.get("has_email") else "❌")
        c2.metric("Phone", "✅" if local.get("has_phone") else "❌")
        c3.metric("GitHub", "✅" if local.get("has_github") else "❌")
        c4.metric("LinkedIn", "✅" if local.get("has_linkedin") else "❌")

        # ── AI Summary ──
        st.markdown('<div class="section-title">📝 AI Summary</div>', unsafe_allow_html=True)
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
            # Bar chart of match percentages
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

            # Cards for each role
            for i, role in enumerate(roles):
                pct = role['match_percentage']
                color = "#6ee7b7" if pct >= 75 else "#fbbf24" if pct >= 50 else "#f87171"
                st.markdown(f"""
                <div class="q-card">
                    <strong style="color:#a78bfa; font-size:1.1rem">
                        #{i+1} {role['role']}
                    </strong>
                    <span class="tag-green" style="margin-left:10px">{pct}% match</span>
                    <p style="color:#94a3b8; margin-top:8px; margin-bottom:0">
                        {role['reason']}
                    </p>
                </div>
                """, unsafe_allow_html=True)


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

        # Three tabs: Technical, Behavioral, HR
        tab1, tab2, tab3 = st.tabs(["⚙️ Technical", "🧠 Behavioral", "💬 HR Round"])

        # ── Technical Questions ──
        with tab1:
            st.markdown("Answer these questions and get instant AI feedback on your response.")
            for i, q in enumerate(q_data.get("technical_questions", [])):
                # Difficulty badge color
                diff = q.get("difficulty", "Medium")
                diff_color = {"Easy": "#6ee7b7", "Medium": "#fbbf24", "Hard": "#f87171"}.get(diff, "#94a3b8")

                st.markdown(f"""
                <div class="q-card">
                    <span style="color:{diff_color}; font-size:0.8rem">● {diff}</span>
                    <span class="tag-blue" style="margin-left:8px">{q.get('topic','')}</span>
                    <p style="margin-top:10px; margin-bottom:0">
                        <strong>Q{i+1}:</strong> {q.get('question', '')}
                    </p>
                </div>
                """, unsafe_allow_html=True)

                # Answer box inside expander
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
                                score_color = "#6ee7b7" if score >= 7 else "#fbbf24" if score >= 5 else "#f87171"
                                st.markdown(f"""
                                <div class="feedback-box">
                                    <h4 style="color:{score_color}; margin-top:0">
                                        Score: {score}/10
                                    </h4>
                                    <p><strong>📝 Feedback:</strong> {fb.get('feedback','')}</p>
                                    <p><strong>✅ What was good:</strong> {fb.get('what_was_good','')}</p>
                                    <p><strong>📈 Improve this:</strong> {fb.get('what_to_improve','')}</p>
                                    <p style="border-top:1px solid #3b82f6; padding-top:12px; margin-bottom:0">
                                        <strong>💡 Model answer:</strong> {fb.get('sample_better_answer','')}
                                    </p>
                                </div>
                                """, unsafe_allow_html=True)

        # ── Behavioral Questions ──
        with tab2:
            st.markdown("Use the **STAR method**: Situation → Task → Action → Result")
            for i, q in enumerate(q_data.get("behavioral_questions", [])):
                st.markdown(f"""
                <div class="q-card">
                    <span class="tag-blue">STAR Method</span>
                    <p style="margin-top:10px; margin-bottom:0">
                        <strong>Q{i+1}:</strong> {q.get('question', '')}
                    </p>
                </div>
                """, unsafe_allow_html=True)

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
                                score_color = "#6ee7b7" if score >= 7 else "#fbbf24" if score >= 5 else "#f87171"
                                st.markdown(f"""
                                <div class="feedback-box">
                                    <h4 style="color:{score_color}; margin-top:0">Score: {score}/10</h4>
                                    <p><strong>📝 Feedback:</strong> {fb.get('feedback','')}</p>
                                    <p style="margin-bottom:0"><strong>💡 Better answer:</strong> {fb.get('sample_better_answer','')}</p>
                                </div>
                                """, unsafe_allow_html=True)

        # ── HR Questions ──
        with tab3:
            st.markdown("Common HR questions — think through your answers out loud.")
            for i, q in enumerate(q_data.get("hr_questions", [])):
                st.markdown(f"""
                <div class="q-card">
                    <strong>Q{i+1}:</strong> {q}
                </div>
                """, unsafe_allow_html=True)