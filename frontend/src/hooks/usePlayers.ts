import { useQuery } from "@tanstack/react-query";
import { searchPlayers } from "../api/client";
import type { SportType } from "../types/common";
import { useDebouncedValue } from "./useDebouncedValue";

const MIN_SEARCH_LENGTH = 3;
const DEFAULT_DEBOUNCE_MS = 500;

export function usePlayerSearch(
  query: string,
  sport: SportType = "soccer",
  leagueId?: number,
  season?: number,
  debounceMs: number = DEFAULT_DEBOUNCE_MS
) {
  const debouncedQuery = useDebouncedValue(query.trim(), debounceMs);
  const canSearch =
    debouncedQuery.length >= MIN_SEARCH_LENGTH &&
    leagueId !== undefined &&
    season !== undefined;

  const result = useQuery({
    queryKey: ["players", "search", debouncedQuery, sport, leagueId, season],
    queryFn: () => searchPlayers(debouncedQuery, sport, leagueId, season),
    enabled: canSearch,
  });

  return {
    ...result,
    debouncedQuery,
    minSearchLength: MIN_SEARCH_LENGTH,
    isDebouncing: canSearch && query.trim() !== debouncedQuery,
  };
}
