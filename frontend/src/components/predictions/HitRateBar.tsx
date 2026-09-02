import { hitRateTier, tierBarFill, tierText } from "../../lib/formatters";

interface HitRateBarProps {
  rate: number;
  overCount: number;
  lastN: number;
}

export default function HitRateBar({ rate, overCount, lastN }: HitRateBarProps) {
  const tier = hitRateTier(rate);
  const clamped = Math.min(100, Math.max(0, rate));

  return (
    <div className="rounded-xl border border-white/10 bg-black/25 p-4">
      <div className="mb-2 flex items-end justify-between gap-3">
        <div>
          <p className="text-xs font-semibold uppercase tracking-wider text-slate-500">
            Hit rate
          </p>
          <p className={`font-display text-2xl font-bold ${tierText(tier)}`}>
            {rate}%
          </p>
        </div>
        <p className="text-xs text-slate-500">
          {overCount}/{lastN} overs
        </p>
      </div>
      <div className="h-2.5 overflow-hidden rounded-full bg-white/10">
        <div
          className={`h-full rounded-full transition-all duration-500 ${tierBarFill(tier)}`}
          style={{ width: `${clamped}%` }}
        />
      </div>
    </div>
  );
}
