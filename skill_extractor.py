import re
from skills import SKILLS

def extract_skills(clean_text):
    found = []
    for skill, variants in SKILLS.items():
        for v in variants:
            if re.search(r"(?<![a-z0-9])" + re.escape(v) + r"(?![a-z0-9])", clean_text):
                found.append(skill)
                break
    return found
