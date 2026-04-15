"use client";

import { useCallback, useState } from "react";
import { useDropzone } from "react-dropzone";
import ScrollReveal from "./ScrollReveal";

export default function UploadWizard({ onAnalyze, isLoading }) {
  const [file, setFile] = useState(null);
  const [jobDescription, setJobDescription] = useState("");
  const [jdFocused, setJdFocused] = useState(false);

  const onDrop = useCallback((acceptedFiles) => {
    if (acceptedFiles.length > 0) setFile(acceptedFiles[0]);
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      "application/pdf": [".pdf"],
      "application/vnd.openxmlformats-officedocument.wordprocessingml.document": [".docx"],
      "text/plain": [".txt"],
    },
    maxFiles: 1,
    maxSize: 10 * 1024 * 1024,
  });

  const handleSubmit = () => {
    if (file && jobDescription.trim()) onAnalyze(file, jobDescription);
  };

  const removeFile = (e) => {
    e.stopPropagation();
    setFile(null);
  };

  const formatSize = (bytes) => {
    if (bytes < 1024) return bytes + " B";
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + " KB";
    return (bytes / (1024 * 1024)).toFixed(1) + " MB";
  };

  const isReady = file && jobDescription.trim().length > 20;
  const wordCount = jobDescription.split(/\s+/).filter(Boolean).length;

  return (
    <div>
      <div className="upload-steps">
        {/* Step 1 */}
        <ScrollReveal delay={60} direction="left">
          <div className="glass-card step-card" id="upload-resume-step">
            <div className="step-number">1</div>
            <div className="step-label">📄 Upload Resume</div>

            <div
              {...getRootProps()}
              className={`upload-zone ${isDragActive ? "drag-active" : ""}`}
              style={{
                borderColor: file
                  ? "rgba(6,214,160,0.5)"
                  : isDragActive
                  ? "var(--accent-cyan)"
                  : undefined,
                background: file
                  ? "rgba(6,214,160,0.04)"
                  : isDragActive
                  ? "rgba(6,214,160,0.07)"
                  : undefined,
              }}
            >
              <input {...getInputProps()} id="resume-file-input" />

              {!file ? (
                <>
                  {/* Animated upload icon */}
                  <span
                    className="icon"
                    style={{
                      animation: isDragActive
                        ? "orbFloat 1s ease-in-out infinite"
                        : "none",
                      display: "block",
                      marginBottom: 16,
                      fontSize: "3rem",
                    }}
                  >
                    {isDragActive ? "🎯" : "📎"}
                  </span>
                  <h3>
                    {isDragActive ? "Drop it here!" : "Drop your resume here"}
                  </h3>
                  <p style={{ marginTop: 8, color: "var(--text-muted)" }}>
                    PDF, DOCX, or TXT • Max 10MB
                  </p>
                  <p
                    style={{
                      marginTop: 14,
                      fontSize: "0.8rem",
                      color: "var(--accent-purple)",
                      opacity: 0.7,
                    }}
                  >
                    or click to browse
                  </p>
                </>
              ) : (
                <div className="file-preview" onClick={(e) => e.stopPropagation()}>
                  <span className="file-icon" style={{ fontSize: "1.8rem" }}>
                    {file.name.endsWith(".pdf") ? "📕" : "📘"}
                  </span>
                  <div className="file-info">
                    <div className="file-name">{file.name}</div>
                    <div className="file-size">{formatSize(file.size)}</div>
                  </div>
                  {/* Success pulse */}
                  <span style={{ color: "var(--accent-green)", fontSize: "1.2rem", animation: "pulse 2s ease-in-out infinite" }}>
                    ✓
                  </span>
                  <button
                    className="remove-btn"
                    onClick={removeFile}
                    title="Remove file"
                    id="remove-file-btn"
                  >
                    ✕
                  </button>
                </div>
              )}
            </div>
          </div>
        </ScrollReveal>

        {/* Step 2 */}
        <ScrollReveal delay={160} direction="right">
          <div className="glass-card step-card" id="job-description-step">
            <div className="step-number">2</div>
            <div className="step-label">💼 Paste Job Description</div>

            <textarea
              className="jd-textarea"
              placeholder={"Paste the job description here...\n\nInclude the role title, required skills, responsibilities, and qualifications for the best analysis results."}
              value={jobDescription}
              onChange={(e) => setJobDescription(e.target.value)}
              onFocus={() => setJdFocused(true)}
              onBlur={() => setJdFocused(false)}
              id="jd-textarea"
              style={{
                borderColor: jdFocused
                  ? "var(--accent-purple)"
                  : jobDescription.length > 20
                  ? "rgba(6,214,160,0.3)"
                  : undefined,
                boxShadow: jdFocused
                  ? "0 0 0 4px rgba(124,58,237,0.12), 0 0 24px rgba(124,58,237,0.06)"
                  : "none",
              }}
            />

            {/* Word count with progress */}
            <div
              className="text-sm text-muted mt-16"
              style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}
            >
              <span>
                {wordCount > 0 && (
                  <span style={{ color: wordCount >= 40 ? "var(--accent-green)" : "var(--text-muted)" }}>
                    {wordCount} words {wordCount >= 40 ? "✓" : `· need ${Math.max(0, 40 - wordCount)} more`}
                  </span>
                )}
              </span>
              <span style={{ fontSize: "0.7rem", color: "var(--text-muted)" }}>
                {jobDescription.length} chars
              </span>
            </div>

            {/* Thin progress bar */}
            <div
              style={{
                height: 2,
                background: "var(--border-subtle)",
                borderRadius: 2,
                marginTop: 8,
                overflow: "hidden",
              }}
            >
              <div
                style={{
                  height: "100%",
                  width: `${Math.min(100, (wordCount / 80) * 100)}%`,
                  background: wordCount >= 40 ? "var(--accent-green)" : "var(--accent-purple)",
                  borderRadius: 2,
                  transition: "width 0.4s ease, background 0.4s ease",
                }}
              />
            </div>
          </div>
        </ScrollReveal>
      </div>

      {/* Analyze Button */}
      <ScrollReveal delay={260} direction="up">
        <div className="analyze-section">
          <button
            className="btn-primary"
            onClick={handleSubmit}
            disabled={!isReady || isLoading}
            id="analyze-btn"
            style={{
              fontSize: "1.05rem",
              padding: "16px 40px",
              boxShadow: isReady
                ? "0 8px 32px rgba(124,58,237,0.28), 0 0 0 0 rgba(124,58,237,0)"
                : "none",
              transition: "all 0.35s ease",
            }}
          >
            {isLoading ? (
              <>
                <span style={{ width: 20, height: 20, border: "2px solid rgba(255,255,255,0.3)", borderTopColor: "white", borderRadius: "50%", display: "inline-block", animation: "spin 0.8s linear infinite" }} />
                Analyzing...
              </>
            ) : (
              <>🔍 Analyze Resume</>
            )}
          </button>

          {!isReady && (
            <p className="text-sm text-muted mt-16" style={{ animation: "fadeInUp 0.4s ease" }}>
              {!file ? "📎 Upload a resume to continue" : "📝 Add a job description (min 20 characters)"}
            </p>
          )}
        </div>
      </ScrollReveal>
    </div>
  );
}
