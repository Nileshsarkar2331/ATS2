"""
Multi-Factor Scoring Engine
Combines all analysis results into a final ATS score (0-100).

Scoring weights:
- Skill Match Score:          25%
- Experience Authenticity:    20%
- Semantic Similarity:        30%
- Anti-Cheat Score:           25%
"""

from __future__ import annotations

from models.schemas import ScoreBreakdown, TrustScoreData, TrustLevel


class ScoringResult:
    """Complete scoring result."""

    def __init__(self):
        self.final_score: float = 0.0
        self.breakdown: ScoreBreakdown = ScoreBreakdown()
        self.trust_score: TrustScoreData = TrustScoreData()


def compute_scores(
    skill_matches: list,
    semantic_similarity: float,
    experience_authenticity: float,
    anti_cheat_score: float,
    adversarial_flags: list,
    section_similarities: dict,
) -> ScoringResult:
    """Compute the complete multi-factor score."""
    result = ScoringResult()

    # ─── 1. Skill Match Score (0-100) ─────────────────
    if skill_matches:
        found_skills = [s for s in skill_matches if s.found]
        total_skills = len(skill_matches)

        # Base score from match percentage
        match_pct = len(found_skills) / total_skills if total_skills > 0 else 0

        # Bonus for skills with project evidence
        evidence_pct = (
            sum(1 for s in found_skills if s.has_project_evidence) / len(found_skills)
            if found_skills else 0
        )

        # Weighted skill score
        skill_score = (match_pct * 70) + (evidence_pct * 30)
    else:
        skill_score = 50.0  # Neutral if no JD skills to match

    # ─── 2. Experience Authenticity Score (0-100) ─────
    exp_score = experience_authenticity  # Already 0-100 from semantic engine

    # ─── 3. Semantic Similarity Score (0-100) ─────────
    # Cosine similarity is typically 0-1; scale to 0-100
    # But values rarely exceed 0.8 for resumes, so use adjusted scaling
    raw_sim = max(0, semantic_similarity)
    if raw_sim > 0.6:
        sem_score = 70 + ((raw_sim - 0.6) / 0.4) * 30  # 70-100 range
    elif raw_sim > 0.3:
        sem_score = 30 + ((raw_sim - 0.3) / 0.3) * 40  # 30-70 range
    else:
        sem_score = raw_sim / 0.3 * 30  # 0-30 range

    # ─── 4. Anti-Cheat Score (0-100) ──────────────────
    cheat_score = anti_cheat_score  # Already 0-100

    # ─── Store breakdown ──────────────────────────────
    result.breakdown = ScoreBreakdown(
        skill_match_score=round(skill_score, 1),
        experience_authenticity_score=round(exp_score, 1),
        semantic_similarity_score=round(sem_score, 1),
        anti_cheat_score=round(cheat_score, 1),
        skill_match_weight=0.25,
        experience_weight=0.20,
        semantic_weight=0.30,
        anti_cheat_weight=0.25,
    )

    # ─── Final weighted score ─────────────────────────
    result.final_score = round(
        (skill_score * 0.25)
        + (exp_score * 0.20)
        + (sem_score * 0.30)
        + (cheat_score * 0.25),
        1,
    )
    result.final_score = max(0, min(100, result.final_score))

    # ─── Trust Score ──────────────────────────────────
    result.trust_score = _compute_trust_score(
        cheat_score, exp_score, adversarial_flags, semantic_similarity
    )

    return result


def _compute_trust_score(
    anti_cheat_score: float,
    experience_authenticity: float,
    adversarial_flags: list,
    semantic_similarity: float,
) -> TrustScoreData:
    """Compute the trust/authenticity score with breakdown."""

    # Content Integrity (40%): Based on anti-cheat score
    content_integrity = anti_cheat_score

    # Consistency (35%): Based on experience authenticity
    consistency = experience_authenticity

    # Originality (25%): Inverse of JD copy-paste issues
    jd_copy_flags = [f for f in adversarial_flags if f.type == "jd_copy_paste"]
    copy_penalty = sum(f.penalty for f in jd_copy_flags)
    originality = max(0, 100 - copy_penalty * 3)

    # Weighted trust score
    trust_score = (
        content_integrity * 0.40
        + consistency * 0.35
        + originality * 0.25
    )
    trust_score = round(max(0, min(100, trust_score)), 1)

    # Determine trust level
    if trust_score >= 90:
        level = TrustLevel.HIGHLY_TRUSTED
    elif trust_score >= 70:
        level = TrustLevel.TRUSTED
    elif trust_score >= 50:
        level = TrustLevel.REVIEW_RECOMMENDED
    else:
        level = TrustLevel.FLAGGED

    # Generate explanation
    explanations = []
    if content_integrity >= 90:
        explanations.append("No formatting manipulation detected.")
    elif content_integrity < 70:
        explanations.append("Suspicious formatting patterns found.")

    if consistency >= 80:
        explanations.append("Skills are well-supported by project evidence.")
    elif consistency < 60:
        explanations.append("Limited evidence supporting claimed skills.")

    if originality >= 85:
        explanations.append("Resume content appears original and authentic.")
    elif originality < 60:
        explanations.append("Significant overlap with job description text detected.")

    return TrustScoreData(
        score=trust_score,
        level=level,
        content_integrity=round(content_integrity, 1),
        consistency=round(consistency, 1),
        originality=round(originality, 1),
        explanation=" ".join(explanations),
    )
