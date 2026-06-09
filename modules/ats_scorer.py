# This file scores resumes by checking for important keywords
# It works WITHOUT any API - just pattern matching

# Keywords that ATS systems look for, grouped by job role
POWER_KEYWORDS = {
    "data science": [
        "python", "machine learning", "pandas", "sql", "tensorflow",
        "numpy", "scikit-learn", "data analysis", "deep learning", "nlp",
        "matplotlib", "jupyter", "statistics", "neural network"
    ],
    "data analyst": [
        "sql", "excel", "python", "tableau", "power bi", "data visualization",
        "pandas", "statistics", "reporting", "dashboard", "pivot"
    ],
    "software engineer": [
        "java", "python", "javascript", "git", "api", "rest",
        "agile", "docker", "sql", "system design", "algorithms"
    ],
    "general": [
        "leadership", "communication", "teamwork", "problem solving",
        "project management", "analytical", "results", "initiative"
    ]
}


def calculate_rule_based_ats(text: str, role: str = "general") -> dict:
    """
    Checks how many important keywords are in the resume.
    Returns a score and lists of found/missing keywords.
    """
    text_lower = text.lower()  # Make everything lowercase for comparison
    
    # Get keywords for the specific role (default to general if not found)
    role_lower = role.lower()
    
    # Find the closest matching role category
    matched_role = "general"
    for key in POWER_KEYWORDS:
        if key in role_lower or role_lower in key:
            matched_role = key
            break
    
    role_keywords = POWER_KEYWORDS[matched_role]
    general_keywords = POWER_KEYWORDS["general"]
    all_keywords = list(set(role_keywords + general_keywords))
    
    # Check which keywords are present
    found_keywords = [kw for kw in all_keywords if kw in text_lower]
    missing_keywords = [kw for kw in role_keywords if kw not in text_lower]
    
    # --- Calculate Score (out of 100) ---
    
    # 1. Keyword match score (40 points max)
    if len(all_keywords) > 0:
        keyword_score = (len(found_keywords) / len(all_keywords)) * 40
    else:
        keyword_score = 0
    
    # 2. Resume length score (20 points max)
    word_count = len(text.split())
    if 300 <= word_count <= 800:
        length_score = 20   # Perfect length
    elif word_count < 200:
        length_score = 5    # Too short
    elif word_count < 300:
        length_score = 12   # A bit short
    else:
        length_score = 14   # Too long (800+ words)
    
    # 3. Contact info (10 points each)
    has_email = 10 if "@" in text else 0
    
    # Check for phone number (10 digits in a row, roughly)
    import re
    has_phone = 10 if re.search(r'\d{10}', text.replace(" ", "").replace("-", "")) else 0
    
    # 4. Professional links (10 points each)
    has_github = 10 if "github" in text_lower else 0
    has_linkedin = 10 if "linkedin" in text_lower else 0
    
    # Add everything up
    total_score = keyword_score + length_score + has_email + has_phone + has_github + has_linkedin
    total_score = round(min(total_score, 100))  # Cap at 100
    
    return {
        "rule_based_score": total_score,
        "found_keywords": found_keywords,
        "missing_keywords": missing_keywords[:8],  # Show top 8 missing
        "word_count": word_count,
        "has_email": bool(has_email),
        "has_phone": bool(has_phone),
        "has_github": bool(has_github),
        "has_linkedin": bool(has_linkedin)
    }