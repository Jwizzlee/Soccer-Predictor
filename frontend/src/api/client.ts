import type { PlayerSummary, League } from "../types/player";
import type { PredictionRequest, PredictionResponse, PredictionHistoryItem } from "../types/prediction";
import type { SportType } from "../types/common";
import { ApiError } from "./errors";

const API_BASE = import.meta.env.VITE_API_URL ?? "";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...init?.headers,
    },
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    const detail = err.detail;
    const message =
      typeof detail === "string"
        ? detail
        : Array.isArray(detail)
          ? detail.map((item: { msg?: string }) => item.msg ?? "").join(", ")
          : "Request failed";
    throw new ApiError(message || "Request failed", res.status);
  }
  return res.json();
}

export async function fetchLeagues(sport: SportType = "soccer") {
  return request<{ sport: string; leagues: League[] }>(
    `/api/v1/leagues?sport=${sport}`
  );
}

export async function searchPlayers(
  query: string,
  sport: SportType = "soccer",
  leagueId?: number,
  season?: number
) {
  const params = new URLSearchParams({ q: query, sport });
  if (leagueId) params.set("league_id", String(leagueId));
  if (season) params.set("season", String(season));
  return request<PlayerSummary[]>(`/api/v1/players/search?${params}`);
}

export async function fetchPlayer(
  playerId: number,
  sport: SportType = "soccer",
  leagueId?: number,
  season?: number
) {
  const params = new URLSearchParams({ sport });
  if (leagueId) params.set("league_id", String(leagueId));
  if (season) params.set("season", String(season));
  return request<PlayerSummary>(`/api/v1/players/${playerId}?${params}`);
}

export async function createPrediction(
  body: PredictionRequest,
  authToken: string
) {
  return request<PredictionResponse>("/api/v1/predict", {
    method: "POST",
    headers: {
      Authorization: `Bearer ${authToken}`,
    },
    body: JSON.stringify(body),
  });
}

export async function fetchPredictionHistory(authToken: string) {
  return request<PredictionHistoryItem[]>("/api/v1/predictions/history", {
    headers: {
      Authorization: `Bearer ${authToken}`,
    },
  });
}

export async function fetchSubscriptionStatus(authToken: string) {
  return request<{ active: boolean; status: string; is_admin: boolean }>(
    "/api/v1/billing/subscription-status",
    {
      headers: {
        Authorization: `Bearer ${authToken}`,
      },
    }
  );
}

export async function createCheckoutSession(authToken: string) {
  return request<{ url: string; session_id: string }>(
    "/api/v1/billing/create-checkout-session",
    {
      method: "POST",
      headers: {
        Authorization: `Bearer ${authToken}`,
      },
    }
  );
}

export async function createCustomerPortalSession(authToken: string) {
  return request<{ url: string }>("/api/v1/billing/customer-portal", {
    method: "POST",
    headers: {
      Authorization: `Bearer ${authToken}`,
    },
  });
}
