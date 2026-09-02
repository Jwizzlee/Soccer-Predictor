import {
  confidenceTier,
  formatConfidence,
  tierBarFill,
  tierBorderBg,
} from "../../lib/formatters";

interface ConfidenceBadgeProps {
  value: number;
}

export default function ConfidenceBadge({ value }: ConfidenceBadgeProps) {
  const pct = Math.round(value * 100);
  const tier = confidenceTier(pct);

  return (
    <div className="space-y-2">
      <div
        className={`inline-flex items-center gap-2 rounded-full border px-3 py-1.5 text-sm font-semibold ${tierBorderBg(tier)}`}
      >
        <span className="h-2 w-2 rounded-full bg-current opacity-80" />
        {formatConfidence(value)} model confidence
      </div>
      <div className="max-w-xs">
        <div className="mb-1 flex justify-between text-[10px] font-medium uppercase tracking-wider text-slate-500">
          <span>Confidence meter</span>
          <span>{pct}%</span>
        </div>
        <div className="h-2 overflow-hidden rounded-full bg-white/10">
          <div
            className={`h-full rounded-full transition-all duration-500 ${tierBarFill(tier)}`}
            style={{ width: `${pct}%` }}
          />
        </div>
      </div>
    </div>
  );
}
