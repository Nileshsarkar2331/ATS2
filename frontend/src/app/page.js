"use client";

import { useState, useEffect, useRef } from "react";
import UploadWizard from "@/components/UploadWizard";
import ScoreCard from "@/components/ScoreCard";
import ScoreBreakdown from "@/components/ScoreBreakdown";
import TrustScore from "@/components/TrustScore";
import AdversarialHeatmap from "@/components/AdversarialHeatmap";
import AIExplanation from "@/components/AIExplanation";
import StrengthsWeaknesses from "@/components/StrengthsWeaknesses";
import AnimatedBackground from "@/components/AnimatedBackground";
import ScrollReveal from "@/components/ScrollReveal";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "https://ats-backend-x8c8.onrender.com";

const LOADING_STEPS = [
  "Parsing resume...",
  "Scanning for adversarial patterns...",
  "Computing semantic embeddings...",
  "Matching skills & experience...",
  "Calculating scores...",
  "Generating AI explanations...",
];

// Animated hero text – cycles through words like igloo.inc
const HERO_WORDS = ["Intelligent", "Resilient", "Adversarial-Proof", "AI-Powered"];

export default function HomePage() {
  const [results, setResults] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [loadingStep, setLoadingStep] = useState(0);
  const [wordIndex, setWordIndex] = useState(0);
  const [wordVisible, setWordVisible] = useState(true);

  // Cycle hero words
  useEffect(() => {
    const interval = setInterval(() => {
      setWordVisible(false);
      setTimeout(() => {
        setWordIndex((i) => (i + 1) % HERO_WORDS.length);
        setWordVisible(true);
      }, 350);
    }, 2800);
    return () => clearInterval(interval);
  }, []);

  const handleAnalyze = async (file, jobDescription) => {
    setIsLoading(true);
    setError(null);
    setResults(null);
    setLoadingStep(0);

    const stepInterval = setInterval(() => {
      setLoadingStep((prev) => {
        if (prev < LOADING_STEPS.length - 1) return prev + 1;
        return prev;
      });
    }, 800);

    try {
      const formData = new FormData();
      formData.append("resume", file);
      formData.append("job_description", jobDescription);

      const response = await fetch(`${API_URL}/api/analyze`, {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        const errData = await response.json().catch(() => ({}));
        throw new Error(errData.detail || `Analysis failed (HTTP ${response.status})`);
      }

      const data = await response.json();
      setResults(data);
    } catch (err) {
      console.error("Analysis error:", err);
      setError(err.message || "Failed to connect to the ATS engine. Make sure the backend is running.");
    } finally {
      clearInterval(stepInterval);
      setIsLoading(false);
    }
  };

  const handleReset = () => {
    setResults(null);
    setError(null);
  };

  return (
    <>
      {/* Full-page animated canvas background */}
      <AnimatedBackground />

      <main className="app-container" style={{ position: "relative", zIndex: 1 }}>

        {/* ── Hero Section ─────────────────────────────── */}
        <section className="hero">
          {/* Glowing orb behind hero */}
          <div className="hero-orb" />

          <div className="hero-badge hero-badge-anim">
            <span className="hero-badge-dot" />
            ⚡ AI-Powered Resume Intelligence
          </div>

          <h1 className="hero-title">
            <span
              className="hero-word"
              style={{
                opacity: wordVisible ? 1 : 0,
                transform: wordVisible ? "translateY(0)" : "translateY(-12px)",
                transition: "opacity 0.35s cubic-bezier(0.22,1,0.36,1), transform 0.35s cubic-bezier(0.22,1,0.36,1)",
              }}
            >
              <span className="gradient-text">{HERO_WORDS[wordIndex]}</span>
            </span>
            <br />
            <span className="hero-subtitle-word">ATS Resume Analyzer</span>
          </h1>

          <p className="hero-desc">
            Go beyond keyword matching. Detect manipulation tactics, validate authenticity,
            and get AI-powered insights for every resume.
          </p>

          {/* Stat pills */}
          <div className="hero-stats">
            {[
              { label: "Detection Rate", val: "99.2%" },
              { label: "Semantic Accuracy", val: "94%" },
              { label: "Models Used", val: "7+" },
            ].map((s, i) => (
              <div className="hero-stat-pill" key={s.label} style={{ animationDelay: `${0.4 + i * 0.1}s` }}>
                <span className="hero-stat-val">{s.val}</span>
                <span className="hero-stat-label">{s.label}</span>
              </div>
            ))}
          </div>
        </section>

        {/* ── Upload or Results ─────────────────────────── */}
        {!results && !isLoading && (
          <ScrollReveal delay={100}>
            <UploadWizard onAnalyze={handleAnalyze} isLoading={isLoading} />
          </ScrollReveal>
        )}

        {/* ── Loading State ─────────────────────────────── */}
        {isLoading && (
          <div className="loading-container animate-fade-in">
            <div className="loading-orb">
              <div className="loading-ring" />
              <div className="loading-ring loading-ring-2" />
              <span className="loading-icon">🧠</span>
            </div>
            <div className="loading-text">Analyzing resume with AI...</div>
            <div className="loading-steps">
              {LOADING_STEPS.map((step, i) => (
                <div
                  key={i}
                  className={`loading-step ${
                    i < loadingStep ? "done" : i === loadingStep ? "active" : ""
                  }`}
                  style={{ transitionDelay: `${i * 60}ms` }}
                >
                  <span>
                    {i < loadingStep ? "✅" : i === loadingStep ? "⏳" : "○"}
                  </span>
                  {step}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* ── Error State ───────────────────────────────── */}
        {error && (
          <ScrollReveal>
            <div
              className="glass-card"
              style={{
                maxWidth: 600,
                margin: "32px auto",
                textAlign: "center",
                borderColor: "rgba(239, 68, 68, 0.35)",
                boxShadow: "0 0 40px rgba(239,68,68,0.08)",
              }}
            >
              <div style={{ fontSize: "2rem", marginBottom: 12 }}>❌</div>
              <h3 style={{ marginBottom: 8 }}>Analysis Failed</h3>
              <p className="text-sm text-muted" style={{ marginBottom: 20 }}>
                {error}
              </p>
              <button className="btn-primary" onClick={handleReset}>
                Try Again
              </button>
            </div>
          </ScrollReveal>
        )}

        {/* ── Results Dashboard ─────────────────────────── */}
        {results && (
          <div className="results-grid" id="results-dashboard">

            {/* Reset bar */}
            <ScrollReveal delay={0} direction="up">
              <div className="text-center">
                <button className="btn-secondary" onClick={handleReset} id="new-analysis-btn">
                  ← New Analysis
                </button>
                <span className="text-sm text-muted" style={{ marginLeft: 12 }}>
                  File: {results.filename} • ID: {results.analysis_id}
                </span>
              </div>
            </ScrollReveal>

            {/* Top row */}
            <div className="results-top">
              <ScrollReveal delay={80} direction="up">
                <ScoreCard score={results.final_score} breakdown={results.score_breakdown} />
              </ScrollReveal>
              <ScrollReveal delay={180} direction="up">
                <TrustScore trustScore={results.trust_score} />
              </ScrollReveal>
              <ScrollReveal delay={280} direction="up">
                <ScoreBreakdown breakdown={results.score_breakdown} skillMatches={results.skill_matches} />
              </ScrollReveal>
            </div>

            {/* Strengths & Weaknesses */}
            <ScrollReveal delay={100} direction="up">
              <StrengthsWeaknesses
                strengths={results.explanation?.strengths}
                weaknesses={results.explanation?.weaknesses}
              />
            </ScrollReveal>

            {/* Bottom row */}
            <div className="results-bottom">
              <ScrollReveal delay={80} direction="left">
                <AdversarialHeatmap
                  heatmapSegments={results.heatmap_segments}
                  flags={results.adversarial_flags}
                />
              </ScrollReveal>
              <ScrollReveal delay={200} direction="right">
                <AIExplanation explanation={results.explanation} />
              </ScrollReveal>
            </div>
          </div>
        )}

        {/* Footer */}
        <footer className="site-footer">
          <p>Resilient ATS Engine • Powered by NLP & Sentence Transformers</p>
          <p>Built for intelligent, fair, and adversarial-resilient resume screening</p>
        </footer>
      </main>
    </>
  );
}
