import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatINR(n?: number | null): string {
  if (n == null) return "—";
  if (n >= 10_00_000) return `₹${(n / 100_000).toFixed(1)}L`;
  if (n >= 1_000) return `₹${(n / 1_000).toFixed(0)}k`;
  return `₹${n}`;
}

export function salaryRange(min?: number | null, max?: number | null): string {
  if (!min && !max) return "Salary not disclosed";
  if (min && max) return `${formatINR(min)}–${formatINR(max)}`;
  return formatINR(min ?? max ?? undefined);
}

export function relativeTime(iso?: string | null): string {
  if (!iso) return "";
  const d = new Date(iso);
  const diff = Date.now() - d.getTime();
  const mins = Math.floor(diff / 60000);
  if (mins < 1) return "just now";
  if (mins < 60) return `${mins}m ago`;
  const hrs = Math.floor(mins / 60);
  if (hrs < 24) return `${hrs}h ago`;
  const days = Math.floor(hrs / 24);
  if (days < 30) return `${days}d ago`;
  const months = Math.floor(days / 30);
  return `${months}mo ago`;
}

export function matchScoreColor(score: number): string {
  if (score >= 80) return "text-success";
  if (score >= 60) return "text-warning";
  return "text-ink-muted";
}

export function ghostBadge(score: number): { label: string; color: string } {
  if (score >= 75) return { label: "Legit", color: "bg-success-light text-success-dark" };
  if (score >= 50) return { label: "Unclear", color: "bg-warning-light text-warning-dark" };
  return { label: "Likely ghost", color: "bg-danger-light text-danger-dark" };
}
