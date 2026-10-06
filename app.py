import streamlit as st

from result_generator import analyze_resume

st.set_page_config(page_title="NLP-Based Resume Screening System", layout="centered")

st.title("NLP-Based Resume Screening System")
st.write("Analyze a resume against a job description using Natural Language Processing.")

uploaded_file = st.file_uploader("Upload Resume (PDF)", type=["pdf"])
jd_text = st.text_area(
    "Job Description", height=220, placeholder="Paste the job description here..."
)

if st.button("Analyze Resume", type="primary"):
    missing_input = False
    if uploaded_file is None:
        st.warning("Please upload a resume.")
        missing_input = True
    if not jd_text.strip():
        st.warning("Please enter a job description.")
        missing_input = True
    if missing_input:
        st.stop()

    with st.spinner("Analyzing..."):
        result = analyze_resume(uploaded_file, jd_text)

    if "error" in result:
        if result["error"] in (
            "Unable to extract text from this resume.",
            "No readable text found in the uploaded resume.",
        ):
            st.error(result["error"])
        else:
            st.warning(result["error"])
        st.stop()

    match = result["matching"]
    score = int(match["final_match_score"])
    similarity = match["tfidf_similarity"]
    skill_pct = match["skill_match_percentage"]
    matched = match["matched_skills"]
    missing = match["missing_skills"]
    resume_skills = result["resume"]["skills"]
    required = result["job"]["required_skills"]

    st.divider()
    st.subheader("Screening Result")
    with st.container(border=True):
        st.metric("Match Score", f"{score}%")
        st.progress(max(0, min(100, score)))
        if skill_pct is None:
            st.caption(f"TF-IDF similarity {similarity:.1f}%")
        else:
            st.caption(f"TF-IDF similarity {similarity:.1f}% | Skill match {skill_pct:.1f}%")

    label = match["screening_result"]
    if label == "Strong Match":
        st.success(label)
    elif label == "Moderate Match":
        st.warning(label)
    else:
        st.error(label)

    if skill_pct is None:
        st.info("No known skills were found in the job description.")

    left, right = st.columns(2)
    with left:
        st.markdown(f"**Matched Skills ({len(matched)}/{len(required)})**")
        st.markdown("\n".join(f"✓ {s}  " for s in matched) if matched else "None")
    with right:
        st.markdown(f"**Missing Skills ({len(missing)}/{len(required)})**")
        st.markdown("\n".join(f"✗ {s}  " for s in missing) if missing else "None")
    left, right = st.columns(2)
    with left:
        st.markdown("**Resume Skills**")
        st.write(", ".join(resume_skills) if resume_skills else "None")
    with right:
        st.markdown("**Required Skills**")
        st.write(", ".join(required) if required else "None")

st.divider()
st.subheader("NLP Processing")
st.caption("How the system produced this result.")
st.markdown(
    "Text Extraction -> Text Preprocessing -> Tokenization -> Stop-word Removal "
    "-> Skill Extraction -> Stemming -> TF-IDF -> Cosine Similarity -> Match Score"
)
st.markdown(
    """
| Step | What it does |
|---|---|
| Text Extraction | Reads the text from the PDF resume |
| Text Preprocessing | Converts to lowercase and removes special characters |
| Tokenization | Splits the text into words |
| Stop-word Removal | Removes common words such as "with", "in", "and", plus job-post filler such as "experience" and "required" |
| Skill Extraction | Finds known skills (Python, SQL, ...) in both texts |
| Stemming | Cuts words to their root, so "developer" and "developing" both become "develop" |
| TF-IDF | Turns each text into a vector of weighted words, counting only the words the job description uses |
| Cosine Similarity | Measures how close the two vectors are |
| Match Score | 50% cosine similarity + 50% share of required skills found |
"""
)
