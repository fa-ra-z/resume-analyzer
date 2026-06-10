import google.generativeai as genai  # Gemini AI library
import json                           # For reading JSON responses
import os                             # For reading our API key
from dotenv import load_dotenv        # For loading the .env file

# Import our prompt templates
from prompts.templates import (
    RESUME_ANALYSIS_PROMPT,
    JOB_ROLE_PREDICTION_PROMPT,
    INTERVIEW_QUESTIONS_PROMPT,
    ANSWER_FEEDBACK_PROMPT,
    RESUME_OPTIMIZER_PROMPT
)

# Load the API key from .env file
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Create the Gemini model object (gemini-2.5-flash is free)
model = genai.GenerativeModel("gemini-2.5-flash")


def call_gemini(prompt: str) -> dict:
    """
    Sends a prompt to Gemini and returns the response as a Python dictionary.
    Handles errors safely.
    """
    try:
        # Send the prompt to Gemini
        response = model.generate_content(prompt)
        
        # Get the text from the response
        text = response.text.strip()
        
        # Sometimes Gemini wraps JSON in ```json ... ``` — remove that
        if "```" in text:
            parts = text.split("```")
            # The JSON is inside the code block
            for part in parts:
                part = part.strip()
                if part.startswith("json"):
                    part = part[4:]  # Remove the word "json"
                try:
                    return json.loads(part.strip())
                except:
                    continue
        
        # Try to parse directly as JSON
        return json.loads(text)
    
    except json.JSONDecodeError:
        return {"error": "AI returned invalid format. Try again."}
    except Exception as e:
        return {"error": str(e)}


def analyze_resume(resume_text: str, job_role: str = "General") -> dict:
    """Analyzes a resume and returns ATS score, strengths, weaknesses, etc."""
    prompt = RESUME_ANALYSIS_PROMPT.format(
        resume_text=resume_text[:4000],  # Limit to 4000 chars to avoid token limits
        job_role=job_role
    )
    return call_gemini(prompt)


def predict_job_roles(resume_text: str) -> dict:
    """Predicts the best matching job roles for this resume."""
    prompt = JOB_ROLE_PREDICTION_PROMPT.format(
        resume_text=resume_text[:4000]
    )
    return call_gemini(prompt)


def generate_interview_questions(resume_text: str, job_role: str) -> dict:
    """Generates personalized interview questions based on resume."""
    prompt = INTERVIEW_QUESTIONS_PROMPT.format(
        resume_text=resume_text[:3000],
        job_role=job_role
    )
    return call_gemini(prompt)


def evaluate_answer(question: str, answer: str) -> dict:
    """Gives AI feedback on a candidate's interview answer."""
    prompt = ANSWER_FEEDBACK_PROMPT.format(
        question=question,
        answer=answer
    )
    return call_gemini(prompt)
    from prompts.templates import RESUME_OPTIMIZER_PROMPT  # add to existing import

def optimize_resume(resume_text: str, job_role: str, missing_keywords: list) -> dict:
    """Rewrites full resume content for ATS and returns structured data."""
    prompt = RESUME_OPTIMIZER_PROMPT.format(
        resume_text=resume_text[:5000],
        job_role=job_role,
        missing_keywords=", ".join(missing_keywords[:15])
    )
    return call_gemini(prompt)