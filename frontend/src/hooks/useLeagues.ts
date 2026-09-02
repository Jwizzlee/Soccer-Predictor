import { useQuery } from "@tanstack/react-query";
import { fetchLeagues } from "../api/client";
import type { SportType } from "../types/common";

export function useLeagues(sport: SportType = "soccer") {
  return useQuery({
    queryKey: ["leagues", sport],
    queryFn: () => fetchLeagues(sport),
    staleTime: 5 * 60_000,
    retry: 2,
  });
}
