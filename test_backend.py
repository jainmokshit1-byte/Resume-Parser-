"""Backend regression checks. No Streamlit, no pytest.
Run:  python test_backend.py             -> run all checks
      python test_backend.py --fixtures  -> also write fixtures/ (PDFs + JD text) for manual UI tests
Expected values assume the documented defaults (weights 50/50, thresholds 75/50).
If you change the constants in matcher.py, re-baseline the score and label checks."""
import io, math, os, sys
import matcher
from matcher import final_score, tfidf_similarity, compare_skills, skill_match_percent
from nlp_processor import preprocess_text, stem_text
from skill_extractor import extract_skills
from result_generator import analyze_resume, get_screening_result

failures = 0
def check(name, got, expected):
    global failures
    ok = got == expected
    failures += not ok
    print(("PASS  " if ok else "FAIL  ") + name + ("" if ok else f"\n      got      {got!r}\n      expected {expected!r}"))

def make_pdf(text=None):  # minimal valid PDF; text=None gives one blank page
    o = [b"<</Type/Catalog/Pages 2 0 R>>", b"<</Type/Pages/Kids[3 0 R]/Count 1>>"]
    if text is None:
        o.append(b"<</Type/Page/Parent 2 0 R/MediaBox[0 0 612 792]>>")
    else:
        o.append(b"<</Type/Page/Parent 2 0 R/MediaBox[0 0 612 792]/Contents 4 0 R/Resources<</Font<</F1 5 0 R>>>>>>")
        s = b"BT /F1 12 Tf 72 720 Td (" + text.encode() + b") Tj ET"
        o += [b"<</Length %d>>\nstream\n" % len(s) + s + b"\nendstream",
              b"<</Type/Font/Subtype/Type1/BaseFont/Helvetica>>"]
    out, offs = b"%PDF-1.4\n", []
    for i, body in enumerate(o, 1):
        offs.append(len(out)); out += b"%d 0 obj\n" % i + body + b"\nendobj\n"
    xref = len(out)
    out += b"xref\n0 %d\n0000000000 65535 f \n" % (len(o) + 1)
    out += b"".join(b"%010d 00000 n \n" % p for p in offs)
    return out + b"trailer\n<</Size %d/Root 1 0 R>>\nstartxref\n%d\n%%%%EOF" % (len(o) + 1, xref)

def as_file(data, name="resume.pdf"):
    f = io.BytesIO(data); f.name = name; return f

JD = "We are looking for a Python developer with Python, SQL, FastAPI, Machine Learning and Docker experience."
def run(resume, jd=JD):
    m = analyze_resume(as_file(make_pdf(resume)), jd)["matching"]
    return (round(m["tfidf_similarity"], 1), m["skill_match_percentage"], m["final_match_score"],
            m["screening_result"], m["missing_skills"])

# A realistic one-page resume (fake person) and a short JD: the case the old cosine score got wrong.
LONG_RESUME = """Rahul Sharma | rahul@example.com | github.com/rahul
Education: B.Tech Computer Science, XYZ Institute of Technology, 2022-2026, CGPA 8.4
Skills: Python, Java, SQL, MySQL, Git, HTML, CSS, Flask, Machine Learning, Pandas, NumPy
Projects: Student Result Portal - Built a web application using Flask and MySQL for 500+ students to view results.
House Price Prediction - Trained regression models with scikit-learn on 20,000 records; tuned hyperparameters.
Chat Application - Real-time chat app developed with Java sockets and a simple Swing interface.
Experience: Intern, ABC Software (May-July 2025) - Developed backend APIs in Python, wrote SQL queries for reporting,
used Git for version control, fixed bugs reported by the QA team.
Achievements: 2nd place in college hackathon; NPTEL course on Data Structures; volunteer at coding club.
Languages: English, Hindi. Hobbies: cricket, reading, chess."""
LONG_JD = ("We are hiring a Python Developer intern. Required skills: Python, SQL, Flask, Git, Machine Learning, "
           "Docker and AWS. You will develop backend APIs, write SQL queries and build machine learning models.")

if (matcher.TFIDF_WEIGHT, matcher.SKILL_WEIGHT, matcher.STRONG_THRESHOLD, matcher.MODERATE_THRESHOLD) != (50, 50, 75, 50):
    print("NOTE: constants differ from the documented defaults; score/label checks may fail by design.\n")

