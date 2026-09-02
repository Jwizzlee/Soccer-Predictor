import { useQuery } from "@tanstack/react-query";
import { useAuth } from "@clerk/react-router";
import { fetchSubscriptionStatus } from "../api/client";

export type SubscriptionStatus = {
  active: boolean;
  status: string;
  is_admin: boolean;
};

export function useSubscriptionStatus() {
  const { isLoaded, isSignedIn, getToken } = useAuth();

  return useQuery({
    queryKey: ["billing", "subscription-status"],
    queryFn: async (): Promise<SubscriptionStatus> => {
      const token = await getToken();
      if (!token) {
        throw new Error("Authentication required");
      }
      return fetchSubscriptionStatus(token);
    },
    enabled: isLoaded && isSignedIn,
    staleTime: 60_000,
    retry: 1,
  });
}
