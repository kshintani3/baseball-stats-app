import {
  Player,
  RankingResponse,
  ComparisonResponse,
  StatsMetaResponse,
  SeasonsResponse,
  TeamsMetaResponse,
  StandingsResponse,
  BatterSeasonStats,
  PitcherSeasonStats,
  PlayerStats,
  StatDefinition,
} from '@/types/index';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

async function apiCall<T>(endpoint: string, params?: Record<string, any>): Promise<T> {
  let url = `${API_BASE}${endpoint}`;

  if (params) {
    const query = new URLSearchParams();
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== '') {
        query.append(key, String(value));
      }
    });
    const queryString = query.toString();
    if (queryString) {
      url += `?${queryString}`;
    }
  }

  const response = await fetch(url);
  if (!response.ok) {
    throw new Error(`API error: ${response.status} ${response.statusText}`);
  }
  return response.json();
}

export async function fetchBatterRankings(
  statKey: string,
  season: number,
  options?: {
    team_code?: string;
    league?: string;
    min_pa?: number;
    limit?: number;
    order?: string;
  }
): Promise<RankingResponse> {
  return apiCall('/api/rankings/batters', {
    stat_key: statKey,
    season,
    team_code: options?.team_code,
    league: options?.league,
    min_pa: options?.min_pa,
    limit: options?.limit || 20,
    order: options?.order,
  });
}

export async function fetchPitcherRankings(
  statKey: string,
  season: number,
  options?: {
    team_code?: string;
    league?: string;
    role?: string;
    min_ip?: number;
    limit?: number;
    order?: string;
  }
): Promise<RankingResponse> {
  return apiCall('/api/rankings/pitchers', {
    stat_key: statKey,
    season,
    team_code: options?.team_code,
    league: options?.league,
    role: options?.role,
    min_ip: options?.min_ip,
    limit: options?.limit || 20,
    order: options?.order,
  });
}

export async function fetchTeamRankings(
  statKey: string,
  season: number,
  options?: {
    league?: string;
    limit?: number;
    order?: string;
  }
): Promise<RankingResponse> {
  return apiCall('/api/rankings/teams', {
    stat_key: statKey,
    season,
    league: options?.league,
    limit: options?.limit || 20,
    order: options?.order,
  });
}

export async function fetchStandings(
  season: number,
  league?: string
): Promise<StandingsResponse> {
  return apiCall('/api/standings', {
    season,
    league,
  });
}

export async function fetchPlayer(playerId: number): Promise<Player> {
  return apiCall(`/api/players/${playerId}`);
}

export async function searchPlayers(
  query: string,
  options?: { team_code?: string; league?: string; limit?: number }
): Promise<Player[]> {
  return apiCall('/api/players/search', {
    q: query,
    team_code: options?.team_code,
    league: options?.league,
    limit: options?.limit || 20,
  });
}

export async function fetchPlayerStats(
  playerId: number,
  type: 'batter' | 'pitcher'
): Promise<PlayerStats[]> {
  return apiCall(`/api/players/${playerId}/stats`, { type });
}

export async function fetchComparePlayersStats(
  ids: number[],
  season: number,
  type: 'batter' | 'pitcher'
): Promise<ComparisonResponse> {
  const idsParam = ids.join(',');
  return apiCall('/api/compare/players', {
    ids: idsParam,
    season,
    type,
  });
}

export async function fetchCompareTeamsStats(
  codes: string[],
  season: number
): Promise<ComparisonResponse> {
  const codesParam = codes.join(',');
  return apiCall('/api/compare/teams', {
    codes: codesParam,
    season,
  });
}

export async function fetchStatDefinitions(
  category?: 'batter' | 'pitcher' | 'team'
): Promise<StatsMetaResponse> {
  return apiCall('/api/meta/stats', { category });
}

export async function fetchSeasons(): Promise<SeasonsResponse> {
  return apiCall('/api/meta/seasons');
}

export async function fetchTeams(league?: string): Promise<TeamsMetaResponse> {
  return apiCall('/api/meta/teams', { league });
}

export type { StatDefinition } from '@/types/index';
