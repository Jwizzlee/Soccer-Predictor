import type { PropType, Recommendation } from "../types/common";

const PROP_LABELS: Record<PropType, string> = {
  goals: "Goals",
  assists: "Assists",
  shots: "Shots",
  shots_on_target: "Shots on Target",
};

export function formatPropLabel(prop: PropType): string {
  return PROP_LABELS[prop] ?? prop;
}

export function formatConfidence(value: number): string {
  return `${Math.round(value * 100)}%`;
}

export function recommendationColor(rec: Recommendation): string {
  return rec === "OVER" ? "text-accent-over" : "text-accent-under";
}

export function recommendationBg(rec: Recommendation): string {
  return rec === "OVER" ? "bg-accent-over/20" : "bg-accent-under/20";
}

export type ColorTier = "high" | "mid" | "low";

export function hitRateTier(rate: number): ColorTier {
  if (rate >= 60) return "high";
  if (rate >= 40) return "mid";
  return "low";
}

export function confidenceTier(pct: number): ColorTier {
  if (pct >= 75) return "high";
  if (pct >= 50) return "mid";
  return "low";
}

export function tierBarFill(tier: ColorTier): string {
  return {
    high: "bg-accent-over",
    mid: "bg-amber-400",
    low: "bg-accent-under",
  }[tier];
}

export function tierText(tier: ColorTier): string {
  return {
    high: "text-accent-over",
    mid: "text-amber-300",
    low: "text-accent-under",
  }[tier];
}

export function tierBorderBg(tier: ColorTier): string {
  return {
    high: "border-accent-over/40 bg-accent-over/15 text-accent-over",
    mid: "border-amber-400/40 bg-amber-400/10 text-amber-300",
    low: "border-accent-under/40 bg-accent-under/10 text-accent-under",
  }[tier];
}

export function formatRelativeTime(isoDate: string): string {
  const then = new Date(isoDate).getTime();
  const now = Date.now();
  const seconds = Math.floor((now - then) / 1000);

  if (seconds < 60) return "Just now";
  const minutes = Math.floor(seconds / 60);
  if (minutes < 60) return `${minutes} min ago`;
  const hours = Math.floor(minutes / 60);
  if (hours < 24) return `${hours} hr${hours === 1 ? "" : "s"} ago`;
  const days = Math.floor(hours / 24);
  if (days < 7) return `${days} day${days === 1 ? "" : "s"} ago`;
  return new Date(isoDate).toLocaleDateString();
}
