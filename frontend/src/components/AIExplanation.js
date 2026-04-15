"use client";

import { useRef, useState, useEffect } from "react";
import MagneticCard from "./MagneticCard";

export default function AIExplanation({ explanation }) {
  const ref = useRef(null);
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => { if (entry.isIntersecting) { setVisible(true); observer.disconnect(); } },
      { threshold: 0.1 }
    );
    if (ref.current) observer.observe(ref.current);
    return () => observer.disconnect();
  }, []);

  if (!explanation) return null;
  const { summary, suggestions } = explanation;

  return (
    <div ref={ref}>
      <MagneticCard id="ai-explanation">
        <div className="section-header">
          <div>
            <div className="section-title">🧠 AI Analysis</div>
            <div className="section-subtitle">Why you scored this — with improvement suggestions</div>
          </div>
        </div>

        {/* Summary block with typewriter border */}
        {summary && (
          <div
            style={{
              padding: "18px 22px",
              background: "rgba(124,58,237,0.06)",
              border: "1px solid rgba(124,58,237,0.18)",
              borderRadius: "var(--radius-md)",
              marginBottom: 24,
              fontSize: "0.95rem",
              lineHeight: 1.75,
              color: "var(--text-primary)",
              position: "relative",
              overflow: "hidden",
              opacity: visible ? 1 : 0,
              transform: visible ? "none" : "translateY(14px)",
              transition: "opacity 0.65s ease, transform 0.65s cubic-bezier(0.22,1,0.36,1)",
            }}
          >
            {/* Animated left accent bar */}
            <div
              style={{
                position: "absolute",
                top: 0,
                left: 0,
                width: 3,
                height: visible ? "100%" : "0%",
                background: "var(--gradient-primary)",
                transition: "height 0.9s cubic-bezier(0.22,1,0.36,1) 0.2s",
                borderRadius: "2px 0 0 2px",
              }}
            />
            <span style={{ paddingLeft: 8 }}>{summary}</span>
          </div>
        )}

        {/* Suggestions with spring stagger */}
        {suggestions && suggestions.length > 0 && (
          <div>
            <h4
              style={{
                fontSize: "0.95rem",
                fontWeight: 700,
                marginBottom: 16,
                display: "flex",
                alignItems: "center",
                gap: 8,
                opacity: visible ? 1 : 0,
                transition: "opacity 0.5s ease 0.3s",
              }}
            >
              💡 How to Improve
            </h4>

            <div className="suggestion-list">
              {suggestions.map((suggestion, i) => (
                <div
                  key={i}
                  className="suggestion-item"
                  style={{
                    opacity: visible ? 1 : 0,
                    transform: visible ? "translateX(0)" : "translateX(24px)",
                    transition: `opacity 0.55s ease ${i * 90 + 350}ms, transform 0.55s cubic-bezier(0.34,1.56,0.64,1) ${i * 90 + 350}ms`,
                  }}
                >
                  <span
                    className="suggestion-number"
                    style={{
                      background: `conic-gradient(from ${i * 60}deg, #7c3aed, #06d6a0, #7c3aed)`,
                      animation: "gradientShift 4s ease infinite",
                    }}
                  >
                    {i + 1}
                  </span>
                  <span className="suggestion-text">{suggestion}</span>
                </div>
              ))}
            </div>
          </div>
        )}
      </MagneticCard>
    </div>
  );
}
