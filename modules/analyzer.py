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
    RESUME_OPTIMIZER_PROMPT
)

load_dotenv()

# ── Configure both APIs ───────────────────────────────────────
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
gemini_model = genai.GenerativeModel("gemini-1.5-flash")
groq_client  = Groq(api_key=os.getenv("GROQ_API_KEY"))

GROQ_MODEL = "llama-3.3-70b-versatile"  # Best free Groq model


# ── JSON parser (same for both APIs) ─────────────────────────
def parse_json(text: str) -> dict:
    """Safely extract and parse JSON from any LLM response."""
    text = text.strip()
    # Strip markdown code fences if present
    if "```" in text:
        for part in text.split("```"):
            part = part.strip()
            if part.startswith("json"):
                part = part[4:].strip()
            try:
                return json.loads(part)
            except:
                continue
    # Try direct parse
    try:
        return json.loads(text)
    except:
        # Last resort: find { } block
        try:
            start = text.index("{")
            end   = text.rindex("}") + 1
            return json.loads(text[start:end])
        except:
            return {"error": "Could not parse response. Please try again."}


# ── Gemini call ───────────────────────────────────────────────
def call_gemini(prompt: str) -> dict:
    try:
        response = gemini_model.generate_content(prompt)
        return parse_json(response.text)
    except Exception as e:
        err = str(e).lower()
        # Quota / rate limit errors → fallback to Groq
        if any(x in err for x in ["429", "quota", "exhausted", "rate", "limit", "resource"]):
            print("Gemini limit hit — switching to Groq...")
            return None  # Signal to use fallback
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
            max_tokens=4096,
        )
        return parse_json(response.choices[0].message.content)
    except Exception as e:
        return {"error": f"Groq error: {str(e)}"}


# ── Main caller with automatic fallback ──────────────────────
def call_ai(prompt: str) -> dict:
    """
    Tries Gemini first.
    If Gemini hits quota/rate limit → automatically falls back to Groq.
    """
    result = call_gemini(prompt)

    # None means Gemini hit a limit — use Groq
    if result is None:
        return call_groq(prompt)

    # If Gemini returned an error that's NOT quota-related, still try Groq
    if "error" in result:
        print(f"Gemini failed ({result['error']}) — trying Groq...")
        return call_groq(prompt)

    return result


# ── Public functions (all use call_ai now) ────────────────────
def analyze_resume(resume_text: str, job_role: str = "General") -> dict:
    prompt = RESUME_ANALYSIS_PROMPT.format(
        resume_text=resume_text[:4000],
        job_role=job_role
    )
    return call_ai(prompt)


def predict_job_roles(resume_text: str) -> dict:
    prompt = JOB_ROLE_PREDICTION_PROMPT.format(
        resume_text=resume_text[:4000]
    )
    return call_ai(prompt)


def generate_interview_questions(resume_text: str, job_role: str) -> dict:
    prompt = INTERVIEW_QUESTIONS_PROMPT.format(
        resume_text=resume_text[:3000],
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
        resume_text=resume_text[:5000],
        job_role=job_role,
        missing_keywords=", ".join(missing_keywords[:15])
    )
    return call_ai(prompt)