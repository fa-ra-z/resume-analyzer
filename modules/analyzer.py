import google.generativeai as genai
from groq import Groq
import json
import os
from dotenv import load_dotenv

from prompts.templates import (
    RESUME_ANALYSIS_PROMPT,
    JOB_ROLE_PREDICTION_PROMPT,
    INTERVIEW_QUESTIONS_PROMPT,
    ANSWER_FEEDBACK_PROMPT,
    RESUME_OPTIMIZER_PROMPT,
    JOB_TAILORED_RESUME_PROMPT,   # ← NEW
)

load_dotenv()

# ── Configure both APIs ───────────────────────────────────────
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
gemini_model = genai.GenerativeModel("gemini-1.5-flash")
groq_client  = Groq(api_key=os.getenv("GROQ_API_KEY"))

GROQ_MODEL = "llama-3.3-70b-versatile"

# ── Character limits — MUCH higher now to handle multi-page resumes ──
# Gemini 1.5 Flash supports 1M token context (~4M chars)
# Groq Llama 3.3 supports 128k tokens (~500k chars)
# So we can safely allow large resumes.
MAX_RESUME_CHARS_ANALYSIS  = 20000   # was 4000
MAX_RESUME_CHARS_JOBS      = 20000   # was 4000
MAX_RESUME_CHARS_INTERVIEW = 15000   # was 3000
MAX_RESUME_CHARS_OPTIMIZE  = 25000   # was 5000 — CRITICAL for multi-page


# ── JSON parser ───────────────────────────────────────────────
def parse_json(text: str) -> dict:
    """Safely extract and parse JSON from any LLM response."""
    text = text.strip()
    if "```" in text:
        for part in text.split("```"):
            part = part.strip()
            if part.startswith("json"):
                part = part[4:].strip()
            try:
                return json.loads(part)
            except:
                continue
    try:
        return json.loads(text)
    except:
        try:
            start = text.index("{")
            end   = text.rindex("}") + 1
            return json.loads(text[start:end])
        except:
            return {"error": "Could not parse response. Please try again."}


# ── Smart truncation — keeps beginning AND end of resume ─────
def smart_truncate(text: str, max_chars: int) -> str:
    """
    If text is too long, keep the first 70% and last 30% of allowed chars.
    This preserves both contact info (top) AND education/projects (bottom).
    """
    if len(text) <= max_chars:
        return text

    head_size = int(max_chars * 0.70)
    tail_size = max_chars - head_size - 50   # -50 for the separator

    head = text[:head_size]
    tail = text[-tail_size:]

    return head + "\n\n[... middle content trimmed ...]\n\n" + tail


# ── Gemini call ───────────────────────────────────────────────
def call_gemini(prompt: str) -> dict:
    try:
        response = gemini_model.generate_content(
            prompt,
            generation_config={
                "max_output_tokens": 8192,   # ← allow large JSON output
                "temperature": 0.3,
            }
        )
        return parse_json(response.text)
    except Exception as e:
        err = str(e).lower()
        if any(x in err for x in ["429", "quota", "exhausted", "rate", "limit", "resource"]):
            print("Gemini limit hit — switching to Groq...")
            return None
        return {"error": f"Gemini error: {str(e)}"}


# ── Groq call ─────────────────────────────────────────────────
def call_groq(prompt: str) -> dict:
    try:
        response = groq_client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert AI assistant. Always respond with valid JSON only. No extra text, no markdown, no explanation."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.3,
            max_tokens=8000,   # ← bigger output for multi-page resumes
        )
        return parse_json(response.choices[0].message.content)
    except Exception as e:
        return {"error": f"Groq error: {str(e)}"}


# ── Main caller with automatic fallback ──────────────────────
def call_ai(prompt: str) -> dict:
    result = call_gemini(prompt)
    if result is None:
        return call_groq(prompt)
    if "error" in result:
        print(f"Gemini failed ({result['error']}) — trying Groq...")
        return call_groq(prompt)
    return result


# ── Public functions ──────────────────────────────────────────
def analyze_resume(resume_text: str, job_role: str = "General") -> dict:
    prompt = RESUME_ANALYSIS_PROMPT.format(
        resume_text=smart_truncate(resume_text, MAX_RESUME_CHARS_ANALYSIS),
        job_role=job_role
    )
    return call_ai(prompt)


def predict_job_roles(resume_text: str) -> dict:
    prompt = JOB_ROLE_PREDICTION_PROMPT.format(
        resume_text=smart_truncate(resume_text, MAX_RESUME_CHARS_JOBS)
    )
    return call_ai(prompt)


def generate_interview_questions(resume_text: str, job_role: str) -> dict:
    prompt = INTERVIEW_QUESTIONS_PROMPT.format(
        resume_text=smart_truncate(resume_text, MAX_RESUME_CHARS_INTERVIEW),
        job_role=job_role
    )
    return call_ai(prompt)


def evaluate_answer(question: str, answer: str) -> dict:
    prompt = ANSWER_FEEDBACK_PROMPT.format(
        question=question,
        answer=answer
    )
    return call_ai(prompt)


def optimize_resume(resume_text: str, job_role: str, missing_keywords: list) -> dict:
    prompt = RESUME_OPTIMIZER_PROMPT.format(
        resume_text=smart_truncate(resume_text, MAX_RESUME_CHARS_OPTIMIZE),
        job_role=job_role,
        missing_keywords=", ".join(missing_keywords[:15])
    )
    return call_ai(prompt)
    
def tailor_resume_to_job(resume_text: str, job_description: str) -> dict:
    """
    Generates a perfectly tailored resume by analyzing both the
    candidate's master resume and the target job description.
    """
    prompt = JOB_TAILORED_RESUME_PROMPT.format(
        resume_text=smart_truncate(resume_text, MAX_RESUME_CHARS_OPTIMIZE),
        job_description=job_description[:8000]
    )
    return call_ai(prompt)