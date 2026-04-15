"use client";

import { useEffect, useRef, useState } from "react";
import MagneticCard from "./MagneticCard";
import {
  Radar, RadarChart, PolarGrid, PolarAngleAxis,
  PolarRadiusAxis, ResponsiveContainer, Tooltip,
} from "recharts";

export default function ScoreBreakdown({ breakdown, skillMatches }) {
  const ref = useRef(null);
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    if (!breakdown) return;
    const observer = new IntersectionObserver(
      ([entry]) => { if (entry.isIntersecting) { setVisible(true); observer.disconnect(); } },
      { threshold: 0.1 }
    );
    if (ref.current) observer.observe(ref.current);
    return () => observer.disconnect();
  }, [breakdown]);

  if (!breakdown) return null;

  const radarData = [
    { subject: "Skill Match",  value: breakdown.skill_match_score,             fullMark: 100 },
    { subject: "Semantic Fit", value: breakdown.semantic_similarity_score,     fullMark: 100 },
    { subject: "Experience",   value: breakdown.experience_authenticity_score, fullMark: 100 },
    { subject: "Anti-Cheat",   value: breakdown.anti_cheat_score,              fullMark: 100 },
  ];

  const matched  = skillMatches?.filter((s) =>  s.found) || [];
  const missing  = skillMatches?.filter((s) => !s.found) || [];
  const evidenced = matched.filter((s) => s.has_project_evidence);

  const allPills = [
    ...evidenced.map((s) => ({ skill: s.skill, type: "evidenced" })),
    ...matched.filter((s) => !s.has_project_evidence).map((s) => ({ skill: s.skill, type: "matched" })),
    ...missing.map((s) => ({ skill: s.skill, type: "missing" })),
  ];

  return (
    <div ref={ref}>
      <MagneticCard id="score-breakdown">
        <div className="section-header">
          <div>
            <div className="section-title">📊 Score Breakdown</div>
            <div className="section-subtitle">Multi-factor analysis radar</div>
          </div>
        </div>

        {/* Animated radar chart */}
        <div
          className="chart-container"
          style={{
            opacity: visible ? 1 : 0,
            transform: visible ? "scale(1)" : "scale(0.88)",
            transition: "opacity 0.75s ease, transform 0.75s cubic-bezier(0.34,1.56,0.64,1)",
          }}
        >
          <ResponsiveContainer width="100%" height="100%">
            <RadarChart data={radarData} cx="50%" cy="50%" outerRadius="70%">
              <PolarGrid stroke="rgba(148,163,184,0.12)" />
              <PolarAngleAxis
                dataKey="subject"
                tick={{ fill: "#94a3b8", fontSize: 12, fontWeight: 500 }}
              />
              <PolarRadiusAxis
                angle={30}
                domain={[0, 100]}
                tick={{ fill: "#64748b", fontSize: 10 }}
              />
              <Tooltip
                contentStyle={{
                  background: "rgba(17,24,39,0.95)",
                  border: "1px solid rgba(124,58,237,0.35)",
                  borderRadius: 10,
                  color: "#f1f5f9",
                  fontSize: "0.85rem",
                  backdropFilter: "blur(12px)",
                }}
                formatter={(value) => [`${Math.round(value)}/100`, "Score"]}
              />
              <Radar
                name="Score"
                dataKey="value"
                stroke="#7c3aed"
                fill="url(#radarGrad)"
                fillOpacity={0.7}
                strokeWidth={2.5}
                dot={{ fill: "#7c3aed", r: 4 }}
                activeDot={{ fill: "#06d6a0", r: 5 }}
              />
              {/* gradient fill */}
              <defs>
                <radialGradient id="radarGrad" cx="50%" cy="50%" r="50%">
                  <stop offset="0%" stopColor="#06d6a0" stopOpacity={0.5} />
                  <stop offset="100%" stopColor="#7c3aed" stopOpacity={0.15} />
                </radialGradient>
              </defs>
            </RadarChart>
          </ResponsiveContainer>
        </div>

        {/* Skill pills with staggered entrance */}
        {skillMatches && skillMatches.length > 0 && (
          <div>
            <h4
              className="text-sm font-semibold mb-16"
              style={{
                color: "var(--text-secondary)",
                opacity: visible ? 1 : 0,
                transition: "opacity 0.55s ease 0.3s",
                display: "flex",
                alignItems: "center",
                justifyContent: "space-between",
              }}
            >
              Skill Coverage
              <span style={{ color: "var(--accent-cyan)", fontWeight: 700 }}>
                {matched.length}/{skillMatches.length}
              </span>
            </h4>

            <div className="skill-pills">
              {allPills.map(({ skill, type }, i) => (
                <span
                  key={`${skill}-${type}`}
                  className={`skill-pill ${type}`}
                  title={
                    type === "evidenced" ? "Found with project evidence"
                      : type === "matched" ? "Found in resume"
                        : "Not found in resume"
                  }
                  style={{
                    animationDelay: `${i * 55 + 200}ms`,
                    opacity: visible ? 1 : 0,
                    transform: visible ? "none" : "translateY(10px) scale(0.9)",
                    transition: `opacity 0.45s ease ${i * 55 + 200}ms, transform 0.45s cubic-bezier(0.34,1.56,0.64,1) ${i * 55 + 200}ms`,
                  }}
                >
                  {type === "missing" ? "✕" : "✓"} {skill}
                </span>
              ))}
            </div>

            {evidenced.length > 0 && (
              <p
                className="text-sm text-muted mt-16"
                style={{
                  opacity: visible ? 1 : 0,
                  transition: "opacity 0.5s ease 0.6s",
                  padding: "10px 14px",
                  background: "rgba(6,214,160,0.05)",
                  border: "1px solid rgba(6,214,160,0.12)",
                  borderRadius: "var(--radius-sm)",
                }}
              >
                💡 <strong style={{ color: "var(--accent-cyan)" }}>{evidenced.length} skill(s)</strong> have supporting project evidence
              </p>
            )}
          </div>
        )}
      </MagneticCard>
    </div>
  );
}
