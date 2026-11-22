export type HeatCategory =
  | "normal"
  | "caution"
  | "extreme_caution"
  | "danger"
  | "extreme_danger";

export interface City {
  id: number;
  slug: string;
  name: string;
  state: string;
  country: string;
  latitude: number;
  longitude: number;
}

export interface Observation {
  observed_at: string;
  temperature_c: number;
  humidity_pct: number | null;
  wind_speed_kmh: number | null;
  wind_direction_deg: number | null;
  heat_index_c: number;
  heat_category: HeatCategory;
}

export interface DailySummary {
  day: string;
  temp_min_c: number;
  temp_max_c: number;
  temp_mean_c: number;
  heat_index_max_c: number;
}

export interface HeatSummary {
  city: City;
  current: Observation;
  days: DailySummary[];
  anomaly_c: number | null;
}

export interface RankingItem {
  city: City;
  heat_index_max_c: number;
  heat_category: HeatCategory;
}
