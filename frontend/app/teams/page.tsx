'use client';

import { Suspense, useEffect, useState } from 'react';
import { useSearchParams, useRouter } from 'next/navigation';
import SeasonSelector from '@/components/SeasonSelector';
import StatSelector from '@/components/StatSelector';
import LeagueFilter from '@/components/LeagueFilter';
import RankingTable from '@/components/RankingTable';
import { fetchStandings, fetchTeamRankings, fetchStatDefinitions, StatDefinition } from '@/lib/api';
import { StandingsResponse, LeagueStandings, RankingRow, LEAGUE_LABELS, LEAGUE_COLORS } from '@/types/index';

type ViewMode = 'standings' | 'ranking';

export default function TeamsPageWrapper() {
  return (
    <Suspense fallback={<div className="p-8 text-gray-400">読み込み中...</div>}>
      <TeamsPage />
    </Suspense>
  );
}

function TeamsPage() {
  const router = useRouter();
  const searchParams = useSearchParams();

  const [season, setSeason] = useState<number>(parseInt(searchParams.get('season') || '2024'));
  const [viewMode, setViewMode] = useState<ViewMode>(
    (searchParams.get('view') as ViewMode) || 'standings'
  );
  const [statKey, setStatKey] = useState(searchParams.get('stat_key') || '');
  const [league, setLeague] = useState(searchParams.get('league') || '');

  const [standings, setStandings] = useState<StandingsResponse | null>(null);
  const [rankings, setRankings] = useState<RankingRow[]>([]);
  const [statDef, setStatDef] = useState<StatDefinition | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Initialize default stat for ranking mode
  useEffect(() => {
    const initStat = async () => {
      if (viewMode === 'ranking' && !statKey) {
        try {
          const response = await fetchStatDefinitions('team');
          if (response.stats.length > 0) {
            setStatKey(response.stats[0].stat_key);
          }
        } catch {
          // Fallback
        }
      }
    };
    initStat();
  }, [viewMode, statKey]);

  // Update URL params
  useEffect(() => {
    const params = new URLSearchParams({
      season: season.toString(),
      view: viewMode,
    });
    if (statKey && viewMode === 'ranking') {
      params.append('stat_key', statKey);
    }
    if (league) {
      params.append('league', league);
    }
    router.push(`/teams?${params.toString()}`);
  }, [season, viewMode, statKey, league, router]);

  // Load data based on view mode
  useEffect(() => {
    const loadData = async () => {
      try {
        setLoading(true);
        setError(null);

        if (viewMode === 'standings') {
          const response = await fetchStandings(season, league || undefined);
          setStandings(response);
        } else {
          if (!statKey) return;

          const response = await fetchTeamRankings(statKey, season, {
            league: league || undefined,
          });
          setRankings(response.rows);

          const defs = await fetchStatDefinitions('team');
          const def = defs.stats.find((s) => s.stat_key === statKey);
          setStatDef(def || null);
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : 'エラーが発生しました');
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, [viewMode, statKey, season, league]);

  const renderStandingsTable = (leagueData: LeagueStandings) => {
    const colors = LEAGUE_COLORS[leagueData.league] || LEAGUE_COLORS.central;

    return (
      <div
        key={leagueData.league}
        className={`bg-gray-800 rounded-lg border ${colors.border} overflow-hidden`}
      >
        <div className={`px-6 py-4 border-b ${colors.border} ${colors.bg}`}>
          <h2 className={`text-xl font-bold ${colors.text}`}>
            {leagueData.league_name_ja}
          </h2>
          <p className="text-gray-400 text-sm mt-1">{season}年シーズン</p>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-gray-700 bg-gray-900">
                <th className="px-4 py-3 text-center text-sm font-semibold text-gray-300 w-12">
                  順位
                </th>
                <th className="px-4 py-3 text-left text-sm font-semibold text-gray-300">
                  チーム
                </th>
                <th className="px-4 py-3 text-center text-sm font-semibold text-gray-300 w-14">
                  試合
                </th>
                <th className="px-4 py-3 text-center text-sm font-semibold text-gray-300 w-14">
                  勝
                </th>
                <th className="px-4 py-3 text-center text-sm font-semibold text-gray-300 w-14">
                  敗
                </th>
                <th className="px-4 py-3 text-center text-sm font-semibold text-gray-300 w-14">
                  分
                </th>
                <th className="px-4 py-3 text-center text-sm font-semibold text-gray-300 w-16">
                  勝率
                </th>
                <th className="px-4 py-3 text-center text-sm font-semibold text-gray-300 w-14">
                  差
                </th>
                <th className="px-4 py-3 text-center text-sm font-semibold text-gray-300 w-14 hidden lg:table-cell">
                  得点
                </th>
                <th className="px-4 py-3 text-center text-sm font-semibold text-gray-300 w-14 hidden lg:table-cell">
                  失点
                </th>
                <th className="px-4 py-3 text-center text-sm font-semibold text-gray-300 w-14 hidden lg:table-cell">
                  本塁打
                </th>
                <th className="px-4 py-3 text-center text-sm font-semibold text-gray-300 w-16 hidden xl:table-cell">
                  打率
                </th>
                <th className="px-4 py-3 text-center text-sm font-semibold text-gray-300 w-16 hidden xl:table-cell">
                  防御率
                </th>
              </tr>
            </thead>
            <tbody>
              {leagueData.teams.map((team) => (
                <tr
                  key={team.team_code}
                  className="border-b border-gray-800 hover:bg-gray-700/50 transition"
                >
                  <td className="px-4 py-4 text-center">
                    <span
                      className={`inline-flex items-center justify-center w-8 h-8 rounded-full font-bold text-sm ${
                        team.rank === 1
                          ? 'bg-yellow-500/20 text-yellow-400'
                          : team.rank === 2
                          ? 'bg-gray-400/20 text-gray-300'
                          : team.rank === 3
                          ? 'bg-orange-600/20 text-orange-400'
                          : 'text-gray-400'
                      }`}
                    >
                      {team.rank}
                    </span>
                  </td>
                  <td className="px-4 py-4">
                    <div className="flex flex-col">
                      <span className="text-gray-100 font-semibold text-sm">
                        {team.name_ja}
                      </span>
                      <span className="text-gray-500 text-xs">{team.name_en}</span>
                    </div>
                  </td>
                  <td className="px-4 py-4 text-center text-sm text-gray-300">
                    {team.games ?? '-'}
                  </td>
                  <td className="px-4 py-4 text-center text-sm font-semibold text-green-400">
                    {team.wins ?? '-'}
                  </td>
                  <td className="px-4 py-4 text-center text-sm font-semibold text-red-400">
                    {team.losses ?? '-'}
                  </td>
                  <td className="px-4 py-4 text-center text-sm text-gray-400">
                    {team.draws ?? '-'}
                  </td>
                  <td className="px-4 py-4 text-center text-sm font-bold text-blue-300">
                    {team.win_pct != null ? team.win_pct.toFixed(3) : '-'}
                  </td>
                  <td className="px-4 py-4 text-center text-sm text-gray-400">
                    {team.games_behind != null
                      ? team.games_behind === 0
                        ? '-'
                        : team.games_behind.toFixed(1)
                      : '-'}
                  </td>
                  <td className="px-4 py-4 text-center text-sm text-gray-300 hidden lg:table-cell">
                    {team.runs_scored ?? '-'}
                  </td>
                  <td className="px-4 py-4 text-center text-sm text-gray-300 hidden lg:table-cell">
                    {team.runs_allowed ?? '-'}
                  </td>
                  <td className="px-4 py-4 text-center text-sm text-gray-300 hidden lg:table-cell">
                    {team.home_runs ?? '-'}
                  </td>
                  <td className="px-4 py-4 text-center text-sm text-gray-300 hidden xl:table-cell">
                    {team.team_batting_avg != null
                      ? team.team_batting_avg.toFixed(3)
                      : '-'}
                  </td>
                  <td className="px-4 py-4 text-center text-sm text-gray-300 hidden xl:table-cell">
                    {team.team_era != null ? team.team_era.toFixed(2) : '-'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    );
  };

  return (
    <div className="p-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-4xl font-bold text-white mb-2">チーム・順位表</h1>
        <p className="text-gray-400">NPBのチーム成績と順位表</p>
      </div>

      {/* Controls */}
      <div className="mb-8 bg-gray-800 rounded-lg border border-gray-700 p-6">
        <div className="flex flex-col md:flex-row gap-4 items-start md:items-end">
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              シーズン
            </label>
            <SeasonSelector value={season} onChange={setSeason} />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              リーグ
            </label>
            <LeagueFilter value={league} onChange={setLeague} />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              表示モード
            </label>
            <div className="flex rounded overflow-hidden border border-gray-600">
              <button
                onClick={() => setViewMode('standings')}
                className={`px-4 py-2 text-sm font-medium transition ${
                  viewMode === 'standings'
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                }`}
              >
                順位表
              </button>
              <button
                onClick={() => setViewMode('ranking')}
                className={`px-4 py-2 text-sm font-medium transition ${
                  viewMode === 'ranking'
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                }`}
              >
                統計ランキング
              </button>
            </div>
          </div>

          {viewMode === 'ranking' && (
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                統計項目
              </label>
              <StatSelector category="team" value={statKey} onChange={setStatKey} />
            </div>
          )}
        </div>
      </div>

      {error && (
        <div className="mb-8 p-4 bg-red-900 border border-red-700 rounded text-red-100">
          エラー: {error}
        </div>
      )}

      {loading ? (
        <div className="flex justify-center items-center py-12">
          <div className="text-gray-400">読み込み中...</div>
        </div>
      ) : viewMode === 'standings' ? (
        /* Standings View */
        <div className="space-y-8">
          {standings?.leagues.map((leagueData) => renderStandingsTable(leagueData))}
          {(!standings || standings.leagues.length === 0) && (
            <div className="flex justify-center items-center py-12">
              <div className="text-gray-400">データがありません</div>
            </div>
          )}
        </div>
      ) : (
        /* Ranking View */
        <div className="bg-gray-800 rounded-lg border border-gray-700 overflow-hidden">
          <div className="px-6 py-4 border-b border-gray-700">
            <h2 className="text-lg font-semibold text-white">
              チームランキング {statDef ? `(${statDef.display_name_ja})` : ''}
              {league && ` - ${LEAGUE_LABELS[league]}`}
            </h2>
          </div>

          {rankings.length === 0 ? (
            <div className="flex justify-center items-center py-12">
              <div className="text-gray-400">データがありません</div>
            </div>
          ) : (
            <div className="p-6">
              <RankingTable
                data={rankings}
                statDef={statDef || undefined}
                loading={loading}
              />
            </div>
          )}
        </div>
      )}
    </div>
  );
}
