import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: "class",
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        brand: {
          50: "#eef2ff",
          100: "#e0e7ff",
          200: "#c7d2fe",
          300: "#a5b4fc",
          400: "#818cf8",
          500: "#6366f1",
          600: "#4f46e5",
          700: "#4338ca",
          800: "#3730a3",
          900: "#1e1b4b",
        },
        surface: {
          DEFAULT: "#ffffff",
          secondary: "#f8f9fa",
          tertiary: "#f1f3f5",
          dark: "#0b0b0e",
          "dark-secondary": "#131318",
          "dark-tertiary": "#1b1b22",
        },
        ink: {
          primary: "#0f0f11",
          secondary: "#52525b",
          muted: "#a1a1aa",
          dark: "#fafafa",
          "dark-secondary": "#a1a1aa",
        },
        success: { light: "#d1fae5", DEFAULT: "#10b981", dark: "#065f46" },
        warning: { light: "#fef3c7", DEFAULT: "#f59e0b", dark: "#92400e" },
        danger: { light: "#fee2e2", DEFAULT: "#ef4444", dark: "#991b1b" },
        info: { light: "#dbeafe", DEFAULT: "#3b82f6", dark: "#1e40af" },
      },
      fontFamily: {
        sans: ["ui-sans-serif", "system-ui", "-apple-system", "BlinkMacSystemFont", "Segoe UI", "sans-serif"],
        serif: ["Georgia", "serif"],
        mono: ["ui-monospace", "SFMono-Regular", "Menlo", "monospace"],
      },
      borderRadius: {
        "4xl": "2rem",
      },
      animation: {
        "fade-in": "fadeIn 0.3s ease-out",
        "slide-up": "slideUp 0.3s ease-out",
        "slide-in": "slideIn 0.25s ease-out",
        "pulse-soft": "pulseSoft 2s ease-in-out infinite",
      },
      keyframes: {
        fadeIn: { from: { opacity: "0" }, to: { opacity: "1" } },
        slideUp: {
          from: { opacity: "0", transform: "translateY(8px)" },
          to: { opacity: "1", transform: "translateY(0)" },
        },
        slideIn: {
          from: { opacity: "0", transform: "translateX(-8px)" },
          to: { opacity: "1", transform: "translateX(0)" },
        },
        pulseSoft: { "0%,100%": { opacity: "1" }, "50%": { opacity: "0.6" } },
      },
      boxShadow: {
        card: "0 1px 3px rgba(0,0,0,0.06), 0 1px 2px rgba(0,0,0,0.04)",
        "card-lg": "0 4px 16px rgba(0,0,0,0.08), 0 2px 6px rgba(0,0,0,0.04)",
        glow: "0 0 0 3px rgba(99, 102, 241, 0.15)",
      },
    },
  },
  plugins: [require("tailwindcss-animate")],
};

export default config;
