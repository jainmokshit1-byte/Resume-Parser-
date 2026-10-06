import math
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from nlp_processor import stem_text

TFIDF_WEIGHT = 50      # percent
SKILL_WEIGHT = 50      # percent
STRONG_THRESHOLD = 75
MODERATE_THRESHOLD = 50

def tfidf_similarity(resume_clean, jd_clean):
    resume_stem, jd_stem = stem_text(resume_clean), stem_text(jd_clean)
    jd_terms = sorted(set(jd_stem.split()))  # only the words the job talks about
    tfidf = TfidfVectorizer(analyzer=str.split, vocabulary=jd_terms).fit_transform([resume_stem, jd_stem])
    return float(cosine_similarity(tfidf[0], tfidf[1])[0][0]) * 100

def compare_skills(resume_skills, jd_skills):
    matched = [s for s in jd_skills if s in resume_skills]
    missing = [s for s in jd_skills if s not in resume_skills]
    return matched, missing

def skill_match_percent(matched, required):
    return 100 * len(matched) / len(required) if required else None

def final_score(similarity_pct, skill_pct):
    if skill_pct is None:
        raw = similarity_pct
    else:
        raw = (TFIDF_WEIGHT * similarity_pct + SKILL_WEIGHT * skill_pct) / 100
    return math.floor(raw + 0.5)
