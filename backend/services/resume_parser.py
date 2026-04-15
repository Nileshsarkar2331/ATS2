"""
Resume Parser Service
Extracts text, sections, and formatting metadata from PDF and DOCX files.
Supports adversarial metadata extraction (font colors, sizes, visibility).
"""

from __future__ import annotations

import io
import re
from typing import Optional
from models.schemas import ResumeSection


# ─── Section header patterns ────────────────────────────
SECTION_PATTERNS = {
    "summary": r"(?i)\b(summary|objective|profile|about\s*me|professional\s*summary)\b",
    "experience": r"(?i)\b(experience|work\s*history|employment|professional\s*experience|work\s*experience)\b",
    "education": r"(?i)\b(education|academic|qualification|degree|university|college)\b",
    "skills": r"(?i)\b(skills|technical\s*skills|core\s*competencies|technologies|tech\s*stack)\b",
    "projects": r"(?i)\b(projects|personal\s*projects|portfolio|key\s*projects)\b",
    "certifications": r"(?i)\b(certifications|certificates|licenses|accreditations)\b",
    "achievements": r"(?i)\b(achievements|awards|honors|accomplishments)\b",
}


class FormattingMetadata:
    """Metadata about text formatting for adversarial detection."""

    def __init__(self):
        self.hidden_text_regions: list[dict] = []  # {start, end, reason, text}
        self.font_sizes: list[dict] = []  # {size, text, start, end}
        self.font_colors: list[dict] = []  # {color, text, start, end}
        self.total_chars: int = 0
        self.visible_chars: int = 0


class ParsedResume:
    """Complete parsed resume with text, sections, and metadata."""

    def __init__(self):
        self.raw_text: str = ""
        self.sections: list[ResumeSection] = []
        self.metadata: FormattingMetadata = FormattingMetadata()
        self.filename: str = ""
        self.file_type: str = ""


def parse_pdf(file_bytes: bytes, filename: str) -> ParsedResume:
    """Parse a PDF file and extract text with formatting metadata."""
    import fitz  # PyMuPDF

    result = ParsedResume()
    result.filename = filename
    result.file_type = "pdf"

    doc = fitz.open(stream=file_bytes, filetype="pdf")
    all_text_parts = []
    current_pos = 0

    for page_num, page in enumerate(doc):
        # Extract text blocks with formatting info
        blocks = page.get_text("dict", flags=fitz.TEXT_PRESERVE_WHITESPACE)

        for block in blocks.get("blocks", []):
            if block.get("type") != 0:  # Skip image blocks
                continue

            for line in block.get("lines", []):
                for span in line.get("spans", []):
                    text = span.get("text", "")
                    if not text.strip():
                        continue

                    font_size = span.get("size", 12)
                    color = span.get("color", 0)
                    flags = span.get("flags", 0)

                    start_pos = current_pos
                    end_pos = current_pos + len(text)

                    # Track font sizes
                    result.metadata.font_sizes.append({
                        "size": font_size,
                        "text": text[:50],
                        "start": start_pos,
                        "end": end_pos,
                    })

                    # Track font colors
                    result.metadata.font_colors.append({
                        "color": color,
                        "text": text[:50],
                        "start": start_pos,
                        "end": end_pos,
                    })

                    # Detect hidden text: white/near-white on white, or tiny font
                    is_hidden = False
                    reason = ""

                    # White or near-white text (RGB > 250 for all channels)
                    r = (color >> 16) & 0xFF
                    g = (color >> 8) & 0xFF
                    b = color & 0xFF
                    if r > 250 and g > 250 and b > 250:
                        is_hidden = True
                        reason = "white_text"

                    # Extremely small font (< 4pt)
                    if font_size < 4:
                        is_hidden = True
                        reason = "tiny_text" if not reason else reason + "+tiny_text"

                    if is_hidden:
                        result.metadata.hidden_text_regions.append({
                            "start": start_pos,
                            "end": end_pos,
                            "reason": reason,
                            "text": text,
                        })

                    all_text_parts.append(text)
                    current_pos = end_pos

                all_text_parts.append(" ")
                current_pos += 1

            all_text_parts.append("\n")
            current_pos += 1

        all_text_parts.append("\n\n")
        current_pos += 2

    doc.close()

    result.raw_text = "".join(all_text_parts).strip()
    result.metadata.total_chars = len(result.raw_text)
    result.metadata.visible_chars = result.metadata.total_chars - sum(
        len(r["text"]) for r in result.metadata.hidden_text_regions
    )

    # Split into sections
    result.sections = _split_sections(result.raw_text)

    return result


