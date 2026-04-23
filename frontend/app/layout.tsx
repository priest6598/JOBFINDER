import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
  display: "swap",
});

export const metadata: Metadata = {
  title: "PathAI — AI-Powered Job Search Copilot for India",
  description:
    "Upload your resume. Get AI-matched jobs, tailored resumes, auto-generated cover letters, and interview prep — all in one platform built for the Indian job market.",
  keywords: [
    "job search",
    "AI resume",
    "job matching",
    "interview prep",
    "India jobs",
    "career copilot",
  ],
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className={inter.variable}>
      <body className="font-sans antialiased">{children}</body>
    </html>
  );
}
