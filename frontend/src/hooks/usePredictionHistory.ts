import { useQuery } from "@tanstack/react-query";
import { useAuth } from "@clerk/react-router";
import { fetchPredictionHistory } from "../api/client";

export function usePredictionHistory() {
  const { isLoaded, isSignedIn, getToken } = useAuth();

  return useQuery({
    queryKey: ["predictions", "history"],
    queryFn: async () => {
      const token = await getToken();
      if (!token) {
        throw new Error("Authentication required");
      }
      return fetchPredictionHistory(token);
    },
    enabled: isLoaded && isSignedIn,
    staleTime: 30_000,
  });
}
