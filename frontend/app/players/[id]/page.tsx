'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { fetchPlayer, fetchPlayerStats, fetchStatDefinitions, StatDefinition } from '@/lib/api';
import { Player, PlayerStats, LEAGUE_LABELS } from '@/types/index';
import StatsChart from '@/components/StatsChart';

interface PlayerDetailProps {
  params: {
    id: string;
  };
}

export default function PlayerDetail({ params }: PlayerDetailProps) {
  const router = useRouter();
  const playerId = parseInt(params.id);

  const [player, setPlayer] = useState<Player | null>(null);
  const [stats, setStats] = useState<PlayerStats[]>([]);
  const [playerType, setPlayerType] = useState<'batter' | 'pitcher'>('batter');
  const [statDefs, setStatDefs] = useState<StatDefinition[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedSeason, setSelectedSeason] = useState<number | null>(null);

  // Load player data
  useEffect(() => {
    const loadPlayer = async () => {
      try {
        setLoading(true);
        setError(null);
        const response = await fetchPlayer(playerId);
        setPlayer(response);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'エラーが発生しました');
      }
    };

    loadPlayer();
  }, [playerId]);

  // Load player stats
  useEffect(() => {
    if (!player) return;

    const loadStats = async () => {
      try {
        setLoading(true);
        setError(null);

        // Determine player type based on position
        const type = player.position?.includes('投') ? 'pitcher' : 'batter';
        setPlayerType(type);

        const response = await fetchPlayerStats(playerId, type);
        setStats(response);

        if (response.length > 0) {
          setSelectedSeason(response[0].season);
        }

        // Load stat definitions
        const defs = await fetchStatDefinitions(type);
        setStatDefs(defs.stats);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'エラーが発生しました');
      } finally {
        setLoading(false);
      }
    };

    loadStats();
  }, [player, playerId]);

  if (error && !player) {
    return (
      <div className="p-8">
        <div className="text-center">
          <p className="text-red-400 mb-4">エラー: {error}</p>
          <Link href="/batters" className="text-blue-400 hover:text-blue-300">
            戻る
          </Link>
        </div>
      </div>
    );
  }

  if (loading || !player) {
    return (
      <div className="p-8">
        <div className="text-center text-gray-400">読み込み中...</div>
      </div>
    );
  }

  const selectedStats = selectedSeason
    ? stats.find((s) => s.season === selectedSeason)
    : null;

  const chartData = stats
    .map((s) => {
      const mainStat = statDefs[0];
      const value = mainStat ? (s as any)[mainStat.stat_key] : 0;
      return {
        season: s.season,
        [mainStat?.stat_key || 'stat']: value,
      };
    })
    .sort((a, b) => a.season - b.season);

  // Build throw/bat display
  const throwHand = player.throws === 'R' ? '右投' : player.throws === 'L' ? '左投' : player.throws || '-';
  const batHand = player.bats === 'R' ? '右打' : player.bats === 'L' ? '左打' : player.bats === 'S' ? '両打' : player.bats || '-';
  const throwBatDisplay = `${throwHand}${batHand}`;

  return (
    <div className="p-8">
      {/* Back link */}
      <Link
        href={playerType === 'pitcher' ? '/pitchers' : '/batters'}
        className="text-blue-400 hover:text-blue-300 mb-6 inline-block transition"
      >
        ← 戻る
      </Link>

      {/* Player Info Header */}
      <div className="mb-8 bg-gradient-to-r from-blue-600 to-blue-500 rounded-lg p-8">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          <div>
            <h1 className="text-4xl font-bold text-white mb-2">{player.name_ja}</h1>
            <p className="text-blue-100 text-xl mb-4">{player.name_en}</p>

            {/* Team & League badge */}
            {player.team && (
              <div className="mb-4 flex items-center gap-2">
                <span className="text-white font-medium">{player.team.name_ja}</span>
                <span
                  className={`inline-block px-2 py-0.5 rounded text-xs font-medium ${
                    player.team.league === 'central'
                      ? 'bg-orange-500/30 text-orange-200 border border-orange-400/50'
                      : 'bg-blue-500/30 text-blue-200 border border-blue-400/50'
                  }`}
                >
                  {LEAGUE_LABELS[player.team.league] || player.team.league}
                </span>
              </div>
            )}

            <div className="grid grid-cols-2 gap-4 text-white">
              <div>
                <p className="text-blue-100 text-sm">ポジション</p>
                <p className="text-lg font-semibold">{player.position || '-'}</p>
              </div>
              <div>
                <p className="text-blue-100 text-sm">背番号</p>
                <p className="text-lg font-semibold">{player.jersey_number ?? '-'}</p>
              </div>
              <div>
                <p className="text-blue-100 text-sm">投打</p>
                <p className="text-lg font-semibold">{throwBatDisplay}</p>
              </div>
              <div>
                <p className="text-blue-100 text-sm">ステータス</p>
                <p className="text-lg font-semibold">
                  {player.is_active ? (
                    <span className="text-green-300">現役</span>
                  ) : (
                    <span className="text-gray-400">引退/育成</span>
                  )}
                </p>
              </div>
            </div>
          </div>

          <div>
            <div className="bg-white/10 rounded-lg p-6 backdrop-blur">
              <h3 className="text-lg font-semibold text-white mb-4">基本情報</h3>
              <div className="space-y-3 text-white">
                {player.birth_date && (
                  <div>
                    <p className="text-blue-100 text-sm">生年月日</p>
                    <p className="text-lg">{player.birth_date}</p>
                  </div>
                )}
                <div>
                  <p className="text-blue-100 text-sm">NPB ID</p>
                  <p className="text-lg font-mono">{player.npb_id}</p>
                </div>
                {stats.length > 0 && (
                  <div>
                    <p className="text-blue-100 text-sm">記録シーズン数</p>
                    <p className="text-lg">{stats.length}シーズン</p>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Actions */}
      <div className="mb-8 flex gap-4">
        <button
          onClick={() => {
            router.push(`/compare?players=${playerId}`);
          }}
          className="px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded font-medium transition"
        >
          比較に追加
        </button>
      </div>

      {error && (
        <div className="mb-8 p-4 bg-red-900 border border-red-700 rounded text-red-100">
          エラー: {error}
        </div>
      )}

      {/* Stats Chart */}
      {chartData.length > 0 && statDefs.length > 0 && (
        <div className="mb-12">
          <StatsChart
            data={chartData}
            type="line"
            dataKey={statDefs[0].stat_key}
            title={`${statDefs[0].display_name_ja}の推移`}
            loading={loading}
          />
        </div>
      )}

      {/* Season Selector */}
      {stats.length > 0 && (
        <div className="mb-8 flex items-center gap-4">
          <label className="text-gray-300 font-medium">シーズン選択:</label>
          <select
            value={selectedSeason || ''}
            onChange={(e) => setSelectedSeason(parseInt(e.target.value))}
            className="px-4 py-2 bg-gray-800 border border-gray-700 rounded text-gray-200 hover:border-blue-500 transition"
          >
            {stats.map((s) => (
              <option key={s.season} value={s.season}>
                {s.season}年
              </option>
            ))}
          </select>
        </div>
      )}

      {/* Stats Table */}
      {selectedStats && (
        <div className="bg-gray-800 rounded-lg border border-gray-700 overflow-hidden">
          <div className="px-6 py-4 border-b border-gray-700">
            <h2 className="text-xl font-bold text-white">
              {selectedStats.season}年シーズン統計
            </h2>
          </div>

          <div className="p-6">
            {loading ? (
              <div className="text-center text-gray-400">読み込み中...</div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {statDefs.map((def) => {
                  const value = (selectedStats as any)[def.stat_key];
                  if (value === undefined || value === null) return null;

                  const displayValue =
                    typeof value === 'number'
                      ? value.toFixed(def.decimal_places)
                      : value;

                  return (
                    <div
                      key={def.stat_key}
                      className="bg-gray-700 rounded-lg p-4 border border-gray-600"
                    >
                      <p className="text-gray-400 text-sm mb-1">{def.display_name_ja}</p>
                      <p className="text-2xl font-bold text-blue-300">{displayValue}</p>
                      <p className="text-xs text-gray-500 mt-1">{def.description || def.stat_key}</p>
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        </div>
      )}

      {/* All Seasons Stats Table */}
      {stats.length > 0 && (
        <div className="mt-12 bg-gray-800 rounded-lg border border-gray-700 overflow-hidden">
          <div className="px-6 py-4 border-b border-gray-700">
            <h2 className="text-xl font-bold text-white">全シーズン統計</h2>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-gray-700 bg-gray-900">
                  <th className="px-6 py-3 text-left text-sm font-semibold text-gray-300">
                    シーズン
                  </th>
                  {statDefs.slice(0, 8).map((def) => (
                    <th
                      key={def.stat_key}
                      className="px-6 py-3 text-left text-sm font-semibold text-gray-300"
                    >
                      {def.display_name_ja}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {stats
                  .sort((a, b) => b.season - a.season)
                  .map((s, idx) => (
                    <tr
                      key={idx}
                      className={`border-b border-gray-800 hover:bg-gray-700 transition ${
                        s.season === selectedSeason ? 'bg-blue-900/20' : ''
                      }`}
                      onClick={() => setSelectedSeason(s.season)}
                    >
                      <td className="px-6 py-4 text-sm font-semibold text-blue-400 cursor-pointer">
                        {s.season}年
                      </td>
                      {statDefs.slice(0, 8).map((def) => {
                        const value = (s as any)[def.stat_key];
                        const displayValue =
                          typeof value === 'number'
                            ? value.toFixed(def.decimal_places)
                            : value || '-';
                        return (
                          <td key={def.stat_key} className="px-6 py-4 text-sm text-gray-300">
                            {displayValue}
                          </td>
                        );
                      })}
                    </tr>
                  ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
