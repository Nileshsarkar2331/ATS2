"use client";

import { useEffect, useRef, useState } from "react";
import MagneticCard from "./MagneticCard";

export default function ScoreCard({ score, breakdown }) {
  const [displayScore, setDisplayScore] = useState(0);
  const [mounted, setMounted] = useState(false);
  const [hovered, setHovered] = useState(false);

  const circumference = 2 * Math.PI * 85;
  const progress = mounted ? ((100 - displayScore) / 100) * circumference : circumference;

  const getScoreColor = (s) => {
    if (s >= 80) return "#06d6a0";
    if (s >= 60) return "#3b82f6";
    if (s >= 40) return "#f59e0b";
    return "#ef4444";
  };

  const getScoreGradientId = (s) => {
    if (s >= 80) return "scoreGreen";
    if (s >= 60) return "scoreBlue";
    if (s >= 40) return "scoreOrange";
    return "scoreRed";
  };

  const getScoreLabel = (s) => {
    if (s >= 90) return "Excellent";
    if (s >= 75) return "Strong";
    if (s >= 60) return "Good";
    if (s >= 45) return "Fair";
    if (s >= 30) return "Below Average";
    return "Needs Work";
  };

  useEffect(() => {
    setMounted(true);
    const target = Math.round(score);
    const duration = 1800;
    const steps = 80;
    const increment = target / steps;
    let current = 0;
    let step = 0;

    const timer = setInterval(() => {
      step++;
      current = Math.min(target, Math.round(increment * step));
      setDisplayScore(current);
      if (step >= steps) {
        setDisplayScore(target);
        clearInterval(timer);
      }
    }, duration / steps);

    return () => clearInterval(timer);
  }, [score]);

  const subScores = [
    { label: "Skill Match",      value: breakdown?.skill_match_score || 0,              weight: "25%", color: "#3b82f6" },
    { label: "Semantic Sim.",    value: breakdown?.semantic_similarity_score || 0,       weight: "30%", color: "#7c3aed" },
    { label: "Experience Auth.", value: breakdown?.experience_authenticity_score || 0,   weight: "20%", color: "#06d6a0" },
    { label: "Anti-Cheat",      value: breakdown?.anti_cheat_score || 0,               weight: "25%",
      color: (breakdown?.anti_cheat_score || 0) >= 80 ? "#06d6a0" : "#ef4444" },
  ];

  const color = getScoreColor(displayScore);
  const gradId = getScoreGradientId(displayScore);

  return (
    <MagneticCard id="score-card" style={{ textAlign: "center" }}>
      <div className="section-header" style={{ justifyContent: "center" }}>
        <div className="section-title">ATS Score</div>
      </div>

      {/* Score Ring */}
      <div
        className="score-ring-container"
        onMouseEnter={() => setHovered(true)}
        onMouseLeave={() => setHovered(false)}
        style={{
          filter: hovered ? `drop-shadow(0 0 22px ${color}55)` : "none",
          transition: "filter 0.4s ease",
        }}
      >
        <svg className="score-ring" viewBox="0 0 200 200">
          <defs>
            <linearGradient id="scoreGreen" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor="#06d6a0" />
              <stop offset="100%" stopColor="#3b82f6" />
            </linearGradient>
            <linearGradient id="scoreBlue" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor="#3b82f6" />
              <stop offset="100%" stopColor="#7c3aed" />
            </linearGradient>
            <linearGradient id="scoreOrange" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor="#f59e0b" />
              <stop offset="100%" stopColor="#ef4444" />
            </linearGradient>
            <linearGradient id="scoreRed" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor="#ef4444" />
              <stop offset="100%" stopColor="#dc2626" />
            </linearGradient>
            {/* Outer pulse ring */}
            <filter id="glow">
              <feGaussianBlur stdDeviation="3" result="coloredBlur" />
              <feMerge>
                <feMergeNode in="coloredBlur" />
                <feMergeNode in="SourceGraphic" />
              </feMerge>
            </filter>
          </defs>

          {/* Background track */}
          <circle className="score-ring-bg" cx="100" cy="100" r="85" />

          {/* Second faint ring for depth */}
          <circle
            cx="100" cy="100" r="75"
            fill="none"
            stroke="rgba(255,255,255,0.025)"
            strokeWidth="1"
          />

          {/* Progress arc */}
          <circle
            className="score-ring-progress"
            cx="100" cy="100" r="85"
            stroke={`url(#${gradId})`}
            strokeDasharray={circumference}
            strokeDashoffset={progress}
            filter="url(#glow)"
          />
        </svg>

        <div className="score-value">
          <div
            className="score-number"
            style={{
              color,
              textShadow: `0 0 24px ${color}66`,
              transition: "color 0.4s ease",
            }}
          >
            {displayScore}
          </div>
          <div className="score-label">{getScoreLabel(displayScore)}</div>
        </div>
      </div>

      {/* Sub-scores */}
      <div className="score-grid">
        {subScores.map((sub, i) => (
          <div
            className="sub-score-card"
            key={sub.label}
            style={{
              animationDelay: `${i * 100 + 400}ms`,
              animation: `fadeInUp 0.5s cubic-bezier(0.22, 1, 0.36, 1) ${i * 100 + 400}ms both`,
            }}
          >
            <div className="sub-score-header">
              <span className="sub-score-title">{sub.label}</span>
              <span className="sub-score-value" style={{ color: sub.color }}>
                {Math.round(sub.value)}
              </span>
            </div>
            <div className="sub-score-bar">
              <div
                className="sub-score-fill"
                style={{
                  width: mounted ? `${sub.value}%` : "0%",
                  background: `linear-gradient(90deg, ${sub.color}99, ${sub.color})`,
                  boxShadow: mounted ? `0 0 8px ${sub.color}55` : "none",
                  transition: `width 1.4s cubic-bezier(0.4, 0, 0.2, 1) ${i * 120}ms`,
                }}
              />
            </div>
            <div className="sub-score-weight">Weight: {sub.weight}</div>
          </div>
        ))}
      </div>
    </MagneticCard>
  );
}
