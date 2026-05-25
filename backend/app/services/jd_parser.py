"""
jd_parser.py
------------
Parse a raw job-description string into a structured JobDescription.

Design goals
  • Zero new dependencies — uses only re and the existing skill taxonomy.
  • Deterministic — same input always produces the same output.
  • Graceful degradation — every field has a safe default when the JD is vague.
"""

import re
from typing import List, Optional, Tuple

# ---------------------------------------------------------------------------
# Skill taxonomy (mirrors the canonical names in resume_parser.py)
# Each tuple: (canonical_name, [regex_patterns])
# Patterns are matched case-insensitively against the full JD text.
# ---------------------------------------------------------------------------
_SKILL_PATTERNS: List[Tuple[str, List[str]]] = [
    # Languages
    ("python",          [r"\bpython\b"]),
    ("java",            [r"\bjava\b(?!script)"]),
    ("javascript",      [r"\bjavascript\b", r"\bjs\b"]),
    ("typescript",      [r"\btypescript\b", r"\bts\b"]),
    ("c++",             [r"c\+\+"]),
    ("c#",              [r"c#"]),
    ("golang",          [r"\bgolang\b", r"\bgo\b"]),
    ("rust",            [r"\brust\b"]),
    ("ruby",            [r"\bruby\b"]),
    ("php",             [r"\bphp\b"]),
    ("swift",           [r"\bswift\b"]),
    ("kotlin",          [r"\bkotlin\b"]),
    ("scala",           [r"\bscala\b"]),
    ("r",               [r"\br\b"]),
    ("matlab",          [r"\bmatlab\b"]),
    ("bash",            [r"\bbash\b"]),
    ("powershell",      [r"\bpowershell\b"]),
    # Frameworks / libraries
    ("react",           [r"\breact\.?js\b", r"\breactjs\b", r"\breact\b"]),
    ("angular",         [r"\bangular\b"]),
    ("vue",             [r"\bvue\.?js\b", r"\bvuejs\b", r"\bvue\b"]),
    ("django",          [r"\bdjango\b"]),
    ("flask",           [r"\bflask\b"]),
    ("fastapi",         [r"\bfastapi\b"]),
    ("express",         [r"\bexpress\.?js\b", r"\bexpress\b"]),
    ("spring",          [r"\bspring boot\b", r"\bspring\b"]),
    ("node.js",         [r"\bnode\.?js\b", r"\bnodejs\b"]),
    ("laravel",         [r"\blaravel\b"]),
    (".net",            [r"\.net\b", r"\basp\.net\b"]),
    ("tensorflow",      [r"\btensorflow\b"]),
    ("pytorch",         [r"\bpytorch\b"]),
    ("keras",           [r"\bkeras\b"]),
    ("scikit-learn",    [r"\bscikit-learn\b", r"\bsklearn\b"]),
    ("pandas",          [r"\bpandas\b"]),
    ("numpy",           [r"\bnumpy\b"]),
    ("hugging face",    [r"\bhugging face\b", r"\btransformers\b"]),
    ("next.js",         [r"\bnext\.?js\b", r"\bnextjs\b"]),
    # Databases
    ("sql",             [r"\bsql\b"]),
    ("mysql",           [r"\bmysql\b"]),
    ("postgresql",      [r"\bpostgresql\b", r"\bpostgres\b"]),
    ("mongodb",         [r"\bmongodb\b", r"\bmongo\b"]),
    ("redis",           [r"\bredis\b"]),
    ("cassandra",       [r"\bcassandra\b"]),
    ("dynamodb",        [r"\bdynamodb\b"]),
    ("oracle",          [r"\boracle\b"]),
    ("elasticsearch",   [r"\belasticsearch\b"]),
    ("neo4j",           [r"\bneo4j\b"]),
    ("sqlite",          [r"\bsqlite\b"]),
    # Cloud / DevOps
    ("aws",             [r"\baws\b", r"\bamazon web services\b"]),
    ("azure",           [r"\bazure\b", r"\bmicrosoft azure\b"]),
    ("gcp",             [r"\bgcp\b", r"\bgoogle cloud\b"]),
    ("docker",          [r"\bdocker\b"]),
    ("kubernetes",      [r"\bkubernetes\b", r"\bk8s\b"]),
    ("jenkins",         [r"\bjenkins\b"]),
    ("gitlab ci",       [r"\bgitlab ci\b", r"\bgitlab\b"]),
    ("github actions",  [r"\bgithub actions\b"]),
    ("terraform",       [r"\bterraform\b"]),
    ("ansible",         [r"\bansible\b"]),
    ("ci/cd",           [r"\bci/cd\b", r"\bcicd\b"]),
    # Tools
    ("git",             [r"\bgit\b"]),
    ("jira",            [r"\bjira\b"]),
    ("confluence",      [r"\bconfluence\b"]),
    ("linux",           [r"\blinux\b"]),
    ("unix",            [r"\bunix\b"]),
    # ML / Data
    ("machine learning",    [r"\bmachine learning\b", r"\bml\b"]),
    ("deep learning",       [r"\bdeep learning\b"]),
    ("nlp",                 [r"\bnlp\b", r"\bnatural language processing\b"]),
    ("computer vision",     [r"\bcomputer vision\b"]),
    ("data science",        [r"\bdata science\b"]),
    ("data engineering",    [r"\bdata engineering\b"]),
    ("spark",               [r"\bapache spark\b", r"\bspark\b"]),
    ("hadoop",              [r"\bhadoop\b"]),
    ("tableau",             [r"\btableau\b"]),
    ("power bi",            [r"\bpower bi\b"]),
    # Methodologies
    ("agile",           [r"\bagile\b"]),
    ("scrum",           [r"\bscrum\b"]),
    ("microservices",   [r"\bmicroservices\b"]),
    ("rest api",        [r"\brest(?:ful)?\s*api\b", r"\brest\b"]),
    ("graphql",         [r"\bgraphql\b"]),
    ("devops",          [r"\bdevops\b"]),
]

