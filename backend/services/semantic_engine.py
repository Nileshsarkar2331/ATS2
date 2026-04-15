"""
Semantic Analysis Engine
Uses sentence-transformers for embedding-based similarity matching.
Performs skill extraction, experience validation, and semantic scoring.
"""

from __future__ import annotations

import re
from typing import Optional
from models.schemas import SkillMatch


# ─── Common skill patterns for extraction ────────────────
TECH_SKILLS = [
    # Programming Languages
    "python", "javascript", "typescript", "java", "c++", "c#", "go", "rust",
    "ruby", "php", "swift", "kotlin", "scala", "r", "matlab", "perl",
    # Web Frameworks
    "react", "angular", "vue", "next.js", "nuxt.js", "express", "django",
    "flask", "fastapi", "spring boot", "rails", "laravel", "asp.net",
    # Data & ML
    "tensorflow", "pytorch", "scikit-learn", "pandas", "numpy", "keras",
    "machine learning", "deep learning", "nlp", "computer vision",
    "data analysis", "data science", "data engineering",
    # Cloud & DevOps
    "aws", "azure", "gcp", "docker", "kubernetes", "terraform", "ci/cd",
    "jenkins", "github actions", "gitlab ci",
    # Databases
    "postgresql", "mysql", "mongodb", "redis", "elasticsearch",
    "dynamodb", "cassandra", "sqlite", "sql", "nosql",
    # Tools & Platforms
    "git", "linux", "agile", "scrum", "jira", "confluence",
    "figma", "photoshop", "illustrator",
    # Soft Skills
    "leadership", "communication", "teamwork", "problem solving",
    "project management", "mentoring", "strategic planning",
]


class SemanticAnalysisResult:
    """Result of semantic analysis."""

    def __init__(self):
        self.semantic_similarity: float = 0.0
        self.section_similarities: dict[str, float] = {}
        self.skill_matches: list[SkillMatch] = []
        self.experience_authenticity: float = 0.0
        self.jd_skills: list[str] = []
        self.resume_skills: list[str] = []


# Global model reference (loaded once)
_model = None
_model_loading = False


def _get_model():
    """Lazy-load the sentence transformer model."""
    global _model, _model_loading
    if _model is None and not _model_loading:
        _model_loading = True
        try:
            from sentence_transformers import SentenceTransformer
            # Use lighter model for faster loading
            _model = SentenceTransformer("paraphrase-MiniLM-L3-v2")  # Faster than all-MiniLM-L6-v2
        except Exception as e:
            print(f"Warning: Could not load sentence-transformers model: {e}")
            _model_loading = False
            return None
        _model_loading = False
    return _model


def analyze_semantic(
    resume_text: str,
    resume_sections: list[dict],
    job_description: str,
) -> SemanticAnalysisResult:
    """Perform full semantic analysis of resume against job description."""
    result = SemanticAnalysisResult()

    # Extract skills from both texts
    result.jd_skills = _extract_skills(job_description)
    result.resume_skills = _extract_skills(resume_text)
Use TF-IDF by default for speed, embeddings as fallback
    model = _get_model()

    if model is not None:
        result = _analyze_with_embeddings(
            model, resume_text, resume_sections, job_description, result
        )
    else:
        # Primary: TF-IDF based matching (faster)
        # Fallback: TF-IDF based matching
        result = _analyze_with_tfidf(
            resume_text, resume_sections, job_description, result
        )

    # Skill matching with context
    result.skill_matches = _match_skills(
        result.jd_skills, resume_text, resume_sections
    )

    # Experience authenticity check
    result.experience_authenticity = _validate_experience(
        resume_text, resume_sections, result.resume_skills
    )

    return result


def _analyze_with_embeddings(
    model,
    resume_text: str,
    resume_sections: list[dict],
    job_description: str,
    result: SemanticAnalysisResult,
) -> SemanticAnalysisResult:
    """Analyze using sentence-transformer embeddings."""
    import numpy as np

    # Encode full texts (limit length for speed)
    resume_embedding = model.encode(resume_text[:1500], convert_to_numpy=True)
    jd_embedding = model.encode(job_description[:1500], convert_to_numpy=True)

    # Overall cosine similarity
    result.semantic_similarity = float(
        np.dot(resume_embedding, jd_embedding)
        / (np.linalg.norm(resume_embedding) * np.linalg.norm(jd_embedding) + 1e-8)
    )

    # Limit section analysis to top 3 longest sections for speed
    sorted_sections = sorted(
        resume_sections,
        key=lambda s: len(s.get("content", "") if isinstance(s, dict) else s.content),
        reverse=True
    )[:3]  # Only analyze top 3 sections

    for section in sorted_sections:
        section_name = section.get("name", "") if isinstance(section, dict) else section.name
        section_content = section.get("content", "") if isinstance(section, dict) else section.content

        if len(section_content) < 50:  # Increased minimum length
            continue

        section_emb = model.encode(section_content[:800], convert_to_numpy=True)  # Reduced length
        sim = float(
            np.dot(section_emb, jd_embedding)
            / (np.linalg.norm(section_emb) * np.linalg.norm(jd_embedding) + 1e-8)
        )
        result.section_similarities[section_name] = round(sim, 3)

    return result


