import "./globals.css";

export const metadata = {
  title: "Resilient ATS — Intelligent Resume Analyzer",
  description:
    "AI-powered resume analysis with adversarial detection, semantic matching, and multi-factor scoring. Detect keyword stuffing, hidden text, and more.",
  keywords: [
    "ATS",
    "resume analyzer",
    "adversarial detection",
    "NLP",
    "semantic matching",
  ],
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
