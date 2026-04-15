"use client";

import { useEffect, useRef, useState } from "react";

export default function ScrollReveal({
  children,
  delay = 0,
  direction = "up", // "up" | "left" | "right" | "scale"
  className = "",
  threshold = 0.12,
}) {
  const ref = useRef(null);
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setVisible(true);
          observer.unobserve(entry.target);
        }
      },
      { threshold }
    );
    const el = ref.current;
    if (el) observer.observe(el);
    return () => el && observer.unobserve(el);
  }, [threshold]);

  const getInitial = () => {
    switch (direction) {
      case "left":  return "translateX(-40px)";
      case "right": return "translateX(40px)";
      case "scale": return "scale(0.88)";
      default:      return "translateY(36px)";
    }
  };

  return (
    <div
      ref={ref}
      className={className}
      style={{
        opacity: visible ? 1 : 0,
        transform: visible ? "none" : getInitial(),
        transition: `opacity 0.72s cubic-bezier(0.22, 1, 0.36, 1) ${delay}ms, transform 0.72s cubic-bezier(0.22, 1, 0.36, 1) ${delay}ms`,
        willChange: "opacity, transform",
      }}
    >
      {children}
    </div>
  );
}
