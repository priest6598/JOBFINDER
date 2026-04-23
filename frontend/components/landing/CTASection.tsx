"use client";

import { motion } from "framer-motion";
import Link from "next/link";
import { ArrowRight, Sparkles, Zap, Shield } from "lucide-react";

const stats = [
  { value: "10+", label: "Companies in India", icon: Shield },
  { value: "7", label: "AI-powered tools", icon: Zap },
  { value: "<60s", label: "Resume analysis time", icon: Sparkles },
];

export default function CTASection() {
  return (
    <section className="py-20 sm:py-28 bg-white border-y border-slate-200/60">
      <div className="max-w-[1200px] mx-auto section-padding">
        {/* Stats */}
        <motion.div
          initial={{ opacity: 0, y: 12 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, amount: 0.5 }}
          transition={{ duration: 0.5 }}
          className="flex flex-col sm:flex-row items-center justify-center gap-8 sm:gap-16 mb-16"
        >
          {stats.map((stat) => (
            <div key={stat.label} className="flex items-center gap-3 group">
              <div className="w-10 h-10 rounded-xl bg-brand-50 flex items-center justify-center group-hover:scale-110 transition-transform duration-300">
                <stat.icon className="w-5 h-5 text-brand-500" />
              </div>
              <div>
                <p className="text-2xl font-extrabold text-slate-900">
                  {stat.value}
                </p>
                <p className="text-xs text-slate-500">{stat.label}</p>
              </div>
            </div>
          ))}
        </motion.div>

        {/* CTA */}
        <motion.div
          initial={{ opacity: 0, y: 16 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, amount: 0.5 }}
          transition={{ delay: 0.1, duration: 0.5 }}
          className="relative"
        >
          <div className="absolute -inset-4 bg-brand-400/[0.04] rounded-3xl blur-2xl" />
          <div className="relative bg-slate-900 rounded-2xl p-10 sm:p-14 text-center overflow-hidden">
            {/* Subtle accent gradient */}
            <div className="absolute top-0 right-0 w-80 h-80 bg-brand-500/10 rounded-full blur-[80px] -translate-y-1/2 translate-x-1/2" />

            <h2 className="text-3xl sm:text-4xl font-extrabold text-white tracking-tight mb-4 relative">
              Stop applying blind.
              <br />
              <span className="text-brand-300">
                Let AI find your perfect fit.
              </span>
            </h2>
            <p className="text-base text-slate-400 max-w-md mx-auto mb-8 leading-relaxed relative">
              Join PathAI today — upload your resume and get AI-matched to the
              best jobs in India, with tailored applications ready in minutes.
            </p>
            <Link
              href="/signup"
              className="relative inline-flex items-center gap-2 text-sm font-semibold text-slate-900 bg-white hover:bg-slate-100 px-8 py-4 rounded-xl transition-all duration-200 shadow-lg hover:shadow-xl hover:-translate-y-0.5"
            >
              Get Started — It&apos;s Free
              <ArrowRight className="w-4 h-4" />
            </Link>
          </div>
        </motion.div>
      </div>
    </section>
  );
}
