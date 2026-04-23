"use client";

import { motion } from "framer-motion";
import {
  Upload,
  Cpu,
  Briefcase,
  ArrowRight,
} from "lucide-react";

const steps = [
  {
    number: "01",
    icon: Upload,
    title: "Upload your resume",
    description:
      "Drop your PDF or DOCX. Our AI extracts skills, experience, and builds your Career DNA profile in seconds.",
    color: "text-brand-500",
    bg: "bg-brand-50",
    borderColor: "border-brand-200",
  },
  {
    number: "02",
    icon: Cpu,
    title: "AI matches & tailors",
    description:
      "Every job is scored against your profile. Resumes and cover letters are auto-tailored — nothing fabricated, always authentic.",
    color: "text-violet-500",
    bg: "bg-violet-50",
    borderColor: "border-violet-200",
  },
  {
    number: "03",
    icon: Briefcase,
    title: "Apply & prep with confidence",
    description:
      "Track applications on a kanban board, get interview prep decks, and practice with AI mock interviews that score you live.",
    color: "text-emerald-500",
    bg: "bg-emerald-50",
    borderColor: "border-emerald-200",
  },
];

const containerVariants = {
  hidden: {},
  visible: {
    transition: {
      staggerChildren: 0.15,
    },
  },
};

const cardVariants = {
  hidden: { opacity: 0, y: 24 },
  visible: {
    opacity: 1,
    y: 0,
    transition: { duration: 0.5, ease: "easeOut" },
  },
};

export default function HowItWorksSection() {
  return (
    <section
      id="how-it-works"
      className="py-20 sm:py-28 bg-white border-y border-slate-200/60"
    >
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
            How It Works
          </span>
          <h2 className="text-3xl sm:text-4xl font-extrabold text-slate-900 tracking-tight mb-4">
            Three steps to your next job
          </h2>
          <p className="text-base text-slate-500 leading-relaxed">
            Simple, fast, and entirely powered by AI. Start in under a minute.
          </p>
        </motion.div>

        {/* Steps */}
        <motion.div
          variants={containerVariants}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, amount: 0.2 }}
          className="grid md:grid-cols-3 gap-6"
        >
          {steps.map((step, index) => (
            <motion.div
              key={step.number}
              variants={cardVariants}
              className="relative group"
            >
              {/* Connector arrow (visible on md+ between cards) */}
              {index < steps.length - 1 && (
                <div className="hidden md:flex absolute top-1/2 -right-3 transform -translate-y-1/2 z-10">
                  <ArrowRight className="w-5 h-5 text-slate-300" />
                </div>
              )}

              <div
                className={`bg-slate-50/50 rounded-2xl border ${step.borderColor} p-7 h-full hover:shadow-card-lg transition-all duration-300 hover:-translate-y-0.5`}
              >
                {/* Step Number */}
                <span className="text-xs font-bold text-slate-300 uppercase tracking-widest mb-5 block">
                  Step {step.number}
                </span>

                {/* Icon */}
                <div
                  className={`w-12 h-12 rounded-xl ${step.bg} flex items-center justify-center mb-5 group-hover:scale-110 transition-transform duration-300`}
                >
                  <step.icon className={`w-6 h-6 ${step.color}`} />
                </div>

                <h3 className="text-lg font-bold text-slate-900 mb-2">
                  {step.title}
                </h3>
                <p className="text-sm text-slate-500 leading-relaxed">
                  {step.description}
                </p>
              </div>
            </motion.div>
          ))}
        </motion.div>
      </div>
    </section>
  );
}
