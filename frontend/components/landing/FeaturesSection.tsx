"use client";

import { motion } from "framer-motion";
import {
  FileSearch,
  PenTool,
  BrainCircuit,
  BarChart3,
} from "lucide-react";

const features = [
  {
    icon: FileSearch,
    title: "AI Job Matching",
    description:
      "Upload your resume once. Our AI analyzes your skills, experience, and career DNA to score every job on a 0–100 match — plus a ghost-job detector to filter out fake postings.",
    color: "text-brand-500",
    bg: "bg-brand-50",
  },
  {
    icon: PenTool,
    title: "Resume Tailoring",
    description:
      "Automatically rewrite your resume for each role — stronger action verbs, keyword alignment, and measurable outcomes. Never fabricated, always true to your experience.",
    color: "text-violet-500",
    bg: "bg-violet-50",
  },
  {
    icon: BrainCircuit,
    title: "Interview Prep",
    description:
      "Get company-specific prep decks with likely questions, STAR stories extracted from your resume, and AI mock interviews that score your answers in real time.",
    color: "text-emerald-500",
    bg: "bg-emerald-50",
  },
  {
    icon: BarChart3,
    title: "Application Tracker",
    description:
      "Kanban board to track every application from applied to hired. AI-generated cover letters, status updates, and follow-up reminders — all in one place.",
    color: "text-amber-500",
    bg: "bg-amber-50",
  },
];

const containerVariants = {
  hidden: {},
  visible: {
    transition: {
      staggerChildren: 0.1,
    },
  },
};

const cardVariants = {
  hidden: { opacity: 0, y: 20 },
  visible: {
    opacity: 1,
    y: 0,
    transition: { duration: 0.45, ease: "easeOut" },
  },
};

export default function FeaturesSection() {
  return (
    <section id="features" className="py-20 sm:py-28">
      <div className="max-w-[1200px] mx-auto section-padding">
        {/* Section Header */}
        <motion.div
          initial={{ opacity: 0, y: 12 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, amount: 0.5 }}
          transition={{ duration: 0.5 }}
          className="text-center max-w-2xl mx-auto mb-14"
        >
          <span className="text-sm font-semibold text-brand-500 uppercase tracking-wider mb-3 block">
            Features
          </span>
          <h2 className="text-3xl sm:text-4xl font-extrabold text-slate-900 tracking-tight mb-4">
            Everything you need to land your next role
          </h2>
          <p className="text-base text-slate-500 leading-relaxed">
            From intelligent matching to interview coaching — PathAI handles the
            heavy lifting so you can focus on what matters.
          </p>
        </motion.div>

        {/* Feature Cards */}
        <motion.div
          variants={containerVariants}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, amount: 0.2 }}
          className="grid sm:grid-cols-2 gap-5"
        >
          {features.map((feature) => (
            <motion.div
              key={feature.title}
              variants={cardVariants}
              className="group bg-white rounded-2xl border border-slate-200/80 p-7 shadow-card hover:shadow-card-lg hover:border-slate-300/80 transition-all duration-300 hover:-translate-y-0.5"
            >
              <div
                className={`w-11 h-11 rounded-xl ${feature.bg} flex items-center justify-center mb-5 group-hover:scale-110 transition-transform duration-300`}
              >
                <feature.icon className={`w-5 h-5 ${feature.color}`} />
              </div>
              <h3 className="text-lg font-bold text-slate-900 mb-2">
                {feature.title}
              </h3>
              <p className="text-sm text-slate-500 leading-relaxed">
                {feature.description}
              </p>
            </motion.div>
          ))}
        </motion.div>
      </div>
    </section>
  );
}