def parse_docx(file_bytes: bytes, filename: str) -> ParsedResume:
    """Parse a DOCX file and extract text with basic metadata."""
    from docx import Document

    result = ParsedResume()
    result.filename = filename
    result.file_type = "docx"

    doc = Document(io.BytesIO(file_bytes))
    all_text_parts = []
    current_pos = 0

    for para in doc.paragraphs:
        para_text = para.text.strip()
        if not para_text:
            all_text_parts.append("\n")
            current_pos += 1
            continue

        # Check runs for hidden formatting
        for run in para.runs:
            text = run.text
            if not text:
                continue

            start_pos = current_pos
            end_pos = current_pos + len(text)

            font = run.font
            is_hidden = False
            reason = ""

            # Check for white font color
            if font.color and font.color.rgb:
                rgb = font.color.rgb
                if rgb[0] > 250 and rgb[1] > 250 and rgb[2] > 250:
                    is_hidden = True
                    reason = "white_text"

            # Check for tiny font
            if font.size and font.size.pt < 4:
                is_hidden = True
                reason = "tiny_text" if not reason else reason + "+tiny_text"

            # Check for hidden property
            if font.hidden:
                is_hidden = True
                reason = "hidden_property" if not reason else reason + "+hidden_property"

            if is_hidden:
                result.metadata.hidden_text_regions.append({
                    "start": start_pos,
                    "end": end_pos,
                    "reason": reason,
                    "text": text,
                })

            if font.size:
                result.metadata.font_sizes.append({
                    "size": font.size.pt,
                    "text": text[:50],
                    "start": start_pos,
                    "end": end_pos,
                })

            current_pos = end_pos

        all_text_parts.append(para_text + "\n")
        current_pos = len("\n".join(all_text_parts))

    result.raw_text = "\n".join(all_text_parts).strip()
    result.metadata.total_chars = len(result.raw_text)
    result.metadata.visible_chars = result.metadata.total_chars - sum(
        len(r["text"]) for r in result.metadata.hidden_text_regions
    )

    result.sections = _split_sections(result.raw_text)

    return result


def parse_text(text: str, filename: str = "pasted_text") -> ParsedResume:
    """Parse raw text input (fallback for plain text resumes)."""
    result = ParsedResume()
    result.filename = filename
    result.file_type = "text"
    result.raw_text = text.strip()
    result.metadata.total_chars = len(result.raw_text)
    result.metadata.visible_chars = result.metadata.total_chars
    result.sections = _split_sections(result.raw_text)
    return result


def _split_sections(text: str) -> list[ResumeSection]:
    """Split resume text into named sections based on header detection."""
    lines = text.split("\n")
    sections: list[ResumeSection] = []
    current_section_name = "header"
    current_section_lines: list[str] = []
    current_start = 0
    char_pos = 0

    for i, line in enumerate(lines):
        stripped = line.strip()

        # Check if this line is a section header
        matched_section: Optional[str] = None
        for section_name, pattern in SECTION_PATTERNS.items():
            if re.search(pattern, stripped):
                # Heuristic: section headers are usually short lines
                if len(stripped) < 60:
                    matched_section = section_name
                    break

        if matched_section and current_section_lines:
            # Save previous section
            content = "\n".join(current_section_lines).strip()
            if content:
                sections.append(ResumeSection(
                    name=current_section_name,
                    content=content,
                    start_pos=current_start,
                    end_pos=char_pos,
                ))

            current_section_name = matched_section
            current_section_lines = []
            current_start = char_pos
        else:
            current_section_lines.append(line)

        char_pos += len(line) + 1  # +1 for newline

    # Save last section
    if current_section_lines:
        content = "\n".join(current_section_lines).strip()
        if content:
            sections.append(ResumeSection(
                name=current_section_name,
                content=content,
                start_pos=current_start,
                end_pos=char_pos,
            ))

    return sections
