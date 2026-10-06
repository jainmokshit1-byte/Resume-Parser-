# NLP-Based Resume Screening and Job Matching System

**Live demo:** https://resume-screening-mj.streamlit.app/

Academic project. Upload a resume PDF, paste a job description, get a 0 to 100 match score, a label, and matched and missing skills.

**Pipeline:** PDF text → clean → tokenize → remove stop words → skill extraction → stemming → TF-IDF + cosine similarity (job's words only) → 50/50 score → label.
No LLM, embeddings, external API, database or login.

## Setup and run

Needs Python 3.10 or newer.

```
git clone https://github.com/jainmokshit1-byte/Resume-Parser-.git
cd Resume-Parser-
python -m venv .venv
```

Activate the virtual environment:
- Windows: `.venv\Scripts\activate`
- Mac/Linux: `source .venv/bin/activate`

Then install and run:

```
pip install -r requirements.txt
streamlit run app.py
```

The app opens in your browser at http://localhost:8501.

First run only: the NLTK word lists (`punkt`, `punkt_tab`, `stopwords`) download automatically, so connect to the internet once. After that it works offline.

## How the score works

`final = floor(0.5 × TF-IDF similarity + 0.5 × skill match + 0.5)` (`TFIDF_WEIGHT`, `SKILL_WEIGHT`, `STRONG_THRESHOLD`, `MODERATE_THRESHOLD` in `matcher.py`).

| Final score | Label |
|---|---|
| 75 or more | Strong Match |
| 50 to 74 | Moderate Match |
| below 50 | Low Match |

If the job names no known skill, the final score is the TF-IDF similarity alone.

Example (one real resume, measured in P7): similarity 75.5, skill 100.0 → 88, Strong Match. Similarity 57.3, skill 71.4 → 64, Moderate Match. Similarity 32.7, no skills in job → 33, Low Match.

## Privacy

Resume and job text are never stored, logged or cached. No temp files, no `st.session_state`, no external calls after setup.

## Limitations

- Thresholds (75/50) were set on a few trial pairs only.
- TF-IDF is fitted on just two documents (resume and job).
- Fixed list of 35 skills; no context ("no Docker experience" still counts) and no synonyms.
- Text-based, English PDFs only.
- A learning prototype, not for hiring decisions.

## Project structure

`app.py` (UI only), `pdf_parser.py`, `nlp_processor.py`, `skill_extractor.py`, `skills.py`, `matcher.py`, `result_generator.py`, `test_backend.py` (dev aid).

Run the backend checks: `python test_backend.py --fixtures`

## More

- Future scope (not built): bigrams, DOCX input, ranking many resumes, keyword highlighting, NER, downloadable report.
- Plain-language guide and build log: [PROJECT_EXPLAINED.md](PROJECT_EXPLAINED.md).
- AI-assisted development: this project was built with Claude Code. The app itself contains no AI.
