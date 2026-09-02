import { useEffect, useRef, useState } from "react";
import { useAuth } from "@clerk/react-router";
import AppShell from "../components/layout/AppShell";
import UpgradeModal from "../components/billing/UpgradeModal";
import PlayerSearch from "../components/players/PlayerSearch";
import PlayerCard from "../components/players/PlayerCard";
import PlayerListSkeleton from "../components/players/PlayerListSkeleton";
import PropSelector, {
  DEFAULT_LAST_N_GAMES,
} from "../components/props/PropSelector";
import PredictionCard from "../components/predictions/PredictionCard";
import RecentPicks from "../components/predictions/RecentPicks";
import AnalysisSkeleton from "../components/predictions/AnalysisSkeleton";
import { fetchPlayer } from "../api/client";
import { useLeagues } from "../hooks/useLeagues";
import { usePlayerSearch } from "../hooks/usePlayers";
import { usePrediction } from "../hooks/usePrediction";
import { usePredictionHistory } from "../hooks/usePredictionHistory";
import { isPaymentRequiredError } from "../api/errors";
import type { PlayerSummary, League } from "../types/player";
import type { PropType } from "../types/common";
import type { PredictionHistoryItem } from "../types/prediction";

const PLAYER_SEARCH_DEBOUNCE_MS = 500;

