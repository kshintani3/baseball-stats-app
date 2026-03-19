export interface StatDefinition {
  id: number;
  stat_key: string;
  display_name_ja: string;
  display_name_en: string;
  category: 'batter' | 'pitcher' | 'team';
  display_order: number;
  decimal_places: number;
  sort_direction: string;
  is_ranking_eligible: boolean;
  is_comparable: boolean;
  is_graphable: boolean;
  is_rate_stat: boolean;
  description?: string;
  created_at: string;
  updated_at: string;
}

export interface Team {
  id: number;
  code: string;
  name_ja: string;
  name_en: string;
  short_name: string;
  league: string;
}

export interface Player {
  id: number;
  npb_id: string;
  name_ja: string;
  name_en: string;
  position?: string;
  bats?: string;
  throws?: string;
  birth_date?: string;
  jersey_number?: number;
  is_active: boolean;
  team_id: number;
  team?: Team;
  created_at: string;
  updated_at: string;
}

export interface BatterSeasonStats {
  id: number;
  player_id: number;
  season: number;
  games?: number;
  plate_appearances?: number;
  at_bats?: number;
  hits?: number;
  doubles?: number;
  triples?: number;
  home_runs?: number;
  rbi?: number;
  runs?: number;
  strikeouts?: number;
  walks?: number;
  hit_by_pitch?: number;
  stolen_bases?: number;
  batting_average?: number;
  on_base_pct?: number;
  slugging_pct?: number;
  ops?: number;
  created_at: string;
  updated_at: string;
}

export interface PitcherSeasonStats {
  id: number;
  player_id: number;
  season: number;
  games?: number;
  games_started?: number;
  wins?: number;
  losses?: number;
  saves?: number;
  holds?: number;
  innings_pitched?: number;
  hits_allowed?: number;
  home_runs_allowed?: number;
  strikeouts?: number;
  walks_allowed?: number;
  runs_allowed?: number;
  earned_runs?: number;
  era?: number;
  whip?: number;
  created_at: string;
  updated_at: string;
}

export type PlayerStats = BatterSeasonStats | PitcherSeasonStats;

export interface TeamSeasonStats {
  id: number;
  team_id: number;
  season: number;
  games?: number;
  wins?: number;
  losses?: number;
  draws?: number;
  win_pct?: number;
  runs_scored?: number;
  runs_allowed?: number;
  home_runs?: number;
  stolen_bases?: number;
  team_batting_avg?: number;
  team_era?: number;
  created_at: string;
  updated_at: string;
}

export interface RankingRow {
  rank: number;
  player_id?: number;
  team_id?: number;
  name_ja: string;
  name_en: string;
  team_code?: string;
  team_short_name?: string;
  stat_value?: number;
  position?: string;
}

export interface RankingResponse {
  stat_key: string;
  stat_name_ja: string;
  stat_name_en: string;
  season: number;
  category: string;
  sort_direction: string;
  decimal_places: number;
  rows: RankingRow[];
  total_count: number;
  returned_count: number;
}

export interface ComparisonRow {
  id: number;
  name_ja: string;
  name_en: string;
  team_code?: string;
  team_short_name?: string;
  position?: string;
  stats: Record<string, number | null>;
}

export interface ComparisonResponse {
  category: string;
  season: number;
  stat_keys: string[];
  rows: ComparisonRow[];
}

export interface StatsMetaResponse {
  category: string;
  stats: StatDefinition[];
}

export interface SeasonsResponse {
  seasons: number[];
}

export interface TeamsMetaResponse {
  teams: Team[];
}
