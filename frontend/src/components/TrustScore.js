"use client";

import { useEffect, useState } from "react";
import MagneticCard from "./MagneticCard";

export default function TrustScore({ trustScore }) {
  const [showDetails, setShowDetails] = useState(false);
  const [displayScore, setDisplayScore] = useState(0);

  const score              = trustScore?.score ?? 0;
  const level              = trustScore?.level;
  const content_integrity  = trustScore?.content_integrity ?? 0;
  const consistency        = trustScore?.consistency ?? 0;
  const originality        = trustScore?.originality ?? 0;
  const explanation        = trustScore?.explanation;

  // Animated counter — all hooks before any early return
  useEffect(() => {
    if (!trustScore) return;
    const target = Math.round(score);
    const steps = 60;
    const inc = target / steps;
    let step = 0;
    const timer = setInterval(() => {
      step++;
      setDisplayScore(Math.min(target, Math.round(inc * step)));
      if (step >= steps) { setDisplayScore(target); clearInterval(timer); }
    }, 1600 / steps);
    return () => clearInterval(timer);
  }, [score, trustScore]);

  if (!trustScore) return null;

  const levelConfig = {
    highly_trusted:     { color: "#06d6a0", bgColor: "rgba(6,214,160,0.1)",  borderColor: "rgba(6,214,160,0.3)",  icon: "🛡️", label: "Highly Trusted" },
    trusted:            { color: "#3b82f6", bgColor: "rgba(59,130,246,0.1)", borderColor: "rgba(59,130,246,0.3)", icon: "✅", label: "Trusted" },
    review_recommended: { color: "#f59e0b", bgColor: "rgba(245,158,11,0.1)", borderColor: "rgba(245,158,11,0.3)", icon: "⚠️", label: "Review Recommended" },
    flagged:            { color: "#ef4444", bgColor: "rgba(239,68,68,0.1)",  borderColor: "rgba(239,68,68,0.3)",  icon: "🚨", label: "Flagged" },
  };

  const config = levelConfig[level] || levelConfig.review_recommended;

  const metrics = [
    { label: "Integrity",   value: content_integrity },
    { label: "Consistency", value: consistency },
    { label: "Originality", value: originality },
  ];

  const arcCircumference = 2 * Math.PI * 20;

  return (
    <MagneticCard id="trust-score">
      <div className="section-header" style={{ justifyContent: "center" }}>
        <div className="section-title">🛡️ Trust Score</div>
      </div>

      <div className="trust-badge-container">
        {/* Floating animated shield */}
        <div
          className="trust-shield"
          style={{ animation: "orbFloat 6s ease-in-out infinite" }}
        >
          <div
            className="trust-shield-glow"
            style={{
              background: config.color,
              animation: "pulse 3s ease-in-out infinite",
            }}
          />
          <div className="trust-shield-icon" style={{ fontSize: "3.2rem" }}>
            {config.icon}
          </div>
        </div>

        {/* Animated score number with glow */}
        <div
          style={{
            fontSize: "2.8rem",
            fontWeight: 900,
            color: config.color,
            lineHeight: 1,
            textShadow: `0 0 28px ${config.color}55`,
            transition: "color 0.4s ease",
          }}
        >
          {displayScore}
        </div>

        {/* Level badge */}
        <span
          style={{
            padding: "5px 18px",
            background: config.bgColor,
            border: `1px solid ${config.borderColor}`,
            borderRadius: "var(--radius-full)",
            color: config.color,
            fontSize: "0.8rem",
            fontWeight: 700,
            boxShadow: `0 0 14px ${config.color}22`,
            animation: "fadeInUp 0.6s cubic-bezier(0.22,1,0.36,1) 0.3s both",
          }}
        >
          {config.label}
        </span>

        {/* Mini radial metric arcs */}
        <div className="trust-breakdown">
          {metrics.map((m, i) => (
            <div
              className="trust-metric"
              key={m.label}
              style={{
                animation: `fadeInUp 0.55s cubic-bezier(0.22,1,0.36,1) ${0.4 + i * 0.1}s both`,
              }}
            >
              <svg width="52" height="52" viewBox="0 0 52 52" style={{ marginBottom: 4 }}>
                <circle
                  cx="26" cy="26" r="20"
                  fill="none"
                  stroke="rgba(148,163,184,0.12)"
                  strokeWidth="4"
                />
                <circle
                  cx="26" cy="26" r="20"
                  fill="none"
                  stroke={m.value >= 80 ? "#06d6a0" : "#f59e0b"}
                  strokeWidth="4"
                  strokeLinecap="round"
                  strokeDasharray={arcCircumference}
                  strokeDashoffset={arcCircumference * (1 - m.value / 100)}
                  transform="rotate(-90 26 26)"
                  style={{
                    transition: "stroke-dashoffset 1.4s cubic-bezier(0.4,0,0.2,1)",
                  }}
                />
                <text
                  x="26" y="30"
                  textAnchor="middle"
                  fontSize="11"
                  fontWeight="700"
                  fill={m.value >= 80 ? "#06d6a0" : "#f59e0b"}
                >
                  {Math.round(m.value)}
                </text>
              </svg>
              <span className="trust-metric-label">{m.label}</span>
            </div>
          ))}
        </div>

        {/* Smooth expand/collapse explanation */}
        {explanation && (
          <div>
            <button
              className="btn-secondary"
              onClick={() => setShowDetails(!showDetails)}
              style={{ fontSize: "0.8rem", marginTop: "10px" }}
            >
              {showDetails ? "Hide Details ▲" : "Show Details ▼"}
            </button>
            <div
              style={{
                maxHeight: showDetails ? "200px" : "0",
                overflow: "hidden",
                transition: "max-height 0.45s cubic-bezier(0.22,1,0.36,1)",
              }}
            >
              <p
                className="text-sm"
                style={{
                  color: "var(--text-secondary)",
                  marginTop: 14,
                  lineHeight: 1.65,
                  maxWidth: 300,
                }}
              >
                {explanation}
              </p>
            </div>
          </div>
        )}
      </div>
    </MagneticCard>
  );
}