# Compile once at import time
_COMPILED = [
    (canonical, re.compile("|".join(patterns), re.IGNORECASE))
    for canonical, patterns in _SKILL_PATTERNS
]

# ---------------------------------------------------------------------------
# Signals that distinguish required vs. preferred
# ---------------------------------------------------------------------------
# Lines / sentences containing these phrases → preferred bucket.
_PREFERRED_SIGNALS = re.compile(
    r"\b(nice[- ]to[- ]have|preferred?|bonus|plus|desirable|"
    r"advantage|ideally|ideally|good to have|would be great|"
    r"not required|optional)\b",
    re.IGNORECASE,
)

# Lines that use these phrases → required bucket.
_REQUIRED_SIGNALS = re.compile(
    r"\b(required?|must[- ]have|essential|mandatory|"
    r"strong(ly)? prefer|minimum|at least|you will need|"
    r"we require|you must)\b",
    re.IGNORECASE,
)

# ---------------------------------------------------------------------------
# Experience year extraction
# ---------------------------------------------------------------------------
_EXP_PATTERNS = [
    re.compile(r"(\d+)\+?\s*(?:years?|yrs?)\s+(?:of\s+)?(?:professional\s+)?experience", re.IGNORECASE),
    re.compile(r"experience[:\s]+(\d+)\+?\s*(?:years?|yrs?)", re.IGNORECASE),
    re.compile(r"minimum\s+(?:of\s+)?(\d+)\+?\s*(?:years?|yrs?)", re.IGNORECASE),
    re.compile(r"at\s+least\s+(\d+)\+?\s*(?:years?|yrs?)", re.IGNORECASE),
    re.compile(r"(\d+)\+\s*(?:years?|yrs?)", re.IGNORECASE),  # "3+ years"
]

# ---------------------------------------------------------------------------
# Job title extraction
# ---------------------------------------------------------------------------
_TITLE_PATTERNS = [
    re.compile(r"(?:position|role|job\s+title|title)\s*:?\s*([^\n]{5,80})", re.IGNORECASE),
    re.compile(r"(?:we are|we're|we are currently)\s+(?:looking for|hiring|seeking)\s+(?:a|an)?\s*([^\n]{5,60})", re.IGNORECASE),
    re.compile(r"(?:join us as|come work as|work as)\s+(?:a|an)?\s*([^\n]{5,60})", re.IGNORECASE),
]

