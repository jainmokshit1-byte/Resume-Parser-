# Project Explained in Plain Words (short version)

**NLP-Based Resume Screening and Job Matching System**

For explaining the project to your ma'am. No coding knowledge needed.

---

## 1. What it does

You upload a resume (PDF) and paste a job description. The app gives:
- a **match score** from 0 to 100,
- a **label**: Strong (75 or more), Moderate (50 to 74), Low (below 50),
- **matched skills** (job needs it, resume has it) and **missing skills** (job needs it, resume lacks it).

**Everyday picture:** a recruiter with a highlighter. She ticks the required skills she finds in the resume, and checks how much of the job ad's wording appears in the resume. The app does the same two checks with arithmetic.

| Check | Question |
|---|---|
| **Skills check** | Of the skills the job needs, what share does the resume have? |
| **Wording check** | How much of the job's wording appears in the resume? |

**Final score = half wording check + half skills check.**

### 60-second version to say out loud

> Ma'am, my project reads a resume PDF and a job description and gives a match score out of 100. It takes the text out of the PDF and cleans it. Then it does two checks. One: it looks for 35 known skills like Python or SQL and counts how many of the job's skills the resume has. Two: it cuts words to their roots and compares the wording of the two texts using TF-IDF and cosine similarity. The final score is half of each, and it says Strong, Moderate or Low. There is no AI model or online service. It is classic NLP on the laptop, so every number can be explained, and the same input always gives the same result.

---

## 2. The steps

| # | Step | In plain words | File |
|---|---|---|---|
| 1 | Read the PDF | Copy the text out of the PDF (pdfplumber). Never saved. | `pdf_parser.py` |
| 2 | Clean | Lowercase, remove odd symbols, so "Python" and "python," match | `nlp_processor.py` |
| 3 | Split into words | Cut text into word cards (**tokens**) | `nlp_processor.py` |
| 4 | Remove filler words | Drop "the", "with", and job-ad filler like "experience" | `nlp_processor.py` |
| 5 | Find skills | Search 35 known skills as whole words ("java" is not found in "javascript") | `skill_extractor.py`, `skills.py` |
| 6 | Cut words to roots | "developer", "developing" → "develop" (**stemming**) | `nlp_processor.py` |
| 7 | Compare wording | **TF-IDF** turns text into numbers (rarer words weigh more); **cosine similarity** measures how closely the two lists of numbers point the same way (1 = same, 0 = nothing in common). Only the job's words are counted, so hobbies and college names on the resume don't hurt. | `matcher.py` |
| 8 | Score and label | 0.5 × wording + 0.5 × skills, rounded the school way (78.5 → 79) | `matcher.py`, `result_generator.py` |

If the job names no known skill, there is no skills check and the score is the wording check alone.

---

## 3. A real example (measured)

One real resume, against three jobs.

| Job | Wording | Skills | Final | Label |
|---|---|---|---|---|
| Strong fit | 75.5% | 100.0% | **88** | Strong Match |
| Partial fit | 57.3% | 71.4% | **64** | Moderate Match |
| Unrelated | 32.7% | none | **33** | Low Match |

Small check: job needs Python, SQL, FastAPI, Machine Learning, Docker; resume has the first four. Skills = 4 ÷ 5 = 80%. Wording = 90.6%. Final = 0.5 × 90.6 + 0.5 × 80 = 85 → Strong Match, Docker missing.

---

## 4. Why no AI or LLM?

The rule was classic NLP only. It works offline, gives the same output every time, and every number can be traced to a simple step. Nothing is trained; TF-IDF just counts words in the two texts in front of it. The resume is never stored, logged or cached.

---

## 5. Limitations

- Matches **keywords, not meaning** ("no experience with Docker" still counts as Docker).
- Only the **35 listed skills**; no synonyms (MySQL does not count as SQL).
- Thresholds 75 and 50 were checked on a few trial pairs only.
- Text-based, English PDFs only.
- No accuracy percentage (no labelled dataset).
- A learning prototype, not for real hiring decisions.

---

## 6. Questions your ma'am may ask