export default function Dashboard() {
  const { getToken } = useAuth();
  const [search, setSearch] = useState("");
  const [selectedLeague, setSelectedLeague] = useState<League | null>(null);
  const [selected, setSelected] = useState<PlayerSummary | null>(null);
  const [propType, setPropType] = useState<PropType>("shots_on_target");
  const [line, setLine] = useState("1.5");
  const [lastN, setLastN] = useState(DEFAULT_LAST_N_GAMES);
  const [upgradeModalOpen, setUpgradeModalOpen] = useState(false);
  const [selectedPickId, setSelectedPickId] = useState<number | null>(null);
  const [pickLoadError, setPickLoadError] = useState<string | null>(null);
  const propAnalysisRef = useRef<HTMLElement>(null);

  const {
    data: leaguesData,
    isLoading: leaguesLoading,
    isError: leaguesError,
    error: leaguesQueryError,
    refetch: refetchLeagues,
  } = useLeagues("soccer");

  const leagues = leaguesData?.leagues ?? [];

  useEffect(() => {
    if (leagues.length > 0 && !selectedLeague) {
      setSelectedLeague(leagues[0]);
    }
  }, [leagues, selectedLeague]);

  const {
    data: players,
    isLoading: searching,
    isDebouncing,
    debouncedQuery,
    minSearchLength,
  } = usePlayerSearch(
    search,
    "soccer",
    selectedLeague?.id,
    selectedLeague?.season,
    PLAYER_SEARCH_DEBOUNCE_MS
  );

  const prediction = usePrediction();
  const history = usePredictionHistory();

  const showPredictionError =
    prediction.isError && !isPaymentRequiredError(prediction.error);

  const handleLeagueChange = (league: League) => {
    setSelectedLeague(league);
    setSelected(null);
  };

  const handleAnalyze = async () => {
    if (!selected || !selectedLeague) return;
    const lineNum = parseFloat(line);
    if (Number.isNaN(lineNum) || lineNum <= 0) return;

    const authToken = await getToken();
    if (!authToken) return;

    prediction.mutate(
      {
        player_id: selected.id,
        prop_type: propType,
        line: lineNum,
        last_n_games: lastN,
        sport: "soccer",
        league_id: selected.league_id ?? selectedLeague.id,
        season: selectedLeague.season,
        authToken,
      },
      {
        onError: (error) => {
          if (isPaymentRequiredError(error)) {
            setUpgradeModalOpen(true);
          }
        },
      }
    );
  };

  const handlePickSelect = async (item: PredictionHistoryItem) => {
    if (!item.player_id) return;

    setSelectedPickId(item.id);
    setPickLoadError(null);
    setPropType(item.prop_type);
    setLine(String(item.line));

    const league =
      item.league_id != null
        ? leagues.find((entry) => entry.id === item.league_id) ?? selectedLeague
        : selectedLeague;

    if (league) {
      setSelectedLeague(league);
    }

    const leagueId = item.league_id ?? league?.id;
    const season = league?.season ?? selectedLeague?.season;

    try {
      const player = await fetchPlayer(item.player_id, "soccer", leagueId, season);
      setSelected(player);
      setSearch(player.name);
    } catch {
      const fallback: PlayerSummary = {
        id: item.player_id,
        name: item.player_name,
        team: item.team_name ?? "",
        team_id: null,
        position: null,
        photo_url: null,
        league_id: leagueId ?? null,
        league_name: league?.name ?? null,
        sport: "soccer",
      };
      setSelected(fallback);
      setSearch(item.player_name);
      setPickLoadError(
        "Loaded saved prop settings. Player details may be limited — re-run analyze to refresh."
      );
    }

    propAnalysisRef.current?.scrollIntoView({ behavior: "smooth", block: "start" });
  };

  const showPlayerSkeleton =
    (searching || isDebouncing) &&
    search.trim().length >= minSearchLength &&
    !!selectedLeague;

  return (
    <AppShell wide>
      <UpgradeModal
        open={upgradeModalOpen}
        onClose={() => setUpgradeModalOpen(false)}
      />

      <div className="mb-8">
        <h1 className="section-title">Live prop dashboard</h1>
        <p className="section-subtitle mt-1">
          Search players, configure lines, and run AI analysis
        </p>
      </div>

      <section className="mb-10">
        {leaguesError && (
          <div className="mb-4 rounded-lg border border-accent-under/30 bg-accent-under/10 px-4 py-3 text-sm text-accent-under">
            <p>
              Could not load competitions:{" "}
              {leaguesQueryError instanceof Error
                ? leaguesQueryError.message
                : "Request failed"}
            </p>
            <p className="mt-1 text-xs text-slate-400">
              Ensure the backend is running on port 8000 and{" "}
              <code className="text-slate-300">pip install -r requirements.txt</code>{" "}
              has been run.
            </p>
            <button
              type="button"
              onClick={() => refetchLeagues()}
              className="mt-3 rounded-lg border border-white/10 bg-white/5 px-3 py-1.5 text-xs font-medium text-white hover:bg-white/10"
            >
              Retry
            </button>
          </div>
        )}

        <PlayerSearch
          value={search}
          onChange={setSearch}
          leagueId={selectedLeague?.id}
          season={selectedLeague?.season}
          onLeagueChange={handleLeagueChange}
          leagues={leagues}
          loading={leaguesLoading}
        />
      </section>

      <div className="grid gap-10 xl:grid-cols-12">
        <section className="xl:col-span-5">
          <div className="mb-5">
            <h2 className="font-display text-lg font-semibold text-white">
              Players
            </h2>
            <p className="section-subtitle">
              {selectedLeague
                ? `${selectedLeague.name} · ${selectedLeague.season} season`
                : leaguesLoading
                  ? "Loading competitions…"
                  : leaguesError
                    ? "Competitions unavailable"
                    : "No competitions available"}
            </p>
          </div>

          {search.trim().length > 0 && search.trim().length < minSearchLength && (
            <p className="mb-4 text-sm text-slate-500">
              Type at least {minSearchLength} characters to search.
            </p>
          )}

          {showPlayerSkeleton && <PlayerListSkeleton rows={4} />}

          {!showPlayerSkeleton &&
            !searching &&
            !isDebouncing &&
            debouncedQuery.length >= minSearchLength &&
            players?.length === 0 && (
              <p className="glass-panel p-6 text-center text-sm text-slate-500">
                No players found for this competition.
              </p>
            )}

          {!showPlayerSkeleton && (
            <div className="grid gap-3">
              {players?.map((p) => (
                <PlayerCard
                  key={p.id}
                  player={p}
                  selected={selected?.id === p.id}
                  onSelect={() => setSelected(p)}
                />
              ))}
            </div>
          )}
        </section>

        <section ref={propAnalysisRef} className="xl:col-span-7 scroll-mt-24">
          <div className="mb-5">
            <h2 className="font-display text-lg font-semibold text-white">
              Prop analysis
            </h2>
            <p className="section-subtitle">
              Configure your line and run the AI engine
            </p>
          </div>

          {!selected ? (
            <div className="glass-panel flex min-h-[280px] flex-col items-center justify-center border-dashed p-10 text-center">
              <p className="font-display text-lg font-medium text-slate-300">
                Select a player
              </p>
              <p className="mt-2 max-w-sm text-sm text-slate-500">
                Choose a competitor from the list to configure goals, assists,
                shots, or shots on target props.
              </p>
            </div>
          ) : (
            <div className="glass-panel space-y-6 p-6 md:p-8">
              <div className="flex items-center gap-4 border-b border-white/10 pb-5">
                {selected.photo_url && (
                  <img
                    src={selected.photo_url}
                    alt=""
                    className="h-16 w-16 rounded-2xl border border-white/10 object-cover"
                  />
                )}
                <div>
                  <p className="font-display text-xl font-bold text-white">
                    {selected.name}
                  </p>
                  <p className="text-sm text-slate-400">
                    {selected.team} · {selectedLeague?.name}
                  </p>
                </div>
              </div>

              <PropSelector
                propType={propType}
                line={line}
                lastNGames={lastN}
                onPropChange={setPropType}
                onLineChange={setLine}
                onLastNChange={setLastN}
                disabled={prediction.isPending}
              />

              <button
                type="button"
                onClick={handleAnalyze}
                disabled={prediction.isPending}
                className="w-full rounded-xl bg-gradient-to-r from-accent-primary to-accent-glow py-3.5 text-sm font-bold uppercase tracking-wider text-white shadow-lg shadow-accent-primary/25 transition-all duration-200 ease-in-out hover:scale-[1.01] hover:shadow-accent-primary/40 disabled:scale-100 disabled:opacity-50"
              >
                {prediction.isPending ? "Analyzing…" : "Analyze prop"}
              </button>

              {pickLoadError && (
                <p className="rounded-lg border border-amber-400/30 bg-amber-400/10 px-4 py-3 text-sm text-amber-200">
                  {pickLoadError}
                </p>
              )}

              {showPredictionError && (
                <p className="rounded-lg border border-accent-under/30 bg-accent-under/10 px-4 py-3 text-sm text-accent-under">
                  {prediction.error?.message}
                </p>
              )}
            </div>
          )}

          {prediction.isPending && <AnalysisSkeleton />}

          {prediction.data && !prediction.isPending && (
            <PredictionCard prediction={prediction.data} />
          )}
        </section>
      </div>

      <RecentPicks
        items={history.data ?? []}
        isLoading={history.isLoading}
        isError={history.isError}
        selectedPickId={selectedPickId}
        onSelectPick={handlePickSelect}
      />
    </AppShell>
  );
}
