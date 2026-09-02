import type { PredictionResponse } from "../../types/prediction";
import { formatPropLabel } from "../../lib/formatters";
import ConfidenceBadge from "./ConfidenceBadge";
import FormBadges from "./FormBadges";
import HitRateBar from "./HitRateBar";
import ReasoningPanel from "./ReasoningPanel";

interface PredictionCardProps {
  prediction: PredictionResponse;
}

export default function PredictionCard({ prediction }: PredictionCardProps) {
  const { supporting_stats: stats } = prediction;
  const isOver = prediction.recommendation === "OVER";
  const hitRate =
    stats.last_n > 0
      ? Math.round((stats.over_count / stats.last_n) * 100)
      : 0;

  return (
    <article className="glass-panel relative mt-6 overflow-hidden">
      <div
        className={`absolute inset-x-0 top-0 h-1 ${
          isOver
            ? "bg-gradient-to-r from-transparent via-accent-over to-transparent"
            : "bg-gradient-to-r from-transparent via-accent-under to-transparent"
        }`}
      />

      <div className="p-6 md:p-8">
        <div className="mb-6 flex flex-wrap items-start justify-between gap-4">
          <div>
            <p className="text-xs font-bold uppercase tracking-[0.2em] text-slate-500">
              AI Prop Verdict
            </p>
            <h3 className="mt-1 font-display text-2xl font-bold text-white">
              {prediction.player_name}
            </h3>
            <p className="mt-1 text-sm text-slate-400">
              {prediction.team_name ? `${prediction.team_name} · ` : ""}
              {formatPropLabel(prediction.prop_type)} · Line{" "}
              <span className="font-semibold text-white">{prediction.line}</span>
            </p>
          </div>

          <div
            className={`flex min-w-[7rem] flex-col items-center justify-center rounded-2xl border-2 px-6 py-4 shadow-lg ${
              isOver
                ? "border-accent-over/60 bg-accent-over/15 text-accent-over shadow-accent-over/20"
                : "border-accent-under/60 bg-accent-under/15 text-accent-under shadow-accent-under/20"
            }`}
          >
            <span className="text-[10px] font-bold uppercase tracking-[0.25em] opacity-80">
              Pick
            </span>
            <span className="font-display text-3xl font-extrabold tracking-tight">
              {prediction.recommendation}
            </span>
          </div>
        </div>

        <ConfidenceBadge value={prediction.confidence} />

        <div className="mt-6 grid gap-4 sm:grid-cols-3">
          <div className="rounded-xl border border-white/10 bg-black/20 px-4 py-3 text-center">
            <p className="text-[10px] font-semibold uppercase tracking-wider text-slate-500">
              Average
            </p>
            <p className="font-display text-2xl font-bold text-white">
              {stats.average}
            </p>
          </div>
          <div className="rounded-xl border border-accent-over/20 bg-accent-over/5 px-4 py-3 text-center">
            <p className="text-[10px] font-semibold uppercase tracking-wider text-accent-over/80">
              Over
            </p>
            <p className="font-display text-2xl font-bold text-accent-over">
              {stats.over_count}
            </p>
          </div>
          <div className="rounded-xl border border-accent-under/20 bg-accent-under/5 px-4 py-3 text-center">
            <p className="text-[10px] font-semibold uppercase tracking-wider text-accent-under/80">
              Under
            </p>
            <p className="font-display text-2xl font-bold text-accent-under">
              {stats.under_count}
            </p>
          </div>
        </div>

        <div className="mt-4">
          <HitRateBar
            rate={hitRate}
            overCount={stats.over_count}
            lastN={stats.last_n}
          />
        </div>

        <div className="mt-4">
          <FormBadges
            values={stats.recent_values}
            line={prediction.line}
            lastN={stats.last_n}
          />
        </div>

        <div className="mt-8 border-t border-white/10 pt-6">
          <ReasoningPanel
            reasoning={prediction.reasoning}
            keyFactors={prediction.key_factors}
            riskFlags={prediction.risk_flags}
          />
        </div>

        <p className="mt-4 text-right text-[10px] text-slate-600">
          Generated {new Date(prediction.generated_at).toLocaleString()}
        </p>
      </div>
    </article>
  );
}