1. **What NLP did you use?** Cleaning, tokenization, stop-word removal, dictionary skill matching, stemming, TF-IDF and cosine similarity.
2. **What is TF-IDF?** Turning text into numbers. A word scores high if it appears often in this text but is not common to every text.
3. **What is cosine similarity?** Comparing two lists of numbers by the angle between them. Same direction means similar text.
4. **Why only the job's words in TF-IDF?** Resumes have many words the job never uses. Counting them made good resumes score low (a realistic resume scored 37 in the old version).
5. **What is stemming?** Cutting words to their root so "developer" and "developing" match.
6. **Why 50/50?** Equal say for both checks. A design choice, kept as two named numbers in `matcher.py`.
7. **How does "java" not match "javascript"?** The skill finder only accepts a word not stuck to other letters or digits.
8. **Why not an LLM?** The rule was classic NLP only; it also keeps the app offline, repeatable and explainable.
9. **How did you check it?** 22 automatic checks in `test_backend.py`, manual screen tests, and trials on three resume-job pairs.
10. **Is the resume stored?** No. No database, no temp file, no logging.
11. **Biggest limitation?** Keywords without context, and only 35 skills.
12. **What next?** Synonyms, two-word phrases, Word input, ranking many resumes, highlighting. Not built.

---

## 7. Glossary

| Word | Plain meaning |
|---|---|
| NLP | Getting computers to work with human text |
| Token | One word card |
| Stop word | Very common word ("the") that is removed |
| Stemming | Cutting a word to its root: developing → develop |
| Regex | A short search pattern, e.g. "this word, not stuck to other letters" |
| TF-IDF | Turning text into numbers that give special words more weight |
| Cosine similarity | How closely two lists of numbers point the same way |
| Threshold | A cut-off, e.g. 75 or more is Strong |
| Constant | A named number kept in one place in the code |

---

## 8. Build log

**Where this differs from anything above, this section is the truth.** Phase close-out: tick the phase here and append one short entry below.

| Phase | Status |
|---|---|
| P0 Setup | done |
| P1 Skills layer | done |
| P2 Text layer | done |
| P3 Matching and result layer | done |
| P4 Backend tests | done |
| P5 UI | done |
| P6 UI test pass | done |
| P7 Calibration | done |
| P8 README | done |
| P9 Demo prep | done (rehearsal and viva drill are yours) |

### Entry template

```
### P_. Phase name
- **What was done, in plain words:**
- **Files created or changed:**
- **What I can say about it to ma'am:**
- **Check result:** real output only, or "not run".
- **Changed from the plan:** or "none".
```

### Short summary of what was built

- **P0:** empty backend files, `requirements.txt` (Streamlit, NLTK, scikit-learn, pdfplumber), `.gitignore`, theme file.
- **P1:** 35-skill list and `extract_skills` (whole-word matching).
- **P2:** PDF reader and text cleaning, tokenizing, stop words, stemming. Sample PDF gave 2625 characters of text.
- **P3:** wording check, skills check, 50/50 final score, labels, five error messages. `final_score(80, 77)` gave 79; sample example gave 85, Strong Match.
- **P4:** `test_backend.py` with 22 checks and `fixtures/`. Result: ALL PASSED.
- **P5:** Streamlit page (`app.py`, UI only): upload, job box, Analyze button, score, label, skills, NLP Processing explanation.
- **P6:** your manual tests found no bugs. Error messages, empty and fake PDFs, and a job with no skills all behaved correctly; the app worked with Wi-Fi off.
- **P7:** kept weights 50/50 and thresholds 75/50. Measured results are in section 3.
- **P8:** `README.md` written (setup, formula, thresholds, privacy, limits).
- **P9:** checked names and numbers against the code (one wrong line fixed), `test_backend.py` ALL PASSED, built `demo_data/` with one resume and three job texts: strong 82 Strong Match, partial 65 Moderate Match, unrelated 44 Low Match. Not done by me: clean-machine run, rehearsal, viva drill.

**Changed from the plan (all phases):** none, except `demo_data/` uses one resume with three job texts instead of three resumes.
