"""
Adversarial Detection Engine
Detects manipulation tactics in resumes:
- Hidden text (white font, tiny text, hidden properties)
- Keyword stuffing (abnormal word frequency)
- Repeated phrases (copy-paste blocks)
- JD copy-paste (near-identical content from job description)
"""

from __future__ import annotations

import re
import math
from collections import Counter
from typing import Optional
from models.schemas import AdversarialFlag, Severity, HeatmapSegment


class AdversarialDetectionResult:
    """Result of adversarial analysis."""

    def __init__(self):
        self.flags: list[AdversarialFlag] = []
        self.heatmap_segments: list[HeatmapSegment] = []
        self.total_penalty: float = 0.0
        self.anti_cheat_score: float = 100.0  # starts at 100, penalties reduce it


def detect_adversarial(
    raw_text: str,
    formatting_metadata: Optional[dict] = None,
    job_description: str = "",
) -> AdversarialDetectionResult:
    """Run all adversarial detection checks on resume text."""
    result = AdversarialDetectionResult()

    # 1. Hidden text detection
    if formatting_metadata:
        _detect_hidden_text(raw_text, formatting_metadata, result)

    # 2. Keyword stuffing detection
    _detect_keyword_stuffing(raw_text, result)

    # 3. Repeated phrases detection
    _detect_repetition(raw_text, result)

    # 4. JD copy-paste detection
    if job_description:
        _detect_jd_copy_paste(raw_text, job_description, result)

    # Calculate final anti-cheat score
    result.total_penalty = sum(f.penalty for f in result.flags)
    result.anti_cheat_score = max(0.0, 100.0 - result.total_penalty)

    # Generate heatmap segments
    result.heatmap_segments = _generate_heatmap(raw_text, result.flags)

    return result


def _detect_hidden_text(
    text: str, metadata: dict, result: AdversarialDetectionResult
) -> None:
    """Detect hidden text from formatting metadata."""
    hidden_regions = metadata.get("hidden_text_regions", [])

    for region in hidden_regions:
        reason = region.get("reason", "unknown")
        hidden_text = region.get("text", "")

        severity = Severity.HIGH
        penalty = 15.0  # Significant penalty for hidden text

        if "tiny_text" in reason:
            description = f"Extremely small text detected (invisible to readers): '{hidden_text[:40]}...'"
        elif "white_text" in reason:
            description = f"White/invisible text detected (hidden from view): '{hidden_text[:40]}...'"
        elif "hidden_property" in reason:
            description = f"Text with hidden formatting property: '{hidden_text[:40]}...'"
        else:
            description = f"Hidden text detected: '{hidden_text[:40]}...'"

        result.flags.append(AdversarialFlag(
            type="hidden_text",
            severity=severity,
            description=description,
            text_snippet=hidden_text[:100],
            start_pos=region.get("start", 0),
            end_pos=region.get("end", 0),
            penalty=penalty,
        ))


def _detect_keyword_stuffing(text: str, result: AdversarialDetectionResult) -> None:
    """Detect abnormal keyword frequency suggesting stuffing."""
    # Tokenize and count words
    words = re.findall(r"\b[a-zA-Z]{2,}\b", text.lower())
    if len(words) < 20:
        return  # Too short to analyze

    word_counts = Counter(words)
    total_words = len(words)

    # Filter out common stop words
    stop_words = {
        "the", "and", "for", "with", "that", "this", "are", "was", "has",
        "have", "been", "from", "will", "can", "not", "but", "they", "all",
        "their", "which", "when", "were", "there", "would", "each", "make",
        "like", "use", "her", "him", "his", "how", "its", "may", "than",
        "who", "did", "get", "our", "you", "your", "about", "into", "over",
        "such", "also", "other", "new", "used", "using", "work", "working",
    }

    # Calculate frequency statistics for non-stop words
    meaningful_counts = {
        w: c for w, c in word_counts.items()
        if w not in stop_words and len(w) > 2
    }

    if not meaningful_counts:
        return

    frequencies = list(meaningful_counts.values())
    mean_freq = sum(frequencies) / len(frequencies)
    variance = sum((f - mean_freq) ** 2 for f in frequencies) / len(frequencies)
    std_dev = math.sqrt(variance) if variance > 0 else 1.0

    # Flag words that appear > 3 standard deviations above mean
    threshold = mean_freq + 3 * std_dev
    stuffed_words = []

    for word, count in meaningful_counts.items():
        if count > threshold and count > 5:
            # Check if this word frequency is unreasonable for document length
            freq_pct = (count / total_words) * 100
            if freq_pct > 3.0:  # Word appears in >3% of all words
                stuffed_words.append((word, count, freq_pct))

    if stuffed_words:
        for word, count, freq_pct in stuffed_words:
            severity = Severity.MEDIUM if freq_pct < 5 else Severity.HIGH
            penalty = min(10.0, freq_pct * 2)

            # Find positions of stuffed words
            positions = [m.start() for m in re.finditer(
                rf"\b{re.escape(word)}\b", text.lower()
            )]

            result.flags.append(AdversarialFlag(
                type="keyword_stuffing",
                severity=severity,
                description=(
                    f"Keyword '{word}' appears {count} times ({freq_pct:.1f}% of text). "
                    f"This is {count / mean_freq:.1f}x the average word frequency."
                ),
                text_snippet=word,
                start_pos=positions[0] if positions else 0,
                end_pos=positions[-1] + len(word) if positions else 0,
                penalty=penalty,
            ))


