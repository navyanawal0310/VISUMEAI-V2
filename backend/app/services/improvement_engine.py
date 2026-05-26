"""
improvement_engine.py
---------------------
Generate prioritised, actionable improvement recommendations from a
completed role-match evaluation.

Input  : scalar scores + matched/missing skill lists + narrative gaps
Output : list of recommendation dicts ordered high → medium → low priority

Priority thresholds
  high   : score < 50
  medium : 50 ≤ score < 70
  low    : score ≥ 70
"""

from typing import List, Dict, Optional

# ---------------------------------------------------------------------------
# Priority helper
# ---------------------------------------------------------------------------

def _priority(score: float) -> str:
    if score < 50:
        return "high"
    if score < 70:
        return "medium"
    return "low"


_PRIORITY_ORDER = {"high": 0, "medium": 1, "low": 2}

# ---------------------------------------------------------------------------
# Per-skill learning suggestions
# A small lookup so recommendations name concrete resources/actions.
# Falls back to a generic message for skills not in the table.
# ---------------------------------------------------------------------------

_SKILL_ADVICE: Dict[str, str] = {
    "python":           "Complete a Python project on GitHub (e.g. a REST API or data pipeline) to demonstrate proficiency.",
    "sql":              "Practice query writing on platforms like SQLZoo or Mode Analytics; add a portfolio project that uses SQL.",
    "machine learning": "Work through a Kaggle competition or build an end-to-end ML project and document it publicly.",
    "deep learning":    "Implement a model with PyTorch or TensorFlow and publish it; add it to your skills section explicitly.",
    "tensorflow":       "Add TensorFlow to your resume skills section and link to a notebook or project that uses it.",
    "pytorch":          "Add PyTorch to your resume skills section and link to a notebook or project that uses it.",
    "aws":              "Obtain the AWS Certified Cloud Practitioner cert (free practice exams available) or deploy a project on AWS.",
    "azure":            "Complete the free Microsoft Learn Azure Fundamentals path and add the badge to your resume.",
    "gcp":              "Deploy a project on Google Cloud and mention it alongside the relevant skills.",
    "docker":           "Containerise one of your existing projects, push it to Docker Hub, and reference it on your resume.",
    "kubernetes":       "Deploy a containerised app to a local minikube cluster and write up the process.",
    "react":            "Build and deploy a small React app; list it in a Projects section with a live link.",
    "node.js":          "Add a Node.js REST API project to your GitHub and reference it under experience or projects.",
    "typescript":       "Migrate an existing JavaScript project to TypeScript and mention the upgrade explicitly.",
    "golang":           "Write a small CLI tool or microservice in Go and publish it; list Go under programming languages.",
    "postgresql":       "Set up a PostgreSQL database for a personal project and include it in your skills section.",
    "mongodb":          "Build a CRUD project using MongoDB and reference it alongside your database skills.",
    "spark":            "Complete a PySpark tutorial and add an Apache Spark project to your portfolio.",
    "data science":     "Add a data-science portfolio section with links to EDA notebooks or Kaggle notebooks.",
    "nlp":              "Build a text classification or summarisation project and reference NLP frameworks used.",
    "devops":           "Document CI/CD pipelines you've built; add them to a Projects or Experience bullet point.",
    "ci/cd":            "Set up a GitHub Actions or GitLab CI pipeline for one of your projects and mention it.",
    "agile":            "Mention sprint planning, stand-ups, or retrospectives you've participated in under each role.",
    "rest api":         "Document at least one REST API project with an OpenAPI/Swagger spec.",
    "graphql":          "Add a GraphQL API example project and reference it in your skills list.",
    "microservices":    "Describe any service-oriented architecture work in your experience bullets.",
}

_GENERIC_SKILL_ADVICE = (
    "Study {skill} through online documentation or a project, "
    "then add it explicitly to your skills section."
)

# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def generate(
    *,
    technical_score: float,
    ats_score: float,
    experience_score: float,
    communication_score: float,
    missing_skills: List[str],
    strengths: List[str],
    gaps: List[str],
) -> List[Dict[str, str]]:
    """
    Return a list of recommendation dicts, each with keys:
      category  – Technical | ATS | Experience | Communication
      priority  – high | medium | low
      issue     – one-line problem statement
      suggestion – one-line actionable fix
    Ordered: high first, then medium, then low.
    At most one recommendation per category (for readability) plus one
    recommendation per missing skill (capped at 5 skill recs total).
    """
    recs: List[Dict[str, str]] = []

    # ── Technical ────────────────────────────────────────────────────────
    tech_priority = _priority(technical_score)
    if tech_priority == "high":
        issue = f"Technical score is critically low ({technical_score:.0f}/100) — significant skill gaps exist."
        suggestion = "Focus on the top missing skills below; each one closed lifts this score directly."
    elif tech_priority == "medium":
        issue = f"Technical score is moderate ({technical_score:.0f}/100) — some required skills are missing."
        suggestion = "Address the missing skills in order of relevance to the target role."
    else:
        issue = f"Technical score is strong ({technical_score:.0f}/100)."
        suggestion = "Ensure all matched skills are clearly named in your resume to maximise ATS detection."

    recs.append({
        "category":   "Technical",
        "priority":   tech_priority,
        "issue":      issue,
        "suggestion": suggestion,
    })

    # ── ATS ──────────────────────────────────────────────────────────────
    ats_priority = _priority(ats_score)
    if ats_priority == "high":
        issue = f"ATS score is low ({ats_score:.0f}/100) — resume may be filtered out before human review."
        suggestion = "Add a dedicated Skills section, mirror keywords from the job description, and aim for 300–1 200 words."
    elif ats_priority == "medium":
        issue = f"ATS score is moderate ({ats_score:.0f}/100) — resume passes basic filters but could rank higher."
        suggestion = "Include missing keywords from the job description in context (not just a keyword dump)."
    else:
        issue = f"ATS score is good ({ats_score:.0f}/100)."
        suggestion = "Keep skills phrased exactly as they appear in job postings to maintain high keyword match rates."

    recs.append({
        "category":   "ATS",
        "priority":   ats_priority,
        "issue":      issue,
        "suggestion": suggestion,
    })

    # ── Experience ───────────────────────────────────────────────────────
    exp_priority = _priority(experience_score)
    if exp_priority == "high":
        issue = f"Experience score is low ({experience_score:.0f}/100) — candidate appears under-qualified for this role."
        suggestion = "Highlight contract work, freelance projects, or open-source contributions to supplement formal experience."
    elif exp_priority == "medium":
        issue = f"Experience score is moderate ({experience_score:.0f}/100) — close to the required threshold."
        suggestion = "Quantify achievements in each role (e.g. 'reduced build time by 40%') to strengthen perceived seniority."
    else:
        issue = f"Experience score is strong ({experience_score:.0f}/100)."
        suggestion = "Make sure years of experience are stated clearly near the top of the resume."

    recs.append({
        "category":   "Experience",
        "priority":   exp_priority,
        "issue":      issue,
        "suggestion": suggestion,
    })

    # ── Communication / semantic alignment ───────────────────────────────
    comm_priority = _priority(communication_score)
    if comm_priority == "high":
        issue = f"Resume content is poorly aligned with the job description ({communication_score:.0f}/100)."
        suggestion = "Rewrite your summary and bullet points to use the same language and framing as the job posting."
    elif comm_priority == "medium":
        issue = f"Resume language is partially aligned with the job description ({communication_score:.0f}/100)."
        suggestion = "Tailor your professional summary to echo the role's priorities and key responsibilities."
    else:
        issue = f"Resume language aligns well with the job description ({communication_score:.0f}/100)."
        suggestion = "Maintain role-specific tailoring for each new application rather than using a generic resume."

    recs.append({
        "category":   "Communication",
        "priority":   comm_priority,
        "issue":      issue,
        "suggestion": suggestion,
    })

    # ── Per-skill recommendations (cap at 5 to avoid noise) ─────────────
    for skill in missing_skills[:5]:
        advice = _SKILL_ADVICE.get(
            skill.lower(),
            _GENERIC_SKILL_ADVICE.format(skill=skill),
        )
        recs.append({
            "category":   "Technical",
            "priority":   "high" if technical_score < 50 else "medium",
            "issue":      f"Required skill '{skill}' not found in resume.",
            "suggestion": advice,
        })

    # ── Sort: high → medium → low, stable within each tier ───────────────
    recs.sort(key=lambda r: _PRIORITY_ORDER[r["priority"]])

    return recs