'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import SeasonSelector from '@/components/SeasonSelector';
import RankingTable from '@/components/RankingTable';
import {
  fetchBatterRankings,
  fetchPitcherRankings,
  fetchStandings,
  fetchSeasons,
  fetchStatDefinitions,
  StatDefinition,
} from '@/lib/api';
import { RankingRow, StandingsResponse, LEAGUE_LABELS, LEAGUE_COLORS } from '@/types/index';

export default function Dashboard() {
  const [season, setSeason] = useState<number>(new Date().getFullYear());
  const [batterStats, setBatterStats] = useState<RankingRow[]>([]);
  const [pitcherStats, setPitcherStats] = useState<RankingRow[]>([]);
  const [standings, setStandings] = useState<StandingsResponse | null>(null);
  const [batterStatDef, setBatterStatDef] = useState<StatDefinition | null>(null);
  const [pitcherStatDef, setPitcherStatDef] = useState<StatDefinition | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const defaultMinPA = 300;
  const defaultMinIP = 100;

  // Detect latest available season
  useEffect(() => {
    const detectSeason = async () => {
      try {
        const seasonsResp = await fetchSeasons();
        if (seasonsResp.seasons.length > 0) {
          setSeason(seasonsResp.seasons[0]); // Most recent
        }
      } catch {
        // Keep default
      }
    };
    detectSeason();
  }, []);

  useEffect(() => {
    const loadDashboard = async () => {
      try {
        setLoading(true);
        setError(null);

        // Load standings, batter and pitcher data in parallel
        const [batterDefs, pitcherDefs, standingsData] = await Promise.all([
          fetchStatDefinitions('batter'),
          fetchStatDefinitions('pitcher'),
          fetchStandings(season).catch(() => null),
        ]);

        setStandings(standingsData);

        // Load top 5 batters (OPS if available)
        const batterStat = batterDefs.stats.find((s) => s.stat_key === 'ops') || batterDefs.stats[0];
        if (batterStat) {
          const batterResp = await fetchBatterRankings(batterStat.stat_key, season, {
            limit: 5,
            min_pa: defaultMinPA,
          });
          setBatterStats(batterResp.rows);
          setBatterStatDef(batterStat);
        }

        // Load top 5 pitchers (ERA if available)
        const pitcherStat = pitcherDefs.stats.find((s) => s.stat_key === 'era') || pitcherDefs.stats[0];
        if (pitcherStat) {
          const pitcherResp = await fetchPitcherRankings(pitcherStat.stat_key, season, {
            limit: 5,
            min_ip: defaultMinIP,
          });
          setPitcherStats(pitcherResp.rows);
          setPitcherStatDef(pitcherStat);
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : 'エラーが発生しました');
      } finally {
        setLoading(false);
      }
    };

    loadDashboard();
  }, [season]);

  return (
    <div className="p-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-4xl font-bold text-white mb-2">ダッシュボード</h1>
        <p className="text-gray-400">NPB統計情報の概要</p>
      </div>

      {/* Season Selector */}
      <div className="mb-8 flex items-center gap-4">
        <label className="text-gray-300 font-medium">シーズン選択:</label>
        <SeasonSelector value={season} onChange={setSeason} loading={loading} />
      </div>

      {error && (
        <div className="mb-8 p-4 bg-red-900 border border-red-700 rounded text-red-100">
          エラー: {error}
        </div>
      )}

      {/* Quick Navigation Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
        <Link
          href="/teams"
          className="bg-gradient-to-br from-yellow-600 to-yellow-700 rounded-lg p-6 hover:shadow-lg hover:from-yellow-500 hover:to-yellow-600 transition transform hover:scale-105"
        >
          <div className="text-3xl mb-2">🏆</div>
          <h3 className="text-lg font-bold text-white mb-1">順位表</h3>
          <p className="text-yellow-100 text-sm">セ・パ両リーグ</p>
        </Link>

        <Link
          href="/batters"
          className="bg-gradient-to-br from-blue-600 to-blue-700 rounded-lg p-6 hover:shadow-lg hover:from-blue-500 hover:to-blue-600 transition transform hover:scale-105"
        >
          <div className="text-3xl mb-2">⚾</div>
          <h3 className="text-lg font-bold text-white mb-1">打者ランキング</h3>
          <p className="text-blue-100 text-sm">トップ打者の統計</p>
        </Link>

        <Link
          href="/pitchers"
          className="bg-gradient-to-br from-green-600 to-green-700 rounded-lg p-6 hover:shadow-lg hover:from-green-500 hover:to-green-600 transition transform hover:scale-105"
        >
          <div className="text-3xl mb-2">🎯</div>
          <h3 className="text-lg font-bold text-white mb-1">投手ランキング</h3>
          <p className="text-green-100 text-sm">投手の成績</p>
        </Link>

        <Link
          href="/compare"
          className="bg-gradient-to-br from-purple-600 to-purple-700 rounded-lg p-6 hover:shadow-lg hover:from-purple-500 hover:to-purple-600 transition transform hover:scale-105"
        >
          <div className="text-3xl mb-2">⚖️</div>
          <h3 className="text-lg font-bold text-white mb-1">選手比較</h3>
          <p className="text-purple-100 text-sm">複数選手の比較</p>
        </Link>
      </div>

      {/* League Standings Preview */}
      {standings && standings.leagues.length > 0 && (
        <div className="mb-12">
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-2xl font-bold text-white">
              {season}年 リーグ順位表
            </h2>
            <Link
              href="/teams"
              className="px-4 py-2 bg-yellow-600 hover:bg-yellow-700 rounded text-white transition text-sm"
            >
              詳細を見る
            </Link>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {standings.leagues.map((leagueData) => {
              const colors = LEAGUE_COLORS[leagueData.league] || LEAGUE_COLORS.central;
              return (
                <div
                  key={leagueData.league}
                  className={`bg-gray-800 rounded-lg border ${colors.border} overflow-hidden`}
                >
                  <div className={`px-4 py-3 border-b ${colors.border} ${colors.bg}`}>
                    <h3 className={`text-lg font-bold ${colors.text}`}>
                      {leagueData.league_name_ja}
                    </h3>
                  </div>
                  <div className="overflow-x-auto">
                    <table className="w-full">
                      <thead>
                        <tr className="border-b border-gray-700 text-xs text-gray-400">
                          <th className="px-3 py-2 text-center w-8">#</th>
                          <th className="px-3 py-2 text-left">チーム</th>
                          <th className="px-3 py-2 text-center w-10">勝</th>
                          <th className="px-3 py-2 text-center w-10">敗</th>
                          <th className="px-3 py-2 text-center w-10">分</th>
                          <th className="px-3 py-2 text-center w-14">勝率</th>
                          <th className="px-3 py-2 text-center w-10">差</th>
                        </tr>
                      </thead>
                      <tbody>
                        {leagueData.teams.map((team) => (
                          <tr
                            key={team.team_code}
                            className="border-b border-gray-800 hover:bg-gray-700/50 transition text-sm"
                          >
                            <td className="px-3 py-2 text-center font-bold text-gray-400">
                              {team.rank}
                            </td>
                            <td className="px-3 py-2 font-medium text-gray-200">
                              {team.short_name}
                            </td>
                            <td className="px-3 py-2 text-center text-green-400 font-medium">
                              {team.wins ?? '-'}
                            </td>
                            <td className="px-3 py-2 text-center text-red-400 font-medium">
                              {team.losses ?? '-'}
                            </td>
                            <td className="px-3 py-2 text-center text-gray-400">
                              {team.draws ?? '-'}
                            </td>
                            <td className="px-3 py-2 text-center font-bold text-blue-300">
                              {team.win_pct != null ? team.win_pct.toFixed(3) : '-'}
                            </td>
                            <td className="px-3 py-2 text-center text-gray-400">
                              {team.games_behind != null
                                ? team.games_behind === 0
                                  ? '-'
                                  : team.games_behind.toFixed(1)
                                : '-'}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Batter Rankings Preview */}
      <div className="mb-12 bg-gray-800 rounded-lg border border-gray-700 overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-700 flex justify-between items-center">
          <div>
            <h2 className="text-2xl font-bold text-white">
              トップ打者
              {batterStatDef ? ` (${batterStatDef.display_name_ja})` : ''}
            </h2>
            <p className="text-gray-400 text-sm mt-1">
              {season}年シーズン上位5選手
              {" "}
              (打席{defaultMinPA}以上)
            </p>
          </div>
          <Link
            href="/batters"
            className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded text-white transition"
          >
            すべて表示
          </Link>
        </div>
        <div className="p-6">
          <RankingTable
            data={batterStats}
            statDef={batterStatDef || undefined}
            loading={loading}
          />
        </div>
      </div>

      {/* Pitcher Rankings Preview */}
      <div className="mb-12 bg-gray-800 rounded-lg border border-gray-700 overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-700 flex justify-between items-center">
          <div>
            <h2 className="text-2xl font-bold text-white">
              トップ投手
              {pitcherStatDef ? ` (${pitcherStatDef.display_name_ja})` : ''}
            </h2>
            <p className="text-gray-400 text-sm mt-1">
              {season}年シーズン上位5選手
              {" "}
              (投球回{defaultMinIP}以上)
            </p>
          </div>
          <Link
            href="/pitchers"
            className="px-4 py-2 bg-green-600 hover:bg-green-700 rounded text-white transition"
          >
            すべて表示
          </Link>
        </div>
        <div className="p-6">
          <RankingTable
            data={pitcherStats}
            statDef={pitcherStatDef || undefined}
            loading={loading}
          />
        </div>
      </div>
    </div>
  );
}