# --- NLP + skills
check("preprocess sample", preprocess_text("Python developer with experience in SQL, FastAPI and Machine Learning."),
      "python developer sql fastapi machine learning")
check("stemming", stem_text("developer developing develops"), "develop develop develop")
check("S1 variants", extract_skills(preprocess_text("Experienced in Node.js, nodejs, JavaScript, machine-learning and C++. Also Java.")),
      ["Java", "C++", "JavaScript", "Node.js", "Machine Learning"])
check("S2 mysql/github", extract_skills(preprocess_text("Worked with MySQL and GitHub.")), ["MySQL"])
check("S3 javascript only", extract_skills(preprocess_text("JavaScript developer")), ["JavaScript"])
check("S4 new skills", extract_skills(preprocess_text("Used scikit-learn, Power BI and RESTful services.")),
      ["REST API", "scikit-learn", "Power BI"])

# --- scoring (50/50) through the real PDF path
check("T1 sample", run("Python developer with experience in Python, SQL, FastAPI and Machine Learning."),
      (90.6, 80.0, 85, "Strong Match", ["Docker"]))
check("T2 all skills", run("Python developer with experience in Python, SQL, FastAPI, Machine Learning and Docker."),
      (100.0, 100.0, 100, "Strong Match", []))
check("T3 some skills", run("Python developer with experience in Python, SQL and FastAPI."),
      (73.6, 60.0, 67, "Moderate Match", ["Machine Learning", "Docker"]))
check("T4 almost none", run("Java developer with experience in Java and HTML.")[:4], (23.1, 0.0, 12, "Low Match"))

# --- the long-resume fix: extra resume words must not drag the score down
r, j = preprocess_text(LONG_RESUME), preprocess_text(LONG_JD)
sim = tfidf_similarity(r, j)
matched, missing = compare_skills(extract_skills(r), extract_skills(j))
score = final_score(sim, skill_match_percent(matched, extract_skills(j)))
check("T11 long resume", (round(sim, 1), missing, score, get_screening_result(score)),
      (83.4, ["Docker", "AWS"], 77, "Strong Match"))

# --- errors
good = make_pdf("Python developer with SQL.")
check("T5 empty JD", analyze_resume(as_file(good), "   "), {"error": "Please enter a job description."})
check("T6 no resume", analyze_resume(None, JD), {"error": "Please upload a resume."})
check("T7 invalid pdf", analyze_resume(as_file(b"not a pdf", "x.pdf"), JD), {"error": "Unable to extract text from this resume."})
check("T8 blank pdf", analyze_resume(as_file(make_pdf(None)), JD), {"error": "No readable text found in the uploaded resume."})
check("not a .pdf name", analyze_resume(as_file(good, "cv.docx"), JD), {"error": "Please upload a PDF resume."})

# --- rounding, boundaries, edge cases
check("T9 half-up rounding", final_score(80, 77), 79)
check("T9 boundaries", [get_screening_result(s) for s in (75, 74, 50, 49)],
      ["Strong Match", "Moderate Match", "Moderate Match", "Low Match"])
m = analyze_resume(as_file(make_pdf("Hardworking developer and team player with good communication.")),
                   "We need a hardworking team player with good communication.")["matching"]
check("T10 no JD skills -> skill None", m["skill_match_percentage"], None)
check("T10 final == similarity", m["final_match_score"], math.floor(m["tfidf_similarity"] + 0.5))
same = "Python developer with experience in SQL and Docker."
check("identical texts", run(same, same)[2:4], (100, "Strong Match"))
check("unrelated texts", run("Experienced chef cooking pasta and baking bread.")[2:4], (0, "Low Match"))

if "--fixtures" in sys.argv:
    os.makedirs("fixtures", exist_ok=True)
    for name, data in {"sample_resume.pdf": make_pdf("Python developer with experience in Python, SQL, FastAPI and Machine Learning."),
                       "blank.pdf": make_pdf(None), "fake.pdf": b"not a pdf"}.items():
        open(os.path.join("fixtures", name), "wb").write(data)
    open(os.path.join("fixtures", "sample_jd.txt"), "w").write(JD)
    print("\nWrote fixtures/: sample_resume.pdf, blank.pdf, fake.pdf, sample_jd.txt")

print(f"\n{'ALL PASSED' if not failures else str(failures) + ' FAILED'}")
sys.exit(1 if failures else 0)
