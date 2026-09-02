import type { SportType } from "./common";

export interface PlayerSummary {
  id: number;
  name: string;
  team: string;
  team_id: number | null;
  position: string | null;
  photo_url: string | null;
  league_id: number | null;
  league_name: string | null;
  sport: SportType;
}

export interface League {
  id: number;
  name: string;
  country: string;
  season: number;
}

export interface LeagueSelection {
  id: number;
  season: number;
  name: string;
}
