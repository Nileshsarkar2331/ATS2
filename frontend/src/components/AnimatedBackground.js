"use client";

import { useEffect, useRef } from "react";

export default function AnimatedBackground() {
  const canvasRef = useRef(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");

    let width = (canvas.width = window.innerWidth);
    let height = (canvas.height = window.innerHeight * 2);
    let animFrame;
    let t = 0;

    const particles = Array.from({ length: 38 }, () => ({
      x: Math.random() * width,
      y: Math.random() * height,
      r: Math.random() * 2 + 0.5,
      speed: Math.random() * 0.4 + 0.1,
      angle: Math.random() * Math.PI * 2,
      drift: (Math.random() - 0.5) * 0.01,
      opacity: Math.random() * 0.5 + 0.2,
    }));

    function drawMesh(t) {
      // Animated gradient orbs
      const grad1 = ctx.createRadialGradient(
        width * 0.2 + Math.sin(t * 0.0008) * 100,
        height * 0.1 + Math.cos(t * 0.0006) * 80,
        0,
        width * 0.2,
        height * 0.1,
        width * 0.55
      );
      grad1.addColorStop(0, "rgba(124, 58, 237, 0.13)");
      grad1.addColorStop(1, "transparent");

      const grad2 = ctx.createRadialGradient(
        width * 0.8 + Math.cos(t * 0.0007) * 120,
        height * 0.25 + Math.sin(t * 0.0009) * 90,
        0,
        width * 0.8,
        height * 0.25,
        width * 0.5
      );
      grad2.addColorStop(0, "rgba(6, 214, 160, 0.10)");
      grad2.addColorStop(1, "transparent");

      const grad3 = ctx.createRadialGradient(
        width * 0.5 + Math.sin(t * 0.0005) * 80,
        height * 0.5 + Math.cos(t * 0.0007) * 60,
        0,
        width * 0.5,
        height * 0.5,
        width * 0.4
      );
      grad3.addColorStop(0, "rgba(59, 130, 246, 0.08)");
      grad3.addColorStop(1, "transparent");

      ctx.clearRect(0, 0, width, height);
      ctx.fillStyle = grad1;
      ctx.fillRect(0, 0, width, height);
      ctx.fillStyle = grad2;
      ctx.fillRect(0, 0, width, height);
      ctx.fillStyle = grad3;
      ctx.fillRect(0, 0, width, height);
    }

    function drawParticles() {
      particles.forEach((p) => {
        ctx.beginPath();
        ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(148, 163, 184, ${p.opacity})`;
        ctx.fill();

        // Move
        p.angle += p.drift;
        p.x += Math.cos(p.angle) * p.speed;
        p.y += Math.sin(p.angle) * p.speed;

        // Wrap around
        if (p.x < 0) p.x = width;
        if (p.x > width) p.x = 0;
        if (p.y < 0) p.y = height;
        if (p.y > height) p.y = 0;
      });
    }

    function drawConnections() {
      for (let i = 0; i < particles.length; i++) {
        for (let j = i + 1; j < particles.length; j++) {
          const dx = particles[i].x - particles[j].x;
          const dy = particles[i].y - particles[j].y;
          const dist = Math.sqrt(dx * dx + dy * dy);
          if (dist < 140) {
            ctx.beginPath();
            ctx.moveTo(particles[i].x, particles[i].y);
            ctx.lineTo(particles[j].x, particles[j].y);
            ctx.strokeStyle = `rgba(124, 58, 237, ${0.07 * (1 - dist / 140)})`;
            ctx.lineWidth = 0.5;
            ctx.stroke();
          }
        }
      }
    }

    function animate(timestamp) {
      t = timestamp;
      drawMesh(t);
      drawConnections();
      drawParticles();
      animFrame = requestAnimationFrame(animate);
    }

    animFrame = requestAnimationFrame(animate);

    const onResize = () => {
      width = canvas.width = window.innerWidth;
      height = canvas.height = window.innerHeight * 2;
    };
    window.addEventListener("resize", onResize);

    return () => {
      cancelAnimationFrame(animFrame);
      window.removeEventListener("resize", onResize);
    };
  }, []);

  return (
    <canvas
      ref={canvasRef}
      style={{
        position: "fixed",
        top: 0,
        left: 0,
        width: "100%",
        height: "100%",
        pointerEvents: "none",
        zIndex: 0,
        opacity: 1,
      }}
    />
  );
}
