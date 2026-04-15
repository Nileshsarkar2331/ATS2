"""
AI Explainability Engine
Generates human-readable explanations for the analysis results.
Produces strengths, weaknesses, suggestions, and detailed reasoning.
"""

from __future__ import annotations

from models.schemas import ExplanationData, SkillMatch, AdversarialFlag, ScoreBreakdown, TrustScoreData


def generate_explanation(
    final_score: float,
    breakdown: ScoreBreakdown,
    trust_score: TrustScoreData,
    skill_matches: list[SkillMatch],
    adversarial_flags: list[AdversarialFlag],
    section_similarities: dict[str, float],
) -> ExplanationData:
    """Generate comprehensive AI explanation of the analysis."""
    strengths = []
    weaknesses = []
    suggestions = []

    # ─── Analyze skill matches ────────────────────────
    matched_skills = [s for s in skill_matches if s.found]
    unmatched_skills = [s for s in skill_matches if not s.found]
    evidenced_skills = [s for s in matched_skills if s.has_project_evidence]

    total = len(skill_matches)
    match_pct = (len(matched_skills) / total * 100) if total > 0 else 0

    if match_pct >= 80:
        strengths.append(
            f"Excellent skill coverage — {len(matched_skills)}/{total} "
            f"required skills found ({match_pct:.0f}% match rate)."
        )
    elif match_pct >= 50:
        strengths.append(
            f"Good skill alignment — {len(matched_skills)}/{total} "
            f"required skills present."
        )
    else:
        weaknesses.append(
            f"Low skill match — only {len(matched_skills)}/{total} "
            f"required skills found ({match_pct:.0f}%)."
        )

    if unmatched_skills:
        missing = ", ".join(s.skill for s in unmatched_skills[:5])
        suggestions.append(
            f"Add missing skills to your resume: {missing}. "
            f"Include them naturally within project descriptions."
        )

    if evidenced_skills:
        strengths.append(
            f"{len(evidenced_skills)} skills supported by project/experience evidence, "
            f"demonstrating practical application."
        )
    elif matched_skills:
        weaknesses.append(
            "Skills are listed but lack supporting evidence in project descriptions."
        )
        suggestions.append(
            "For each key skill, describe a specific project or achievement where you applied it. "
            "Use the STAR method (Situation, Task, Action, Result)."
        )

    # ─── Analyze semantic similarity ──────────────────
    sem_score = breakdown.semantic_similarity_score
    if sem_score >= 75:
        strengths.append(
            "Strong semantic alignment with the job description — "
            "your experience narrative closely matches what the role requires."
        )
    elif sem_score >= 50:
        pass  # Neutral, don't mention
    else:
        weaknesses.append(
            "Weak semantic match with the job description — "
            "your resume may not clearly communicate relevant experience."
        )
        suggestions.append(
            "Tailor your professional summary and experience descriptions to use "
            "similar language and focus areas as the job description."
        )

    # ─── Analyze section-level strengths ──────────────
    if section_similarities:
        best_section = max(section_similarities.items(), key=lambda x: x[1])
        if best_section[1] > 0.5:
            strengths.append(
                f"Your '{best_section[0]}' section is the strongest match "
                f"to the job requirements."
            )

        worst_section = min(section_similarities.items(), key=lambda x: x[1])
        if worst_section[1] < 0.3 and worst_section[0] != "header":
            weaknesses.append(
                f"Your '{worst_section[0]}' section has weak alignment with "
                f"the job description."
            )

    # ─── Analyze experience authenticity ──────────────
    exp_score = breakdown.experience_authenticity_score
    if exp_score >= 80:
        strengths.append(
            "Experience section demonstrates strong consistency between "
            "claimed skills and described work."
        )
    elif exp_score < 60:
        weaknesses.append(
            "Skills listed don't strongly correlate with described experience. "
            "This can appear inauthentic to reviewers."
        )
        suggestions.append(
            "Ensure each skill in your Skills section appears in at least one "
            "project or experience description with concrete context."
        )

    # ─── Analyze adversarial flags ────────────────────
    if not adversarial_flags:
        strengths.append(
            "Clean formatting — no adversarial manipulation tactics detected."
        )
    else:
        flag_types = set(f.type for f in adversarial_flags)

        if "hidden_text" in flag_types:
            weaknesses.append(
                "⚠️ Hidden text detected — invisible content (white font, tiny text) "
                "is a serious red flag that can lead to automatic rejection."
            )
            suggestions.append(
                "Remove all hidden text from your resume. Every word should be "
                "visible and readable. Hidden text is easily detected by modern ATS systems."
            )

        if "keyword_stuffing" in flag_types:
            weaknesses.append(
                "Keyword stuffing detected — certain terms appear with unnaturally "
                "high frequency, suggesting artificial inflation."
            )
            suggestions.append(
                "Use keywords naturally within sentences rather than repeating them. "
                "Quality of context matters more than quantity of mentions."
            )

        if "repetition" in flag_types:
            weaknesses.append(
                "Excessive repetition detected — similar phrases appear multiple times."
            )
            suggestions.append(
                "Vary your language and descriptions. Each bullet point should "
                "convey unique information about your achievements."
            )

        if "jd_copy_paste" in flag_types:
            weaknesses.append(
                "Job description copy-paste detected — sections of your resume "
                "appear to be directly copied from the JD."
            )
            suggestions.append(
                "Rewrite matching sections in your own words. Echo the JD's requirements "
                "but describe your actual experience and achievements."
            )

    # ─── Generate summary narrative ───────────────────
    score_label = _score_label(final_score)
    summary = _generate_summary(
        final_score, score_label, matched_skills, unmatched_skills,
        breakdown, trust_score
    )

    # ─── Generate detailed reasoning ─────────────────
    detailed = _generate_detailed_reasoning(
        breakdown, trust_score, len(matched_skills), len(skill_matches),
        adversarial_flags
    )

    return ExplanationData(
        summary=summary,
        strengths=strengths,
        weaknesses=weaknesses,
        suggestions=suggestions,
        detailed_reasoning=detailed,
    )


