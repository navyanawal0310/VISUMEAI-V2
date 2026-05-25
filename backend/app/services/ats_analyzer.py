import re
from typing import Dict, List


class ATSAnalyzer:
    """
    Analyze resume ATS friendliness
    """

    ACTION_VERBS = {
        "developed", "built", "implemented", "designed",
        "managed", "created", "optimized", "led",
        "improved", "engineered", "analyzed", "deployed"
    }

    def analyze(self, parsed_resume, required_skills=None) -> Dict:

        text = parsed_resume.parsed_text.lower()

        score = 0
        issues = []
        recommendations = []

        # -------------------------------------------------
        # SECTION CHECKS
        # -------------------------------------------------

        if parsed_resume.skills:
            score += 15
        else:
            issues.append("Missing skills section")
            recommendations.append("Add a dedicated skills section")

        if parsed_resume.education:
            score += 10
        else:
            issues.append("Missing education section")

        if parsed_resume.projects:
            score += 15
        else:
            issues.append("No projects detected")
            recommendations.append("Add project experience")

        if parsed_resume.experience_years > 0:
            score += 15
        else:
            issues.append("No experience detected")

        # -------------------------------------------------
        # KEYWORD MATCHING
        # -------------------------------------------------

        keyword_score = 0

        if required_skills:
            matched = 0

            for skill in required_skills:
                if skill.lower() in text:
                    matched += 1

            keyword_score = (
                matched / len(required_skills)
            ) * 25

        score += keyword_score

        if keyword_score < 15:
            issues.append("Low keyword match with job description")
            recommendations.append(
                "Add more job-relevant keywords"
            )

        # -------------------------------------------------
        # ACTION VERBS
        # -------------------------------------------------

        verb_matches = sum(
            1 for verb in self.ACTION_VERBS
            if verb in text
        )

        if verb_matches >= 5:
            score += 10
        else:
            issues.append("Weak action verbs")
            recommendations.append(
                "Use stronger action verbs like 'developed', 'implemented', 'led'"
            )

        # -------------------------------------------------
        # RESUME LENGTH
        # -------------------------------------------------

        word_count = len(text.split())

        if 300 <= word_count <= 1200:
            score += 10
        else:
            issues.append("Resume length may not be ATS optimal")

        # -------------------------------------------------
        # FINALIZE
        # -------------------------------------------------

        score = min(100, round(score, 1))

        return {
            "ats_score": score,
            "issues": issues,
            "recommendations": recommendations
        }