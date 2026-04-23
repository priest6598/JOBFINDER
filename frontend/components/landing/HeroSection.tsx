"use client";

import { motion } from "framer-motion";
import Link from "next/link";
import {
  ArrowRight,
  Upload,
  Target,
  Star,
  TrendingUp,
  Building2,
  MapPin,
  Clock,
} from "lucide-react";

const mockJobs = [
  {
    company: "Razorpay",
    role: "Senior Data Engineer",
    location: "Bangalore",
    match: 94,
    salary: "₹30L–₹45L",
    tags: ["Python", "Spark", "Kafka"],
    fresh: true,
    ghost: "Legit",
  },
  {
    company: "CRED",
    role: "Full-Stack Engineer",
    location: "Bangalore",
    match: 88,
    salary: "₹25L–₹40L",
    tags: ["React", "TypeScript", "Node.js"],
    fresh: true,
    ghost: "Legit",
  },
  {
    company: "PhonePe",
    role: "Staff Data Engineer",
    location: "Remote",
    match: 82,
    salary: "₹40L–₹60L",
    tags: ["Spark", "Iceberg", "dbt"],
    fresh: false,
    ghost: "Legit",
  },
];

function MatchBadge({ score }: { score: number }) {
  const color =
    score >= 85
      ? "bg-emerald-50 text-emerald-700 border-emerald-200"
      : score >= 70
        ? "bg-amber-50 text-amber-700 border-amber-200"
        : "bg-slate-50 text-slate-600 border-slate-200";
  return (
    <span
      className={`inline-flex items-center gap-1 text-xs font-semibold px-2.5 py-1 rounded-lg border ${color}`}
    >
      <Target className="w-3 h-3" />
      {score}% match
    </span>
  );
}

function GhostBadge({ label }: { label: string }) {
  return (
    <span className="inline-flex items-center gap-1 text-[11px] font-medium px-2 py-0.5 rounded-md bg-emerald-50 text-emerald-600 border border-emerald-100">
      <Star className="w-2.5 h-2.5" />
      {label}
    </span>
  );
}

function MockJobCard({
  job,
  index,
}: {
  job: (typeof mockJobs)[0];
  index: number;
}) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.6 + index * 0.12, duration: 0.4, ease: "easeOut" }}
      className="bg-white rounded-2xl border border-slate-200/80 p-4 shadow-card hover:shadow-card-lg hover:border-brand-200/60 transition-all duration-300 group cursor-default"
    >
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-slate-100 flex items-center justify-center text-slate-400 group-hover:bg-brand-50 group-hover:text-brand-500 transition-colors duration-300">
            <Building2 className="w-5 h-5" />
          </div>
          <div>
            <p className="text-sm font-semibold text-slate-900 leading-tight">
              {job.role}
            </p>
            <p className="text-xs text-slate-500 mt-0.5">{job.company}</p>
          </div>
        </div>
        <MatchBadge score={job.match} />
      </div>
      <div className="flex items-center gap-3 text-xs text-slate-500 mb-3">
        <span className="flex items-center gap-1">
          <MapPin className="w-3 h-3" />
          {job.location}
        </span>
        <span className="flex items-center gap-1">
          <TrendingUp className="w-3 h-3" />
          {job.salary}
        </span>
        {job.fresh && (
          <span className="flex items-center gap-1 text-emerald-600 font-medium">
            <Clock className="w-3 h-3" />
            Fresh
          </span>
        )}
      </div>
      <div className="flex items-center gap-1.5 flex-wrap">
        {job.tags.map((tag) => (
          <span
            key={tag}
            className="text-[11px] font-medium px-2 py-0.5 rounded-md bg-slate-100 text-slate-600"
          >
            {tag}
          </span>
        ))}
        <GhostBadge label={job.ghost} />
      </div>
    </motion.div>
  );
}

export default function HeroSection() {
  return (
    <section className="relative pt-28 pb-16 sm:pt-36 sm:pb-24 overflow-hidden">
      {/* Subtle background gradient orbs */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-20 -left-40 w-[500px] h-[500px] bg-brand-400/[0.07] rounded-full blur-[100px]" />
        <div className="absolute top-40 -right-40 w-[400px] h-[400px] bg-violet-400/[0.06] rounded-full blur-[100px]" />
      </div>

      <div className="max-w-[1200px] mx-auto section-padding relative">
        <div className="grid lg:grid-cols-2 gap-12 lg:gap-16 items-center">
          {/* Left: Copy */}
          <div className="max-w-xl">
            <motion.div
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.4 }}
              className="inline-flex items-center gap-2 text-sm font-medium text-brand-600 bg-brand-50 border border-brand-100 px-4 py-1.5 rounded-full mb-6"
            >
              <Upload className="w-3.5 h-3.5" />
              Upload resume. AI does the rest.
            </motion.div>

            <motion.h1
              initial={{ opacity: 0, y: 16 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1, duration: 0.5 }}
              className="text-4xl sm:text-5xl lg:text-[3.5rem] font-extrabold text-slate-900 tracking-tight leading-[1.1] mb-5"
            >
              Your AI copilot
              <br />
              <span className="text-gradient">for getting hired</span>
            </motion.h1>

            <motion.p
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2, duration: 0.5 }}
              className="text-lg text-slate-500 leading-relaxed mb-8 max-w-md"
            >
              PathAI matches you to jobs, tailors your resume per role,
              generates cover letters, and preps you for interviews —
              all powered by AI.
            </motion.p>

            <motion.div
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3, duration: 0.5 }}
              className="flex flex-col sm:flex-row items-start sm:items-center gap-3"
            >
              <Link
                href="/signup"
                className="inline-flex items-center gap-2 text-sm font-semibold text-white bg-brand-500 hover:bg-brand-600 px-7 py-3.5 rounded-xl transition-all duration-200 shadow-lg shadow-brand-500/20 hover:shadow-brand-500/30 hover:-translate-y-0.5"
              >
                Start for free
                <ArrowRight className="w-4 h-4" />
              </Link>
              <span className="text-xs text-slate-400 ml-1">
                No credit card required
              </span>
            </motion.div>
          </div>

          {/* Right: Mock Dashboard Preview */}
          <motion.div
            initial={{ opacity: 0, x: 24 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.35, duration: 0.6, ease: "easeOut" }}
            className="relative"
          >
            {/* Glow behind card */}
            <div className="absolute -inset-4 bg-brand-400/[0.04] rounded-3xl blur-2xl" />

            <div className="relative bg-white/80 backdrop-blur-sm rounded-2xl border border-slate-200/80 shadow-xl shadow-slate-200/30 overflow-hidden">
              {/* Header bar */}
              <div className="px-5 py-3 border-b border-slate-100 flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <div className="w-2.5 h-2.5 rounded-full bg-emerald-400 animate-pulse" />
                  <span className="text-xs font-medium text-slate-500">
                    AI Match Engine Active
                  </span>
                </div>
                <span className="text-[11px] text-slate-400">
                  3 new matches today
                </span>
              </div>

              {/* Job Cards */}
              <div className="p-4 space-y-3">
                {mockJobs.map((job, i) => (
                  <MockJobCard key={job.company} job={job} index={i} />
                ))}
              </div>
            </div>
          </motion.div>
        </div>
      </div>
    </section>
  );
}
