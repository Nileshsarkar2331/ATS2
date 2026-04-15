"""
Analysis API Router
Handles resume upload, analysis orchestration, and result retrieval.
"""

from __future__ import annotations

import uuid
import hashlib
import asyncio
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from models.schemas import AnalysisResponse
from services.resume_parser import parse_pdf, parse_docx, parse_text
from services.adversarial_detector import detect_adversarial
from services.semantic_engine import analyze_semantic
from services.scoring_engine import compute_scores
from services.explainability_engine import generate_explanation

router = APIRouter(prefix="/api", tags=["analysis"])

# In-memory storage for prototype
_results_store: dict[str, AnalysisResponse] = {}

# Simple cache for analysis results (key: hash of inputs)
_analysis_cache: dict[str, AnalysisResponse] = {}


@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_resume(
    resume: UploadFile = File(...),
    job_description: str = Form(...),
):
    """
    Upload a resume file (PDF/DOCX) and job description text.
    Returns a complete analysis with scoring, adversarial detection, and explanations.
    """
    # Generate analysis ID
    analysis_id = str(uuid.uuid4())[:8]

    # Create cache key from file content and job description
    file_bytes = await resume.read()
    cache_key = hashlib.md5(file_bytes + job_description.encode()).hexdigest()[:16]

    # Check cache first
    if cache_key in _analysis_cache:
        cached_result = _analysis_cache[cache_key]
        # Return cached result with new analysis ID
        response = cached_result.model_copy()
        response.analysis_id = analysis_id
        _results_store[analysis_id] = response
        return response

    # Reset file pointer for parsing
    await resume.seek(0)

    # ─── Step 1: Parse Resume ─────────────────────────
    filename = resume.filename or "unknown"
    file_ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""

    if file_ext == "pdf":
        parsed = parse_pdf(file_bytes, filename)
    elif file_ext in ("docx", "doc"):
        parsed = parse_docx(file_bytes, filename)
    else:
        # Try to decode as text
        try:
            text = file_bytes.decode("utf-8")
            parsed = parse_text(text, filename)
        except UnicodeDecodeError:
            raise HTTPException(
                status_code=400,
                detail="Unsupported file format. Please upload a PDF or DOCX file.",
            )

    if not parsed.raw_text.strip():
        raise HTTPException(
            status_code=400,
            detail="Could not extract text from the uploaded file. The file may be empty or image-based.",
        )

    # ─── Step 2: Adversarial Detection ────────────────
    formatting_meta = {
        "hidden_text_regions": parsed.metadata.hidden_text_regions,
        "font_sizes": parsed.metadata.font_sizes,
        "font_colors": parsed.metadata.font_colors,
    }

    adversarial_result = detect_adversarial(
        raw_text=parsed.raw_text,
        formatting_metadata=formatting_meta,
        job_description=job_description,
    )

    # ─── Step 3: Semantic Analysis ────────────────────
    sections_as_dicts = [
        {"name": s.name, "content": s.content, "start_pos": s.start_pos, "end_pos": s.end_pos}
        for s in parsed.sections
    ]

    # Limit text length for performance
    resume_text_limited = parsed.raw_text[:3000]  # Reduced from unlimited
    jd_limited = job_description[:2000]  # Reduced from unlimited

    # Add timeout to prevent hanging
    try:
        semantic_result = await asyncio.wait_for(
            asyncio.get_event_loop().run_in_executor(
                None, analyze_semantic, resume_text_limited, sections_as_dicts, jd_limited
            ),
            timeout=30.0  # 30 second timeout
        )
    except asyncio.TimeoutError:
        raise HTTPException(
            status_code=408,
            detail="Analysis timed out. Please try with a shorter resume or job description.",
        )

    # ─── Step 4: Compute Scores ───────────────────────
    scoring_result = compute_scores(
        skill_matches=semantic_result.skill_matches,
        semantic_similarity=semantic_result.semantic_similarity,
        experience_authenticity=semantic_result.experience_authenticity,
        anti_cheat_score=adversarial_result.anti_cheat_score,
        adversarial_flags=adversarial_result.flags,
        section_similarities=semantic_result.section_similarities,
    )

    # ─── Step 5: Generate Explanations ────────────────
    explanation = generate_explanation(
        final_score=scoring_result.final_score,
        breakdown=scoring_result.breakdown,
        trust_score=scoring_result.trust_score,
        skill_matches=semantic_result.skill_matches,
        adversarial_flags=adversarial_result.flags,
        section_similarities=semantic_result.section_similarities,
    )

    # ─── Assemble Response ────────────────────────────
    response = AnalysisResponse(
        analysis_id=analysis_id,
        filename=filename,
        final_score=scoring_result.final_score,
        score_breakdown=scoring_result.breakdown,
        trust_score=scoring_result.trust_score,
        skill_matches=semantic_result.skill_matches,
        adversarial_flags=adversarial_result.flags,
        heatmap_segments=adversarial_result.heatmap_segments,
        explanation=explanation,
        resume_sections=parsed.sections,
        raw_text=parsed.raw_text[:3000],  # Reduced from 5000
        job_description=job_description,
    )

    # Store result in cache
    _analysis_cache[cache_key] = response
    _results_store[analysis_id] = response

    return response


@router.get("/results/{analysis_id}", response_model=AnalysisResponse)
async def get_results(analysis_id: str):
    """Retrieve previously computed analysis results."""
    if analysis_id not in _results_store:
        raise HTTPException(
            status_code=404,
            detail=f"Analysis results not found for ID: {analysis_id}",
        )
    return _results_store[analysis_id]


