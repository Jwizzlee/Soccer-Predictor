import { useState } from "react";
import type { PredictionHistoryItem } from "../../types/prediction";
import {
  formatPropLabel,
  formatRelativeTime,
  hitRateTier,
  recommendationBg,
  recommendationColor,
  tierText,
} from "../../lib/formatters";

interface RecentPicksProps {
  items: PredictionHistoryItem[];
  isLoading?: boolean;
  isError?: boolean;
  selectedPickId?: number | null;
  onSelectPick?: (item: PredictionHistoryItem) => void;
}

export default function RecentPicks({
  items,
  isLoading,
  isError,
  selectedPickId,
  onSelectPick,
}: RecentPicksProps) {
  const [expanded, setExpanded] = useState(true);

  return (
    <section className="mt-10">
      <button
        type="button"
        onClick={() => setExpanded((open) => !open)}
        className="mb-4 flex w-full items-center justify-between gap-3 text-left"
      >
        <div>
          <h2 className="font-display text-lg font-semibold text-white">
            Recent picks
          </h2>
          <p className="section-subtitle">Click a row to reload that pick</p>
        </div>
        <span className="text-sm text-slate-500">{expanded ? "−" : "+"}</span>
      </button>

      {expanded && (
        <div className="glass-panel divide-y divide-white/5 overflow-hidden">
          {isLoading && (
            <p className="p-6 text-center text-sm text-slate-500">
              Loading history…
            </p>
          )}

          {isError && (
            <p className="p-6 text-center text-sm text-accent-under">
              Could not load recent picks.
            </p>
          )}

          {!isLoading && !isError && items.length === 0 && (
            <p className="p-6 text-center text-sm text-slate-500">
              No picks yet — run your first analysis above.
            </p>
          )}

          {!isLoading &&
            !isError &&
            items.map((item) => (
              <RecentPickRow
                key={item.id}
                item={item}
                selected={selectedPickId === item.id}
                onSelect={onSelectPick}
              />
            ))}
        </div>
      )}
    </section>
  );
}

interface RecentPickRowProps {
  item: PredictionHistoryItem;
  selected?: boolean;
  onSelect?: (item: PredictionHistoryItem) => void;
}

function RecentPickRow({ item, selected, onSelect }: RecentPickRowProps) {
  const hitTier = hitRateTier(item.hit_rate);
  const clickable = Boolean(onSelect && item.player_id);

  return (
    <button
      type="button"
      onClick={() => onSelect?.(item)}
      disabled={!clickable}
      className={`flex w-full flex-wrap items-center gap-3 px-4 py-4 text-left transition-colors sm:px-6 ${
        clickable
          ? "cursor-pointer hover:bg-white/5 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-[-2px] focus-visible:outline-accent-primary"
          : "cursor-default opacity-70"
      } ${selected ? "bg-accent-primary/10 ring-1 ring-inset ring-accent-primary/30" : ""}`}
    >
      <div className="min-w-0 flex-1">
        <p className="truncate font-semibold text-white">{item.player_name}</p>
        <p className="text-xs text-slate-500">
          {item.team_name ? `${item.team_name} · ` : ""}
          {formatPropLabel(item.prop_type)} · Line {item.line}
        </p>
      </div>

      <span
        className={`rounded-full px-3 py-1 text-xs font-bold uppercase tracking-wider ${recommendationBg(item.recommendation)} ${recommendationColor(item.recommendation)}`}
      >
        {item.recommendation}
      </span>

      <div className="text-right">
        <p className={`text-sm font-bold ${tierText(hitTier)}`}>
          {Math.round(item.hit_rate)}% hit
        </p>
        <p className="text-[10px] text-slate-600">
          {formatRelativeTime(item.created_at)}
        </p>
      </div>
    </button>
  );
}
