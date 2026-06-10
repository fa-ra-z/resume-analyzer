# These are the instructions we send to Gemini AI
# Think of them as very detailed questions we ask the AI about a resume

RESUME_ANALYSIS_PROMPT = """
You are an expert HR consultant and ATS specialist. Analyze the following resume carefully.

Resume Text:
{resume_text}

Target Job Role: {job_role}

You MUST respond ONLY with valid JSON. No extra text before or after. Use this exact format:
{{
  "ats_score": <a number from 0 to 100>,
  "overall_rating": "<one of: Poor, Average, Good, Excellent>",
  "strengths": ["<strength1>", "<strength2>", "<strength3>"],
  "weaknesses": ["<weakness1>", "<weakness2>", "<weakness3>"],
  "missing_skills": ["<skill1>", "<skill2>", "<skill3>", "<skill4>"],
  "improvement_suggestions": [
    {{"area": "<area name>", "suggestion": "<what to do>"}},
    {{"area": "<area name>", "suggestion": "<what to do>"}},
    {{"area": "<area name>", "suggestion": "<what to do>"}}
  ],
  "formatting_issues": ["<issue1>", "<issue2>"],
  "experience_level": "<one of: Fresher, Junior, Mid, Senior>",
  "summary": "<2-3 sentences describing the resume overall>"
}}
"""

JOB_ROLE_PREDICTION_PROMPT = """
Look at this resume and predict the 5 best matching job roles for this person.

Resume:
{resume_text}

Respond ONLY with valid JSON, no extra text:
{{
  "predicted_roles": [
    {{"role": "<Job Title>", "match_percentage": <number 0-100>, "reason": "<one sentence why>"}},
    {{"role": "<Job Title>", "match_percentage": <number 0-100>, "reason": "<one sentence why>"}},
    {{"role": "<Job Title>", "match_percentage": <number 0-100>, "reason": "<one sentence why>"}},
    {{"role": "<Job Title>", "match_percentage": <number 0-100>, "reason": "<one sentence why>"}},
    {{"role": "<Job Title>", "match_percentage": <number 0-100>, "reason": "<one sentence why>"}}
  ]
}}
"""

INTERVIEW_QUESTIONS_PROMPT = """
Generate interview questions for this candidate based on their resume.

Resume: {resume_text}
Target Role: {job_role}

Respond ONLY with valid JSON, no extra text:
{{
  "technical_questions": [
    {{"question": "<question text>", "difficulty": "<Easy, Medium, or Hard>", "topic": "<topic name>"}},
    {{"question": "<question text>", "difficulty": "<Easy, Medium, or Hard>", "topic": "<topic name>"}},
    {{"question": "<question text>", "difficulty": "<Easy, Medium, or Hard>", "topic": "<topic name>"}},
    {{"question": "<question text>", "difficulty": "<Easy, Medium, or Hard>", "topic": "<topic name>"}},
    {{"question": "<question text>", "difficulty": "<Easy, Medium, or Hard>", "topic": "<topic name>"}}
  ],
  "behavioral_questions": [
    {{"question": "<question text>", "framework": "STAR"}},
    {{"question": "<question text>", "framework": "STAR"}},
    {{"question": "<question text>", "framework": "STAR"}}
  ],
  "hr_questions": [
    "<question1>",
    "<question2>",
    "<question3>"
  ]
}}
"""

ANSWER_FEEDBACK_PROMPT = """
You are an expert interview coach. A candidate answered this interview question.
Evaluate their answer honestly.

Question: {question}
Candidate's Answer: {answer}

Respond ONLY with valid JSON, no extra text:
{{
  "score": <number from 1 to 10>,
  "feedback": "<2-3 sentences of honest feedback>",
  "what_was_good": "<what they did well>",
  "what_to_improve": "<one specific thing to improve>",
  "sample_better_answer": "<a short model answer they can learn from>"
}}
"""
RESUME_OPTIMIZER_PROMPT = """
You are an ATS keyword specialist. Your ONLY job is to inject missing keywords into the resume naturally.

Rules:
- DO NOT rewrite sentences completely
- DO NOT change the structure or format
- DO NOT change any existing content that is already good
- ONLY add missing keywords naturally into existing bullets, skills section, or summary
- Keep the original tone and wording as much as possible
- Just slip the missing keywords in where they fit naturally

Raw Resume Text:
{resume_text}

Target Job Role: {job_role}
Keywords to inject: {missing_keywords}

Respond ONLY in this exact JSON format with no extra text:
{{
  "name": "<full name from resume>",
  "email": "<email from resume>",
  "phone": "<phone from resume>",
  "linkedin": "<linkedin url if present, else empty string>",
  "github": "<github url if present, else empty string>",
  "location": "<city/location if present, else empty string>",
  "target_role": "{job_role}",
  "summary": "<original summary with missing keywords injected naturally, minimal changes>",
  "skills": ["<all original skills plus the missing keywords added>"],
  "experience": [
    {{
      "title": "<exact original job title>",
      "company": "<exact original company name>",
      "duration": "<exact original date range>",
      "bullets": [
        "<original bullet, only add keyword if it fits naturally>",
        "<original bullet, only add keyword if it fits naturally>"
      ]
    }}
  ],
  "projects": [
    {{
      "name": "<exact original project name>",
      "tech": "<original tech stack, add missing keywords here if relevant>",
      "bullets": [
        "<original bullet with keyword injected only if natural>",
        "<original bullet with keyword injected only if natural>"
      ]
    }}
  ],
  "education": [
    {{
      "degree": "<exact original degree>",
      "institution": "<exact original institution>",
      "year": "<exact original year>",
      "grade": "<exact original grade>"
    }}
  ],
  "certifications": ["<original certs unchanged>"]
}}
"""