def _detect_repetition(text: str, result: AdversarialDetectionResult) -> None:
    """Detect copy-pasted or repeated blocks of text."""
    # Split into sentences
    sentences = re.split(r"[.!?\n]+", text)
    sentences = [s.strip().lower() for s in sentences if len(s.strip()) > 20]

    if len(sentences) < 3:
        return

    # Check for duplicate sentences
    sentence_counts = Counter(sentences)
    duplicates = {s: c for s, c in sentence_counts.items() if c > 1}

    for sentence, count in duplicates.items():
        severity = Severity.MEDIUM if count <= 3 else Severity.HIGH
        penalty = min(8.0, count * 3.0)

        # Find first occurrence position
        pos = text.lower().find(sentence)

        result.flags.append(AdversarialFlag(
            type="repetition",
            severity=severity,
            description=(
                f"Phrase repeated {count} times: '{sentence[:60]}...'"
            ),
            text_snippet=sentence[:100],
            start_pos=max(0, pos),
            end_pos=max(0, pos + len(sentence)) if pos >= 0 else 0,
            penalty=penalty,
        ))

    # Check for repeated n-grams (tri-grams)
    words = text.lower().split()
    if len(words) < 10:
        return

    trigrams = [" ".join(words[i:i + 3]) for i in range(len(words) - 2)]
    trigram_counts = Counter(trigrams)

    # Flag trigrams appearing abnormally often (> 5 times)
    suspicious_trigrams = {
        tg: c for tg, c in trigram_counts.items()
        if c > 5 and len(tg) > 10
    }

    if len(suspicious_trigrams) > 3:
        total_suspicious = sum(suspicious_trigrams.values())
        top_examples = sorted(
            suspicious_trigrams.items(), key=lambda x: -x[1]
        )[:3]
        examples_str = ", ".join(f"'{tg}' ({c}x)" for tg, c in top_examples)

        result.flags.append(AdversarialFlag(
            type="repetition",
            severity=Severity.MEDIUM,
            description=(
                f"High phrase repetition detected ({total_suspicious} repeated trigrams). "
                f"Examples: {examples_str}"
            ),
            text_snippet=top_examples[0][0] if top_examples else "",
            penalty=5.0,
        ))


