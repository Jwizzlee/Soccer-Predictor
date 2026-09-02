import type { PlayerSummary } from "../../types/player";

interface PlayerCardProps {
  player: PlayerSummary;
  selected: boolean;
  onSelect: () => void;
}

export default function PlayerCard({
  player,
  selected,
  onSelect,
}: PlayerCardProps) {
  return (
    <button
      type="button"
      onClick={onSelect}
      className={`flex w-full items-center gap-4 p-4 text-left ${
        selected
          ? "glass-panel scale-[1.02] border-accent-primary/50 ring-2 ring-accent-primary/30"
          : "glass-card-interactive"
      }`}
    >
      {player.photo_url ? (
        <img
          src={player.photo_url}
          alt=""
          className="h-14 w-14 rounded-2xl border border-white/10 object-cover bg-black/40 shadow-lg"
        />
      ) : (
        <div className="flex h-14 w-14 items-center justify-center rounded-2xl border border-white/10 bg-black/40 font-display text-xl font-bold text-slate-400">
          {player.name.charAt(0)}
        </div>
      )}
      <div className="min-w-0 flex-1">
        <p className="truncate font-display text-lg font-semibold text-white">
          {player.name}
        </p>
        <p className="truncate text-sm text-slate-400">
          {player.team}
          {player.league_name ? ` · ${player.league_name}` : ""}
        </p>
        {player.position && (
          <p className="mt-1 text-xs font-medium uppercase tracking-wider text-slate-500">
            {player.position}
          </p>
        )}
      </div>
      {selected && (
        <span className="rounded-full bg-accent-primary/20 px-2.5 py-1 text-xs font-semibold text-accent-primary">
          Selected
        </span>
      )}
    </button>
  );
}