# Common job-title keywords used as a last-resort heuristic
_TITLE_KEYWORDS = [
    "engineer", "developer", "scientist", "analyst", "architect",
    "manager", "designer", "lead", "director", "consultant",
    "specialist", "administrator", "devops", "data",
]


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def parse(jd_text: str) -> dict:
    """
    Parse a raw job description string.

    Returns a dict compatible with JobDescription(**result):
      {
          "title": str,
          "description": str,
          "required_skills": List[str],
          "preferred_skills": List[str],
          "experience_years": Optional[int],
      }

    Falls back gracefully when the JD is short or poorly formatted:
    - title defaults to "Open Position"
    - skills are extracted from the full text with no bucket distinction
    - experience_years defaults to None
    """
    if not jd_text or not jd_text.strip():
        return _empty_jd()

    text = jd_text.strip()

    title          = _extract_title(text)
    experience_years = _extract_experience_years(text)
    required, preferred = _split_skills(text)

    # If we couldn't separate buckets, treat everything as required
    if not required and not preferred:
        all_skills = _all_skills_from_text(text)
        required   = all_skills
        preferred  = []

    return {
        "title":            title,
        "description":      text,
        "required_skills":  required,
        "preferred_skills": preferred,
        "experience_years": experience_years,
    }


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _empty_jd() -> dict:
    return {
        "title":             "Open Position",
        "description":       "",
        "required_skills":   [],
        "preferred_skills":  [],
        "experience_years":  None,
    }


def _extract_title(text: str) -> str:
    # Try explicit patterns first
    for pat in _TITLE_PATTERNS:
        m = pat.search(text)
        if m:
            candidate = m.group(1).strip().rstrip(".,:")
            if len(candidate) < 80:
                return candidate.title()

    # Fall back to first non-empty line that contains a title keyword
    for line in text.splitlines():
        line = line.strip()
        if 3 < len(line) < 80:
            lower = line.lower()
            if any(kw in lower for kw in _TITLE_KEYWORDS):
                return line.title()

    # Final fallback: first non-empty line
    for line in text.splitlines():
        line = line.strip()
        if len(line) > 3:
            return line[:80].title()

    return "Open Position"


def _extract_experience_years(text: str) -> Optional[int]:
    candidates: List[int] = []
    for pat in _EXP_PATTERNS:
        for m in pat.finditer(text):
            try:
                val = int(m.group(1))
                if 0 < val <= 30:
                    candidates.append(val)
            except (ValueError, IndexError):
                pass
    return max(candidates) if candidates else None


def _split_skills(text: str) -> Tuple[List[str], List[str]]:
    """
    Split text into sentences/lines then classify each one as required or
    preferred based on signal words. Skills found in preferred-signal lines
    go to the preferred bucket; everything else goes to required.
    """
    # Tokenise into logical chunks (lines or sentences)
    chunks = [c.strip() for c in re.split(r"[\n.;]", text) if c.strip()]

    required:  List[str] = []
    preferred: List[str] = []
    req_set:   set = set()
    pref_set:  set = set()

    for chunk in chunks:
        chunk_skills = _skills_in_text(chunk)
        if not chunk_skills:
            continue

        is_preferred = bool(_PREFERRED_SIGNALS.search(chunk))
        is_required  = bool(_REQUIRED_SIGNALS.search(chunk))

        # Prefer explicit signals; if both fire, required wins
        if is_preferred and not is_required:
            for s in chunk_skills:
                if s not in pref_set:
                    preferred.append(s)
                    pref_set.add(s)
        else:
            for s in chunk_skills:
                if s not in req_set:
                    required.append(s)
                    req_set.add(s)

    # A skill can't be in both buckets; required wins
    preferred = [s for s in preferred if s not in req_set]
    return required, preferred


def _all_skills_from_text(text: str) -> List[str]:
    """Extract all matching skills from text without bucket classification."""
    return _skills_in_text(text)


def _skills_in_text(text: str) -> List[str]:
    """Return canonical skill names matched in the given text snippet."""
    found: List[str] = []
    for canonical, pattern in _COMPILED:
        if pattern.search(text):
            found.append(canonical)
    return found