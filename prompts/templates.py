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
You are an expert ATS resume writer and career coach.

Below is a candidate's raw resume text and their target job role.
Your job is to:
1. Rewrite and improve ALL content (summary, bullets, skills)
2. Add relevant missing keywords for the target role
3. Make every bullet point start with a strong action verb
4. Quantify achievements wherever possible (add realistic estimates if exact numbers are missing)
5. Return structured data so it can be rendered into a PDF

Raw Resume Text:
{resume_text}

Target Job Role: {job_role}
Missing Keywords to Add: {missing_keywords}

Respond ONLY in this exact JSON format with no extra text:
{{
  "name": "<full name from resume>",
  "email": "<email from resume>",
  "phone": "<phone from resume>",
  "linkedin": "<linkedin url if present, else empty string>",
  "github": "<github url if present, else empty string>",
  "location": "<city/location if present, else empty string>",
  "target_role": "{job_role}",
  "summary": "<3-4 sentence powerful professional summary with keywords>",
  "skills": ["<skill1>", "<skill2>", "<skill3>", "<skill4>", "<skill5>", "<skill6>", "<skill7>", "<skill8>", "<skill9>", "<skill10>", "<skill11>", "<skill12>"],
  "experience": [
    {{
      "title": "<job title>",
      "company": "<company name>",
      "duration": "<date range e.g. Jun 2022 – Present>",
      "bullets": [
        "<rewritten bullet with action verb and metric>",
        "<rewritten bullet with action verb and metric>",
        "<rewritten bullet with action verb and metric>"
      ]
    }}
  ],
  "projects": [
    {{
      "name": "<project name>",
      "tech": "<tech stack used>",
      "bullets": [
        "<rewritten bullet>",
        "<rewritten bullet>"
      ]
    }}
  ],
  "education": [
    {{
      "degree": "<degree and field>",
      "institution": "<college/university name>",
      "year": "<graduation year or range>",
      "grade": "<CGPA or percentage if mentioned>"
    }}
  ],
  "certifications": ["<cert1>", "<cert2>"]
}}
"""