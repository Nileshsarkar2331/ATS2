"use client";

import { useRef } from "react";

export default function MagneticCard({ children, className = "", style = {}, id }) {
  const cardRef = useRef(null);
  const glowRef = useRef(null);

  const handleMouseMove = (e) => {
    const card = cardRef.current;
    const glow = glowRef.current;
    if (!card) return;

    const rect = card.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    const cx = rect.width / 2;
    const cy = rect.height / 2;

    const tiltX = ((y - cy) / cy) * 6;
    const tiltY = ((cx - x) / cx) * 6;

    card.style.transform = `perspective(800px) rotateX(${tiltX}deg) rotateY(${tiltY}deg) translateZ(4px)`;

    if (glow) {
      glow.style.background = `radial-gradient(280px circle at ${x}px ${y}px, rgba(124, 58, 237, 0.13), transparent 65%)`;
    }
  };

  const handleMouseLeave = () => {
    const card = cardRef.current;
    const glow = glowRef.current;
    if (card) {
      card.style.transform = "perspective(800px) rotateX(0deg) rotateY(0deg) translateZ(0)";
    }
    if (glow) glow.style.background = "none";
  };

  return (
    <div
      ref={cardRef}
      id={id}
      className={`glass-card magnetic-card ${className}`}
      style={{
        transition: "transform 0.18s ease, box-shadow 0.18s ease",
        ...style,
      }}
      onMouseMove={handleMouseMove}
      onMouseLeave={handleMouseLeave}
    >
      {/* Glow spotlight */}
      <div
        ref={glowRef}
        style={{
          position: "absolute",
          inset: 0,
          borderRadius: "inherit",
          pointerEvents: "none",
          zIndex: 0,
          transition: "background 0.1s ease",
        }}
      />
      <div style={{ position: "relative", zIndex: 1 }}>{children}</div>
    </div>
  );
}
