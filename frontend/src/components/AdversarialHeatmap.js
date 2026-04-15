"use client";

import { useState, useEffect, useRef } from "react";
import MagneticCard from "./MagneticCard";

export default function AdversarialHeatmap({ heatmapSegments, flags }) {
  const [hoveredSegment, setHoveredSegment] = useState(null);
  const [viewMode, setViewMode] = useState("detection");
  const [visible, setVisible] = useState(false);
  const ref = useRef(null);

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => { if (entry.isIntersecting) { setVisible(true); observer.disconnect(); } },
      { threshold: 0.08 }
    );
    if (ref.current) observer.observe(ref.current);
    return () => observer.disconnect();
  }, []);

  if (!heatmapSegments || heatmapSegments.length === 0) return null;

  const getSuspicionColor = (level) => {
    if (level <= 0)   return "transparent";
    if (level < 0.3)  return "rgba(6, 214, 160, 0.15)";
    if (level < 0.6)  return "rgba(245, 158, 11, 0.22)";
    if (level < 0.85) return "rgba(239, 68, 68, 0.28)";
    return "rgba(239, 68, 68, 0.45)";
  };

  const flagSummary = {};
  (flags || []).forEach((f) => {
    flagSummary[f.type] = (flagSummary[f.type] || 0) + 1;
  });

  const flagLabels = {
    hidden_text:      "🔍 Hidden Text",
    keyword_stuffing: "📝 Keyword Stuffing",
    repetition:       "🔁 Repetition",
    jd_copy_paste:    "📋 JD Copy-Paste",
  };

  const totalFlags = Object.values(flagSummary).reduce((a, b) => a + b, 0);
  const riskColor  = totalFlags === 0 ? "#06d6a0" : totalFlags <= 2 ? "#f59e0b" : "#ef4444";

  return (
    <div ref={ref}>
      <MagneticCard id="adversarial-heatmap">
        {/* Header */}
        <div className="section-header">
          <div style={{ flex: 1 }}>
            <div className="section-title">🔥 Adversarial Detection Heatmap</div>
            <div className="section-subtitle">Suspicious content highlighted in resume text</div>
          </div>
          {/* Risk indicator */}
          <div
            style={{
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
              padding: "8px 14px",
              background: `${riskColor}12`,
              border: `1px solid ${riskColor}33`,
              borderRadius: "var(--radius-md)",
              minWidth: 72,
            }}
          >
            <span style={{ fontSize: "1.3rem", fontWeight: 800, color: riskColor, lineHeight: 1 }}>
              {totalFlags}
            </span>
            <span style={{ fontSize: "0.65rem", color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "0.06em" }}>
              Flags
            </span>
          </div>
        </div>

        {/* Flag badges with entrance animation */}
        {Object.keys(flagSummary).length > 0 && (
          <div style={{ display: "flex", gap: 8, flexWrap: "wrap", marginBottom: 16 }}>
            {Object.entries(flagSummary).map(([type, count], i) => (
              <span
                key={type}
                className={`flag-badge ${count > 2 ? "high" : "medium"}`}
                style={{
                  opacity: visible ? 1 : 0,
                  transform: visible ? "none" : "translateY(8px)",
                  transition: `opacity 0.45s ease ${i * 80 + 100}ms, transform 0.45s cubic-bezier(0.22,1,0.36,1) ${i * 80 + 100}ms`,
                }}
              >
                {flagLabels[type] || type}: {count}
              </span>
            ))}
          </div>
        )}

        {/* View toggle */}
        <div style={{ display: "flex", gap: 8, marginBottom: 16 }}>
          {["detection", "clean"].map((mode) => (
            <button
              key={mode}
              className={viewMode === mode ? "btn-primary" : "btn-secondary"}
              onClick={() => setViewMode(mode)}
              style={{ padding: "6px 16px", fontSize: "0.8rem" }}
            >
              {mode === "detection" ? "🔍 Detection View" : "📄 Clean View"}
            </button>
          ))}
        </div>

        {/* Legend */}
        {viewMode === "detection" && (
          <div style={{ display: "flex", gap: 16, marginBottom: 16, fontSize: "0.75rem", color: "var(--text-muted)", flexWrap: "wrap" }}>
            {[
              { label: "Clean",      bg: "rgba(6,214,160,0.2)" },
              { label: "Moderate",   bg: "rgba(245,158,11,0.3)" },
              { label: "Suspicious", bg: "rgba(239,68,68,0.4)" },
            ].map((l) => (
              <span key={l.label} style={{ display: "flex", alignItems: "center", gap: 5 }}>
                <span style={{ width: 12, height: 12, borderRadius: 2, background: l.bg, display: "inline-block" }} />
                {l.label}
              </span>
            ))}
          </div>
        )}

        {/* Heatmap text */}
        <div className="heatmap-container">
          {heatmapSegments.map((segment, i) => (
            <span
              key={i}
              className="heatmap-segment"
              style={{
                backgroundColor: viewMode === "detection" ? getSuspicionColor(segment.suspicion_level) : "transparent",
                opacity: visible ? 1 : 0,
                transition: `opacity 0.4s ease ${Math.min(i * 8, 400)}ms, background-color 0.3s ease`,
                cursor: segment.suspicion_level > 0 ? "pointer" : "default",
              }}
              onMouseEnter={() => segment.suspicion_level > 0 && setHoveredSegment(i)}
              onMouseLeave={() => setHoveredSegment(null)}
            >
              {segment.text}
              {hoveredSegment === i && segment.tooltip && (
                <span
                  className="heatmap-tooltip"
                  style={{ animation: "fadeInDown 0.2s ease" }}
                >
                  {segment.tooltip}
                </span>
              )}
            </span>
          ))}
        </div>

        {/* Clean notice */}
        {Object.keys(flagSummary).length === 0 && (
          <div
            className="text-center mt-16"
            style={{
              color: "var(--accent-green)",
              animation: "fadeInUp 0.6s ease 0.3s both",
              padding: "12px",
              background: "rgba(6,214,160,0.06)",
              borderRadius: "var(--radius-md)",
              border: "1px solid rgba(6,214,160,0.15)",
            }}
          >
            ✅ No adversarial patterns detected — resume appears clean!
          </div>
        )}
      </MagneticCard>
    </div>
  );
}
