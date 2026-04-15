"use client";

import { useRef, useState, useEffect } from "react";

export default function StrengthsWeaknesses({ strengths, weaknesses }) {
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

  if ((!strengths || strengths.length === 0) && (!weaknesses || weaknesses.length === 0)) return null;

  return (
    <div
      ref={ref}
      className="glass-card"
      id="strengths-weaknesses"
      style={{
        opacity: visible ? 1 : 0,
        transform: visible ? "none" : "translateY(32px)",
        transition: "opacity 0.7s cubic-bezier(0.22,1,0.36,1), transform 0.7s cubic-bezier(0.22,1,0.36,1)",
      }}
    >
      <div className="section-header">
        <div>
          <div className="section-title">⚖️ Strengths & Weaknesses</div>
          <div className="section-subtitle">Key findings from the analysis</div>
        </div>
      </div>

      <div className="sw-grid">
        {/* Strengths */}
        <div className="sw-column">
          <h3>
            <span style={{ color: "var(--accent-green)" }}>✓</span>
            Strengths
            {strengths && (
              <span
                className="text-sm text-muted"
                style={{
                  fontWeight: 400,
                  marginLeft: "auto",
                  background: "rgba(16,185,129,0.12)",
                  border: "1px solid rgba(16,185,129,0.25)",
                  padding: "2px 10px",
                  borderRadius: "var(--radius-full)",
                  color: "var(--accent-green)",
                  fontSize: "0.75rem",
                }}
              >
                {strengths.length}
              </span>
            )}
          </h3>

          {strengths && strengths.length > 0 ? (
            strengths.map((item, i) => (
              <div
                key={i}
                className="sw-item strength-item"
                style={{
                  opacity: visible ? 1 : 0,
                  transform: visible ? "none" : "translateX(-18px)",
                  transition: `opacity 0.55s ease ${i * 70 + 150}ms, transform 0.55s cubic-bezier(0.22,1,0.36,1) ${i * 70 + 150}ms`,
                  borderLeft: "2px solid rgba(16,185,129,0.25)",
                  paddingLeft: 14,
                }}
              >
                <span className="icon">✅</span>
                <span>{item}</span>
              </div>
            ))
          ) : (
            <div className="sw-item" style={{ color: "var(--text-muted)" }}>No notable strengths identified.</div>
          )}
        </div>

        {/* Weaknesses */}
        <div className="sw-column">
          <h3>
            <span style={{ color: "var(--accent-orange)" }}>!</span>
            Weaknesses
            {weaknesses && (
              <span
                className="text-sm text-muted"
                style={{
                  fontWeight: 400,
                  marginLeft: "auto",
                  background: "rgba(245,158,11,0.1)",
                  border: "1px solid rgba(245,158,11,0.25)",
                  padding: "2px 10px",
                  borderRadius: "var(--radius-full)",
                  color: "var(--accent-orange)",
                  fontSize: "0.75rem",
                }}
              >
                {weaknesses.length}
              </span>
            )}
          </h3>

          {weaknesses && weaknesses.length > 0 ? (
            weaknesses.map((item, i) => (
              <div
                key={i}
                className="sw-item weakness-item"
                style={{
                  opacity: visible ? 1 : 0,
                  transform: visible ? "none" : "translateX(18px)",
                  transition: `opacity 0.55s ease ${i * 70 + 200}ms, transform 0.55s cubic-bezier(0.22,1,0.36,1) ${i * 70 + 200}ms`,
                  borderLeft: "2px solid rgba(245,158,11,0.25)",
                  paddingLeft: 14,
                }}
              >
                <span className="icon">⚠️</span>
                <span>{item}</span>
              </div>
            ))
          ) : (
            <div className="sw-item" style={{ color: "var(--text-muted)" }}>No weaknesses found — great resume!</div>
          )}
        </div>
      </div>
    </div>
  );
}
