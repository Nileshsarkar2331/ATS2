"""
Pydantic schemas for the Resilient ATS API.
Defines all request/response models for resume analysis.
"""

from __future__ import annotations

from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum


# ─── Enums ──────────────────────────────────────────────

class TrustLevel(str, Enum):
    HIGHLY_TRUSTED = "highly_trusted"
    TRUSTED = "trusted"
    REVIEW_RECOMMENDED = "review_recommended"
    FLAGGED = "flagged"


class Severity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


# ─── Sub-models ─────────────────────────────────────────

class SkillMatch(BaseModel):
    """A matched skill with context and confidence."""
    skill: str
    found: bool = False
    confidence: float = Field(0.0, ge=0.0, le=1.0)
    context: str = ""  # Where in the resume it was found
    has_project_evidence: bool = False


class AdversarialFlag(BaseModel):
    """A single adversarial detection flag."""
    type: str  # hidden_text, keyword_stuffing, repetition, jd_copy_paste
    severity: Severity = Severity.LOW
    description: str = ""
    text_snippet: str = ""
    start_pos: int = 0
    end_pos: int = 0
    penalty: float = 0.0


class HeatmapSegment(BaseModel):
    """A segment of text with a suspicion level for heatmap rendering."""
    text: str
    suspicion_level: float = Field(0.0, ge=0.0, le=1.0)  # 0 = clean, 1 = highly suspicious
    flag_type: Optional[str] = None
    tooltip: str = ""


class ScoreBreakdown(BaseModel):
    """Detailed breakdown of all scoring factors."""
    skill_match_score: float = Field(0.0, ge=0.0, le=100.0)
    experience_authenticity_score: float = Field(0.0, ge=0.0, le=100.0)
    semantic_similarity_score: float = Field(0.0, ge=0.0, le=100.0)
    anti_cheat_score: float = Field(0.0, ge=0.0, le=100.0)
    skill_match_weight: float = 0.25
    experience_weight: float = 0.20
    semantic_weight: float = 0.30
    anti_cheat_weight: float = 0.25


class TrustScoreData(BaseModel):
    """Trust score with breakdown."""
    score: float = Field(0.0, ge=0.0, le=100.0)
    level: TrustLevel = TrustLevel.REVIEW_RECOMMENDED
    content_integrity: float = Field(0.0, ge=0.0, le=100.0)
    consistency: float = Field(0.0, ge=0.0, le=100.0)
    originality: float = Field(0.0, ge=0.0, le=100.0)
    explanation: str = ""


class ExplanationData(BaseModel):
    """AI-generated explanation of the analysis."""
    summary: str = ""
    strengths: list[str] = []
    weaknesses: list[str] = []
    suggestions: list[str] = []
    detailed_reasoning: str = ""


class ResumeSection(BaseModel):
    """A parsed section of the resume."""
    name: str
    content: str
    start_pos: int = 0
    end_pos: int = 0


# ─── API Request/Response ───────────────────────────────

class AnalysisResponse(BaseModel):
    """Complete analysis response returned to the frontend."""
    analysis_id: str
    filename: str
    final_score: float = Field(0.0, ge=0.0, le=100.0)
    score_breakdown: ScoreBreakdown
    trust_score: TrustScoreData
    skill_matches: list[SkillMatch] = []
    adversarial_flags: list[AdversarialFlag] = []
    heatmap_segments: list[HeatmapSegment] = []
    explanation: ExplanationData
    resume_sections: list[ResumeSection] = []
    raw_text: str = ""
    job_description: str = ""
