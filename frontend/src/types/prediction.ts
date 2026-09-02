import type { PropType, Recommendation, SportType } from "./common";

export interface SupportingStats {
  last_n: number;
  average: number;
  over_count: number;
  under_count: number;
  push_count: number;
  recent_values: number[];
}

export interface PredictionRequest {
  player_id: number;
  prop_type: PropType;
  line: number;
  last_n_games?: number;
  sport?: SportType;
  league_id?: number | null;
  season?: number | null;
}

export interface PredictionResponse {
  player_id: number;
  player_name: string;
  team_name?: string | null;
  sport: SportType;
  prop_type: PropType;
  line: number;
  recommendation: Recommendation;
  confidence: number;
  reasoning: string;
  key_factors: string[];
  risk_flags: string[];
  supporting_stats: SupportingStats;
  generated_at: string;
}

export interface PredictionHistoryItem {
  id: number;
  player_id?: number | null;
  league_id?: number | null;
  player_name: string;
  team_name?: string | null;
  prop_type: PropType;
  line: number;
  recommendation: Recommendation;
  confidence: number;
  hit_rate: number;
  created_at: string;
}
