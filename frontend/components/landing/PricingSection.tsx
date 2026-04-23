"use client";

import { motion } from "framer-motion";
import { Check, Sparkles } from "lucide-react";
import Link from "next/link";

const tiers = [
  {
    name: "Free",
    price: "₹0",
    period: "forever",
    description: "Get started with the essentials",
    cta: "Start free",
    ctaStyle:
      "bg-white text-slate-900 border border-slate-200 hover:border-slate-300 hover:bg-slate-50",
    features: [
      "20 AI-matched jobs per day",
      "2 tailored resumes per month",
      "2 AI cover letters per month",
      "1 mock interview per week",
      "Application kanban tracker",
      "Ghost job detection",
    ],
    popular: false,
  },
  {
    name: "Boost",
    price: "₹49",
    period: "per 5 credits",
    description: "Unlock power features on demand",
    cta: "Get credits",
    ctaStyle:
      "bg-brand-500 text-white hover:bg-brand-600 shadow-lg shadow-brand-500/20 hover:shadow-brand-500/30",
    features: [
      "Everything in Free",
      "Extra resume tailoring (3 credits)",
      "Company prep packs (8 credits)",
      "Voice mock interviews (5 credits)",
      "LinkedIn profile rewrite (6 credits)",
      "Priority job matching",
    ],
    popular: true,
  },
  {
    name: "Pro",
    price: "₹399",
    period: "per month",
    description: "Unlimited everything, zero limits",
    cta: "Go Pro",
    ctaStyle:
      "bg-slate-900 text-white hover:bg-slate-800 shadow-lg shadow-slate-900/15",
    features: [
      "Everything in Boost",
      "Unlimited job matches",
      "Unlimited resume tailoring",
      "Unlimited cover letters",
      "Unlimited mock interviews",
      "All credit features included",
    ],
    popular: false,
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

export default function PricingSection() {
  return (
    <section id="pricing" className="py-20 sm:py-28">
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
            Pricing
          </span>
          <h2 className="text-3xl sm:text-4xl font-extrabold text-slate-900 tracking-tight mb-4">
            Start free. Pay only when you need more.
          </h2>
          <p className="text-base text-slate-500 leading-relaxed">
            No subscriptions required. Buy credits when you need power features,
            or go Pro for unlimited access.
          </p>
        </motion.div>

        {/* Pricing Cards */}
        <motion.div
          variants={containerVariants}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, amount: 0.2 }}
          className="grid md:grid-cols-3 gap-5 items-start"
        >
          {tiers.map((tier) => (
            <motion.div
              key={tier.name}
              variants={cardVariants}
              className={`relative bg-white rounded-2xl border p-7 transition-all duration-300 hover:-translate-y-0.5 ${
                tier.popular
                  ? "border-brand-200 shadow-xl shadow-brand-500/[0.07] ring-1 ring-brand-100"
                  : "border-slate-200/80 shadow-card hover:shadow-card-lg"
              }`}
            >
              {/* Popular badge */}
              {tier.popular && (
                <div className="absolute -top-3 left-1/2 -translate-x-1/2">
                  <span className="inline-flex items-center gap-1.5 text-xs font-semibold text-brand-600 bg-brand-50 border border-brand-200 px-4 py-1.5 rounded-full shadow-sm">
                    <Sparkles className="w-3 h-3" />
                    Most Popular
                  </span>
                </div>
              )}

              <div className={tier.popular ? "mt-2" : ""}>
                <h3 className="text-lg font-bold text-slate-900">
                  {tier.name}
                </h3>
                <p className="text-sm text-slate-500 mt-1 mb-5">
                  {tier.description}
                </p>

                <div className="flex items-baseline gap-1.5 mb-6">
                  <span className="text-4xl font-extrabold text-slate-900">
                    {tier.price}
                  </span>
                  <span className="text-sm text-slate-400">
                    {tier.period}
                  </span>
                </div>

                <Link
                  href="/signup"
                  className={`block w-full text-center text-sm font-semibold px-5 py-3 rounded-xl transition-all duration-200 mb-7 ${tier.ctaStyle}`}
                >
                  {tier.cta}
                </Link>

                <ul className="space-y-3">
                  {tier.features.map((feature) => (
                    <li
                      key={feature}
                      className="flex items-start gap-2.5 text-sm text-slate-600"
                    >
                      <Check className="w-4 h-4 text-emerald-500 mt-0.5 shrink-0" />
                      {feature}
                    </li>
                  ))}
                </ul>
              </div>
            </motion.div>
          ))}
        </motion.div>
      </div>
    </section>
  );
}