@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "Resilient ATS Engine",
        "version": "1.0.0",
    }"""
Analysis API Router
Handles resume upload, analysis orchestration, and result retrieval.
"""

from __future__ import annotations

import uuid
import hashlib
import asyncio
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from models.schemas import AnalysisResponse
from services.resume_parser import parse_pdf, parse_docx, parse_text
from services.adversarial_detector import detect_adversarial
from services.semantic_engine import analyze_semantic
from services.scoring_engine import compute_scores
from services.explainability_engine import generate_explanation

router = APIRouter(prefix="/api", tags=["analysis"])

# In-memory storage for prototype
_results_store: dict[str, AnalysisResponse] = {}

# Simple cache for analysis results (key: hash of inputs)
_analysis_cache: dict[str, AnalysisResponse] = {}


@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_resume(
    resume: UploadFile = File(...),
    job_description: str = Form(...),
):
    """
    Upload a resume file (PDF/DOCX) and job description text.
    Returns a complete analysis with scoring, adversarial detection, and explanations.
    ""Create cache key from file content and job description
    file_bytes = await resume.read()
    cache_key = hashlib.md5(file_bytes + job_description.encode()).hexdigest()[:16]

    # Check cache first
    if cache_key in _analysis_cache:
        cached_result = _analysis_cache[cache_key]
        # Return cached result with new analysis ID
        response = cached_result.model_copy()
        response.analysis_id = analysis_id
        _results_store[analysis_id] = response
        return response

    # Reset file pointer for parsing
    await resume.seek(0)
    # Generate analysis ID
    analysis_id = str(uuid.uuid4())[:8]

    # ─── Step 1: Parse Resume ─────────────────────────
    file_bytes = await resume.read()
    filename = resume.filename or "unknown"
    file_ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""

    if file_ext == "pdf":
        parsed = parse_pdf(file_bytes, filename)
    elif file_ext in ("docx", "doc"):
        parsed = parse_docx(file_bytes, filename)
    else:
        # Try to decode as text
        try:
            text = file_bytes.decode("utf-8")
            parsed = parse_text(text, filename)
        except UnicodeDecodeError:
            raise HTTPException(
                status_code=400,
                detail="Unsupported file format. Please upload a PDF or DOCX file.",
            )

    if not parsed.raw_text.strip():
        raise HTTPException(
            status_code=400,
            detail="Could not extract text from the uploaded file. The file may be empty or image-based.",
        )

    # ─── Step 2: Adversarial Detection ────────────────
    formatting_meta = {
        "hidden_text_regions": parsed.metadata.hidden_text_regions,
        "font_sizes": parsed.metadata.font_sizes,
        "font_colors": parsed.metadata.font_colors,
    }

    adversarial_result = detect_adversarial(
        raw_text=parsed.raw_text,
        formatting_metadata=formatting_meta,
        job_description=job_description,
    )

    # ─── Step 3: Semantic Analysis ────────────────────
    sections_as_dicts = [
        {"name": s.name, "content": s.content, "start_pos": s.start_pos, "end_pos": s.end_pos}
        for s in parsed.sections
    ]

    # Limit text length for performance
    resume_text_limited = parsed.raw_text[:3000]  # Reduced from unlimited
    jd_limited = job_description[:2000]  # Reduced from unlimited

    semantic_result = analyze_semantic(
        resume_text=resume_text_limited,
        resume_sections=sections_as_dicts,
        job_description=jd_limited,
    )

    # ─── Step 4: Compute Scores ───────────────────────
    scoring_result = compute_scores(
        skill_matches=semantic_result.skill_matches,
        semantic_similarity=semantic_result.semantic_similarity,
        experience_authenticity=semantic_result.experience_authenticity,
        anti_cheat_score=adversarial_result.anti_cheat_score,
        adversarial_flags=adversarial_result.flags,
        section_similarities=semantic_result.section_similarities,
    )

    # ─── Step 5: Generate Explanations ────────────────
    explanation = generate_explanation(
        final_score=scoring_result.final_score,
        breakdown=scoring_result.breakdown,
        trust_score=scoring_result.trust_score,
        skill_matches=semantic_result.skill_matches,
        adversarial_flags=adversarial_result.flags,
        section_similarities=semantic_result.section_similarities,
    )

    # ─── Assemble Response ────────────────────────────
    response = AnalysisResponse(
        analysis_i in cache
    _analysis_cache[cache_key] = responsed=analysis_id,
        filename=filename,
        final_score=scoring_result.final_score,
        score_breakdown=scoring_result.breakdown,
        trust_score=scoring_result.trust_score,
        skill_matches=semantic_result.skill_matches,
        adversarial_flags=adversarial_result.flags,
        heatmap_segments=adversarial_result.heatmap_segments,
        explanation=explanation,
        resume_sections=parsed.sections,
        raw_text=parsed.raw_text[:3000],  # Reduced from 5000
        job_description=job_description,
    )

    # Store result
    _results_store[analysis_id] = response

    return response


@router.get("/results/{analysis_id}", response_model=AnalysisResponse)
async def get_results(analysis_id: str):
    """Retrieve previously computed analysis results."""
    if analysis_id not in _results_store:
        raise HTTPException(
            status_code=404,
            detail=f"Analysis results not found for ID: {analysis_id}",
        )
    return _results_store[analysis_id]


@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "Resilient ATS Engine",
        "version": "1.0.0",
    }
