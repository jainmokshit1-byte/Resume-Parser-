import re
import nltk
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from nltk.tokenize import word_tokenize

def _ensure_nltk_data():
    for pkg, path in [("punkt", "tokenizers/punkt"),
                      ("punkt_tab", "tokenizers/punkt_tab"),
                      ("stopwords", "corpora/stopwords")]:
        try:
            nltk.data.find(path)
        except LookupError:
            nltk.download(pkg, quiet=True)

_ensure_nltk_data()

# Words found in almost every job post or resume that say nothing about fit.
DOMAIN_STOP_WORDS = {
    "experience", "experienced", "skill", "skills", "required", "requirement", "requirements",
    "looking", "hiring", "candidate", "candidates", "job", "role", "responsibilities",
    "responsibility", "ability", "knowledge", "plus", "preferred", "must", "year", "years",
    "strong", "good", "excellent", "etc", "need", "needed", "work", "working", "using",
    "will", "also", "like",
}
STOP_WORDS = set(stopwords.words("english")) | DOMAIN_STOP_WORDS
_stemmer = PorterStemmer()

def clean_text(text):
    text = text.lower()
    text = re.sub(r"[-_/]", " ", text)
    text = re.sub(r"[^a-z0-9+#.\s]", " ", text)
    return re.sub(r"\s+", " ", text).strip()

def tokenize(text):
    tokens = [t.strip(".") for t in word_tokenize(text)]
    return [t for t in tokens if t and any(c.isalnum() for c in t)]

def remove_stopwords(tokens):
    return [t for t in tokens if t not in STOP_WORDS]

def preprocess_text(text):
    return " ".join(remove_stopwords(tokenize(clean_text(text))))

def stem_text(clean):
    return " ".join(_stemmer.stem(t) for t in clean.split())
