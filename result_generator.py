from pdf_parser import extract_text_from_pdf
from nlp_processor import preprocess_text
from skill_extractor import extract_skills
from matcher import (tfidf_similarity, compare_skills, skill_match_percent,
                     final_score, STRONG_THRESHOLD, MODERATE_THRESHOLD)

ERR_NO_RESUME = "Please upload a resume."
ERR_NOT_PDF = "Please upload a PDF resume."
ERR_NO_JD = "Please enter a job description."
ERR_EXTRACT = "Unable to extract text from this resume."
ERR_EMPTY_RESUME = "No readable text found in the uploaded resume."

def get_screening_result(score):
    if score >= STRONG_THRESHOLD:
        return "Strong Match"
    if score >= MODERATE_THRESHOLD:
        return "Moderate Match"
    return "Low Match"

def build_analysis_result(filename, resume_skills, required_skills,
                          matched, missing, similarity, skill_pct, score):
    return {
        "resume": {"filename": filename, "skills": resume_skills},
        "job": {"required_skills": required_skills},
        "matching": {
            "tfidf_similarity": similarity,
            "skill_match_percentage": skill_pct,
            "final_match_score": score,
            "screening_result": get_screening_result(score),
            "matched_skills": matched,
            "missing_skills": missing,
        },
    }

def analyze_resume(resume_file, job_description):
    if resume_file is None:
        return {"error": ERR_NO_RESUME}
    if not job_description or not job_description.strip():
        return {"error": ERR_NO_JD}
    filename = getattr(resume_file, "name", "resume.pdf")
    if not filename.lower().endswith(".pdf"):
        return {"error": ERR_NOT_PDF}
    try:
        resume_text = extract_text_from_pdf(resume_file)
    except ValueError:
        return {"error": ERR_EXTRACT}
    if not resume_text:
        return {"error": ERR_EMPTY_RESUME}

    resume_clean = preprocess_text(resume_text)
    jd_clean = preprocess_text(job_description)
    if not jd_clean:
        return {"error": ERR_NO_JD}
    if not resume_clean:
        return {"error": ERR_EMPTY_RESUME}

    resume_skills = extract_skills(resume_clean)
    required_skills = extract_skills(jd_clean)
    matched, missing = compare_skills(resume_skills, required_skills)
    similarity = tfidf_similarity(resume_clean, jd_clean)
    skill_pct = skill_match_percent(matched, required_skills)
    score = final_score(similarity, skill_pct)
    return build_analysis_result(filename, resume_skills, required_skills,
                                 matched, missing, similarity, skill_pct, score)