def _score_label(score: float) -> str:
    """Convert numeric score to human-readable label."""
    if score >= 90:
        return "Excellent"
    elif score >= 75:
        return "Strong"
    elif score >= 60:
        return "Good"
    elif score >= 45:
        return "Fair"
    elif score >= 30:
        return "Below Average"
    else:
        return "Needs Improvement"


def _generate_summary(
    score: float,
    label: str,
    matched: list[SkillMatch],
    unmatched: list[SkillMatch],
    breakdown: ScoreBreakdown,
    trust: TrustScoreData,
) -> str:
    """Generate the main summary paragraph."""
    parts = [f"This resume received a {label} score of {score:.0f}/100."]

    if matched:
        top_skills = ", ".join(s.skill for s in matched[:3])
        parts.append(
            f"Key matching skills include {top_skills}."
        )

    if breakdown.semantic_similarity_score >= 60:
        parts.append(
            "The resume shows good semantic alignment with the job requirements."
        )
    elif breakdown.semantic_similarity_score < 40:
        parts.append(
            "The resume could be better tailored to match the job description."
        )

    if trust.level.value == "flagged":
        parts.append(
            "⚠️ The trust score is low — reviewers should manually verify this resume."
        )
    elif trust.level.value == "highly_trusted":
        parts.append(
            "The resume demonstrates high authenticity with verified skill-experience consistency."
        )

    if unmatched:
        missing = ", ".join(s.skill for s in unmatched[:3])
        parts.append(
            f"Missing key skills: {missing}."
        )

    return " ".join(parts)


def _generate_detailed_reasoning(
    breakdown: ScoreBreakdown,
    trust: TrustScoreData,
    matched_count: int,
    total_skills: int,
    flags: list[AdversarialFlag],
) -> str:
    """Generate detailed reasoning for the score."""
    lines = [
        "### Score Breakdown Analysis\n",
        f"**Skill Match ({breakdown.skill_match_weight*100:.0f}% weight):** "
        f"Score {breakdown.skill_match_score:.0f}/100 — "
        f"{matched_count}/{total_skills} required skills identified.\n",
        f"**Experience Authenticity ({breakdown.experience_weight*100:.0f}% weight):** "
        f"Score {breakdown.experience_authenticity_score:.0f}/100 — "
        f"Measures consistency between listed skills and described experience.\n",
        f"**Semantic Similarity ({breakdown.semantic_weight*100:.0f}% weight):** "
        f"Score {breakdown.semantic_similarity_score:.0f}/100 — "
        f"NLP-based meaning comparison between resume and job description.\n",
        f"**Anti-Cheat ({breakdown.anti_cheat_weight*100:.0f}% weight):** "
        f"Score {breakdown.anti_cheat_score:.0f}/100 — "
        f"{len(flags)} adversarial flag(s) detected.\n",
        f"\n### Trust Assessment\n",
        f"Trust Score: {trust.score:.0f}/100 ({trust.level.value.replace('_', ' ').title()})\n",
        f"- Content Integrity: {trust.content_integrity:.0f}/100\n",
        f"- Consistency: {trust.consistency:.0f}/100\n",
        f"- Originality: {trust.originality:.0f}/100\n",
    ]

    return "".join(lines)