def _detect_jd_copy_paste(
    resume_text: str, jd_text: str, result: AdversarialDetectionResult
) -> None:
    """Detect if resume contains copy-pasted content from the job description."""
    # Use sliding window comparison (word-level)
    resume_words = resume_text.lower().split()
    jd_words = jd_text.lower().split()

    if len(jd_words) < 10 or len(resume_words) < 10:
        return

    window_size = 8  # Check 8-word windows
    jd_windows = set()

    for i in range(len(jd_words) - window_size + 1):
        window = " ".join(jd_words[i:i + window_size])
        jd_windows.add(window)

    # Check resume windows against JD windows
    matches = []
    for i in range(len(resume_words) - window_size + 1):
        window = " ".join(resume_words[i:i + window_size])
        if window in jd_windows:
            # Find position in original text
            pos = resume_text.lower().find(window)
            matches.append({
                "text": window,
                "pos": max(0, pos),
            })

    if len(matches) > 2:
        # Merge adjacent matches
        unique_matches = _merge_overlapping(matches)
        copy_pct = (len(unique_matches) * window_size / len(resume_words)) * 100

        if copy_pct > 5.0:
            severity = Severity.MEDIUM if copy_pct < 15 else Severity.HIGH
            penalty = min(15.0, copy_pct)

            result.flags.append(AdversarialFlag(
                type="jd_copy_paste",
                severity=severity,
                description=(
                    f"~{copy_pct:.0f}% of resume appears to be directly copied from the "
                    f"job description ({len(unique_matches)} matching segments found)."
                ),
                text_snippet=unique_matches[0]["text"][:100] if unique_matches else "",
                start_pos=unique_matches[0]["pos"] if unique_matches else 0,
                end_pos=(
                    unique_matches[-1]["pos"] + len(unique_matches[-1]["text"])
                    if unique_matches else 0
                ),
                penalty=penalty,
            ))


def _merge_overlapping(matches: list[dict]) -> list[dict]:
    """Merge overlapping text matches."""
    if not matches:
        return []

    sorted_matches = sorted(matches, key=lambda m: m["pos"])
    merged = [sorted_matches[0]]

    for match in sorted_matches[1:]:
        last = merged[-1]
        last_end = last["pos"] + len(last["text"])
        if match["pos"] <= last_end + 5:  # Allow small gaps
            # Extend the last match
            new_end = match["pos"] + len(match["text"])
            if new_end > last_end:
                last["text"] = last["text"] + match["text"][last_end - match["pos"]:]
        else:
            merged.append(match)

    return merged


def _generate_heatmap(
    text: str, flags: list[AdversarialFlag]
) -> list[HeatmapSegment]:
    """Generate character-level heatmap segments for visualization."""
    if not text:
        return []

    # Create a suspicion map
    char_suspicion = [0.0] * len(text)
    char_flags: list[Optional[str]] = [None] * len(text)
    char_tooltips: list[str] = [""] * len(text)

    severity_to_level = {
        Severity.LOW: 0.3,
        Severity.MEDIUM: 0.6,
        Severity.HIGH: 0.85,
        Severity.CRITICAL: 1.0,
    }

    for flag in flags:
        start = max(0, flag.start_pos)
        end = min(len(text), flag.end_pos) if flag.end_pos > 0 else start

        if start == end and flag.text_snippet:
            # Try to find the snippet in the text
            pos = text.lower().find(flag.text_snippet.lower())
            if pos >= 0:
                start = pos
                end = pos + len(flag.text_snippet)

        level = severity_to_level.get(flag.severity, 0.3)

        for i in range(start, min(end, len(text))):
            char_suspicion[i] = max(char_suspicion[i], level)
            char_flags[i] = flag.type
            char_tooltips[i] = flag.description

    # Compress into segments (group adjacent chars with same suspicion level)
    segments: list[HeatmapSegment] = []
    if not text:
        return segments

    # Use a window approach to create manageable segments
    chunk_size = 100  # Characters per segment max
    i = 0
    while i < len(text):
        end = min(i + chunk_size, len(text))

        # Try to break at a word boundary
        if end < len(text):
            space_pos = text.rfind(" ", i, end)
            if space_pos > i:
                end = space_pos + 1

        chunk_text = text[i:end]
        chunk_suspicion = char_suspicion[i:end]
        avg_suspicion = sum(chunk_suspicion) / len(chunk_suspicion) if chunk_suspicion else 0

        # Get the dominant flag type for this chunk
        chunk_flag_types = [f for f in char_flags[i:end] if f]
        dominant_flag = max(set(chunk_flag_types), key=chunk_flag_types.count) if chunk_flag_types else None

        # Get tooltip
        chunk_tooltips = [t for t in char_tooltips[i:end] if t]
        tooltip = chunk_tooltips[0] if chunk_tooltips else ""

        segments.append(HeatmapSegment(
            text=chunk_text,
            suspicion_level=round(avg_suspicion, 2),
            flag_type=dominant_flag,
            tooltip=tooltip,
        ))

        i = end

    return segments
