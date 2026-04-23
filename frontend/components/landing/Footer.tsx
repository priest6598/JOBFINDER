"use client";

import Link from "next/link";
import { Sparkles } from "lucide-react";

export default function Footer() {
  return (
    <footer className="py-10 sm:py-12">
      <div className="max-w-[1200px] mx-auto section-padding">
        <div className="flex flex-col sm:flex-row items-center justify-between gap-6">
          {/* Logo */}
          <Link href="/" className="flex items-center gap-2">
            <div className="w-7 h-7 rounded-lg bg-brand-500 flex items-center justify-center">
              <Sparkles className="w-3.5 h-3.5 text-white" />
            </div>
            <span className="text-lg font-bold tracking-tight text-slate-900">
              Path<span className="text-brand-500">AI</span>
            </span>
          </Link>

          {/* Links */}
          <div className="flex items-center gap-6">
            <a
              href="#features"
              className="text-sm text-slate-500 hover:text-slate-900 transition-colors"
            >
              Features
            </a>
            <a
              href="#how-it-works"
              className="text-sm text-slate-500 hover:text-slate-900 transition-colors"
            >
              How It Works
            </a>
            <a
              href="#pricing"
              className="text-sm text-slate-500 hover:text-slate-900 transition-colors"
            >
              Pricing
            </a>
          </div>

          {/* Copyright */}
          <p className="text-xs text-slate-400">
            © {new Date().getFullYear()} PathAI. Built for India.
          </p>
        </div>
      </div>
    </footer>
  );
}