def _analyze_with_tfidf(
    resume_text: str,
    resume_sections: list[dict],
    job_description: str,
    result: SemanticAnalysisResult,
) -> SemanticAnalysisResult:
    """Fallback: TF-IDF based similarity analysis."""
    try:
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.metrics.pairwise import cosine_similarity

        vectorizer = TfidfVectorizer(max_features=5000, stop_words="english")
        tfidf_matrix = vectorizer.fit_transform([resume_text, job_description])

        result.semantic_similarity = float(
            cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
        )

        # Per-section
        for section in resume_sections:
            section_name = section.get("name", "") if isinstance(section, dict) else section.name
            section_content = section.get("content", "") if isinstance(section, dict) else section.content

            if len(section_content) < 20:
                continue

            try:
                section_tfidf = vectorizer.transform([section_content])
                jd_tfidf = vectorizer.transform([job_description])
                sim = float(cosine_similarity(section_tfidf, jd_tfidf)[0][0])
                result.section_similarities[section_name] = round(sim, 3)
            except Exception:
                pass

    except ImportError:
        # Ultimate fallback: simple word overlap
        resume_words = set(resume_text.lower().split())
        jd_words = set(job_description.lower().split())
        if jd_words:
            overlap = len(resume_words & jd_words) / len(jd_words)
            result.semantic_similarity = min(1.0, overlap)

    return result


def _extract_skills(text: str) -> list[str]:
    """Extract skills mentioned in text using pattern matching."""
    text_lower = text.lower()
    found_skills = []

    for skill in TECH_SKILLS:
        # Use word boundary matching for short skills
        if len(skill) <= 3:
            pattern = rf"\b{re.escape(skill)}\b"
        else:
            pattern = re.escape(skill)

        if re.search(pattern, text_lower):
            found_skills.append(skill)

    return found_skills


def _match_skills(
    jd_skills: list[str],
    resume_text: str,
    resume_sections: list[dict],
) -> list[SkillMatch]:
    """Match JD-required skills against resume with context."""
    results = []
    resume_lower = resume_text.lower()

    for skill in jd_skills:
        match = SkillMatch(skill=skill)

        # Check if skill exists in resume
        if len(skill) <= 3:
            pattern = rf"\b{re.escape(skill)}\b"
        else:
            pattern = re.escape(skill)

        occurrences = list(re.finditer(pattern, resume_lower))
        match.found = len(occurrences) > 0

        if match.found:
            # Get context around the skill mention
            first_pos = occurrences[0].start()
            context_start = max(0, first_pos - 50)
            context_end = min(len(resume_text), first_pos + len(skill) + 50)
            match.context = resume_text[context_start:context_end].strip()

            # Check for project evidence (skill in experience/projects sections)
            match.has_project_evidence = _skill_has_evidence(
                skill, resume_sections
            )

            # Confidence based on context richness
            base_conf = 0.5
            if match.has_project_evidence:
                base_conf += 0.3
            if len(occurrences) > 1:
                base_conf += 0.1
            if len(match.context) > 40:
                base_conf += 0.1
            match.confidence = min(1.0, base_conf)
        else:
            match.confidence = 0.0

        results.append(match)

    return results


def _skill_has_evidence(skill: str, sections: list[dict]) -> bool:
    """Check if a skill has supporting evidence in experience/project sections."""
    evidence_sections = {"experience", "projects", "achievements"}

    for section in sections:
        section_name = section.get("name", "") if isinstance(section, dict) else section.name
        section_content = section.get("content", "") if isinstance(section, dict) else section.content

        if section_name.lower() in evidence_sections:
            if skill.lower() in section_content.lower():
                return True

    return False


def _validate_experience(
    resume_text: str,
    sections: list[dict],
    resume_skills: list[str],
) -> float:
    """Validate experience authenticity (skills-to-projects consistency)."""
    score = 100.0

    # Get skills section and experience section
    skills_content = ""
    experience_content = ""
    projects_content = ""

    for section in sections:
        name = section.get("name", "") if isinstance(section, dict) else section.name
        content = section.get("content", "") if isinstance(section, dict) else section.content
        name_lower = name.lower()

        if "skill" in name_lower:
            skills_content = content
        elif "experience" in name_lower:
            experience_content = content
        elif "project" in name_lower:
            projects_content = content

    combined_evidence = (experience_content + " " + projects_content).lower()

    if not skills_content or not combined_evidence:
        return 70.0  # Neutral if we can't validate

    # Check what % of claimed skills have evidence in experience/projects
    skills_in_skills_section = _extract_skills(skills_content)
    skills_with_evidence = 0

    for skill in skills_in_skills_section:
        if skill.lower() in combined_evidence:
            skills_with_evidence += 1

    if skills_in_skills_section:
        evidence_ratio = skills_with_evidence / len(skills_in_skills_section)
        score = 40.0 + (evidence_ratio * 60.0)  # 40-100 range
    else:
        score = 60.0

    # Check for quantifiable achievements (numbers in experience)
    numbers = re.findall(r"\b\d+[%+]?\b", combined_evidence)
    if len(numbers) > 3:
        score = min(100, score + 5)  # Bonus for quantified achievements

    # Check for action verbs (good sign)
    action_verbs = [
        "developed", "built", "designed", "implemented", "led",
        "managed", "created", "optimized", "reduced", "increased",
        "deployed", "architected", "mentored", "launched", "delivered",
    ]
    verb_count = sum(1 for v in action_verbs if v in combined_evidence)
    if verb_count > 5:
        score = min(100, score + 5)

    return round(score, 1)
