import type { League } from "../../types/player";

interface PlayerSearchProps {
  value: string;
  onChange: (value: string) => void;
  leagueId: number | undefined;
  season: number | undefined;
  onLeagueChange: (league: League) => void;
  leagues: League[];
  loading?: boolean;
}

export default function PlayerSearch({
  value,
  onChange,
  leagueId,
  season,
  onLeagueChange,
  leagues,
  loading = false,
}: PlayerSearchProps) {
  const selectedKey =
    leagueId !== undefined && season !== undefined
      ? `${leagueId}-${season}`
      : "";

  return (
    <div className="glass-panel p-5">
      <div className="mb-4 flex flex-col gap-1 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <h2 className="section-title">Scout players</h2>
          <p className="section-subtitle">
            Select a competition, then search by name
          </p>
        </div>
      </div>
      <div className="flex flex-col gap-4 lg:flex-row">
        <select
          value={selectedKey}
          disabled={loading || leagues.length === 0}
          onChange={(e) => {
            const league = leagues.find(
              (l) => `${l.id}-${l.season}` === e.target.value
            );
            if (league) onLeagueChange(league);
          }}
          className="glass-input lg:w-72 disabled:cursor-not-allowed disabled:opacity-60"
        >
          {loading || leagues.length === 0 ? (
            <option value="">
              {loading ? "Loading competitions…" : "No competitions available"}
            </option>
          ) : (
            leagues.map((l) => (
              <option key={`${l.id}-${l.season}`} value={`${l.id}-${l.season}`}>
                {l.name} · Season {l.season}
              </option>
            ))
          )}
        </select>
        <input
          type="search"
          placeholder="Search player (min 3 characters)..."
          value={value}
          onChange={(e) => onChange(e.target.value)}
          className="glass-input flex-1"
        />
      </div>
    </div>
  );
}
