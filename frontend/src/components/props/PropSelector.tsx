import type { PropType } from "../../types/common";
import { formatPropLabel } from "../../lib/formatters";

const MVP_PROPS: PropType[] = [
  "goals",
  "assists",
  "shots",
  "shots_on_target",
];

export const MAX_LAST_N_GAMES = 5;
export const DEFAULT_LAST_N_GAMES = 5;

interface PropSelectorProps {
  propType: PropType;
  line: string;
  lastNGames: number;
  onPropChange: (prop: PropType) => void;
  onLineChange: (line: string) => void;
  onLastNChange: (n: number) => void;
  disabled?: boolean;
}

export default function PropSelector({
  propType,
  line,
  lastNGames,
  onPropChange,
  onLineChange,
  onLastNChange,
  disabled,
}: PropSelectorProps) {
  return (
    <div className="grid gap-4 sm:grid-cols-3">
      <div>
        <label className="mb-2 block text-xs font-semibold uppercase tracking-wider text-slate-500">
          Prop type
        </label>
        <select
          value={propType}
          onChange={(e) => onPropChange(e.target.value as PropType)}
          disabled={disabled}
          className="glass-input w-full disabled:opacity-50"
        >
          {MVP_PROPS.map((p) => (
            <option key={p} value={p}>
              {formatPropLabel(p)}
            </option>
          ))}
        </select>
      </div>
      <div>
        <label className="mb-2 block text-xs font-semibold uppercase tracking-wider text-slate-500">
          Line
        </label>
        <input
          type="number"
          step="0.5"
          min="0.5"
          value={line}
          onChange={(e) => onLineChange(e.target.value)}
          disabled={disabled}
          className="glass-input w-full disabled:opacity-50"
        />
      </div>
      <div>
        <label className="mb-2 block text-xs font-semibold uppercase tracking-wider text-slate-500">
          Last N games
        </label>
        <input
          type="number"
          min={3}
          max={MAX_LAST_N_GAMES}
          value={lastNGames}
          onChange={(e) => {
            const parsed = Number(e.target.value);
            if (Number.isNaN(parsed)) return;
            onLastNChange(Math.min(MAX_LAST_N_GAMES, Math.max(3, parsed)));
          }}
          disabled={disabled}
          className="glass-input w-full disabled:opacity-50"
        />
        <p className="mt-2 text-xs text-slate-500">
          Free API plan allows 10 requests/min — max {MAX_LAST_N_GAMES} games per
          analysis.
        </p>
      </div>
    </div>
  );
}
