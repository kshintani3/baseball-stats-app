'use client';

import { useEffect, useState } from 'react';
import { useSearchParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import SeasonSelector from '@/components/SeasonSelector';
import PlayerCard from '@/components/PlayerCard';
import StatsChart from '@/components/StatsChart';
import {
  fetchComparePlayersStats,
  fetchPlayer,
  fetchStatDefinitions,
  StatDefinition,
} from '@/lib/api';
import { Player, ComparisonResponse } from '@/types/index';

export default function ComparePage() {
  const router = useRouter();
  const searchParams = useSearchParams();

  const [season, setSeason] = useState<number>(parseInt(searchParams.get('season') || '2024'));
  const [selectedPlayers, setSelectedPlayers] = useState<Player[]>([]);
  const [playerSearch, setPlayerSearch] = useState('');
  const [comparisonData, setComparisonData] = useState<ComparisonResponse | null>(null);
  const [statDefs, setStatDefs] = useState<StatDefinition[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [playerType, setPlayerType] = useState<'batter' | 'pitcher'>('batter');

  // Initialize from URL params
  useEffect(() => {
    const playerIds = searchParams.get('players');
    if (playerIds) {
      const ids = playerIds.split(',').map((id) => parseInt(id));
      loadPlayersForIds(ids);
    }
  }, []);

  // Load stat definitions
  useEffect(() => {
    const loadDefs = async () => {
      try {
        const defs = await fetchStatDefinitions(playerType);
        setStatDefs(defs.stats);
      } catch (err) {
        // Fallback
      }
    };
    loadDefs();
  }, [playerType]);

  const loadPlayersForIds = async (ids: number[]) => {
    try {
      setLoading(true);
      setError(null);
      const players: Player[] = [];
      for (const id of ids) {
        const response = await fetchPlayer(id);
        players.push(response);
      }
      setSelectedPlayers(players);
      if (players.length > 0) {
        const type = players[0].position?.includes('投') ? 'pitcher' : 'batter';
        setPlayerType(type);
      }
    } catch (err) {
      setError('選手の読み込みに失敗しました');
    } finally {
      setLoading(false);
    }
  };

  const addPlayer = async () => {
    if (!playerSearch.trim() || selectedPlayers.length >= 4) return;

    try {
      setLoading(true);
      setError(null);

      // Parse player ID from search
      const playerId = parseInt(playerSearch);
      if (isNaN(playerId)) {
        setError('有効なプレイヤーIDを入力してください');
        return;
      }

      const response = await fetchPlayer(playerId);
      const player = response;

      // Check if already selected
      if (selectedPlayers.some((p) => p.id === player.id)) {
        setError('この選手は既に選択されています');
        return;
      }

      // Check player type consistency
      const newType = player.position?.includes('投') ? 'pitcher' : 'batter';
      if (selectedPlayers.length > 0 && newType !== playerType) {
        setError('異なるタイプの選手は比較できません');
        return;
      }

      setSelectedPlayers([...selectedPlayers, player]);
      setPlayerSearch('');
      if (selectedPlayers.length === 0) {
        setPlayerType(newType);
      }
    } catch (err) {
      setError('選手を見つけることができません');
    } finally {
      setLoading(false);
    }
  };

  const removePlayer = (id: number) => {
    setSelectedPlayers(selectedPlayers.filter((p) => p.id !== id));
  };

  const performComparison = async () => {
    if (selectedPlayers.length < 2) {
      setError('2人以上の選手を選択してください');
      return;
    }

    try {
      setLoading(true);
      setError(null);

      const ids = selectedPlayers.map((p) => p.id);
      const response = await fetchComparePlayersStats(ids, season, playerType);
      setComparisonData(response);

      // Update URL
      const params = new URLSearchParams({
        players: ids.join(','),
        season: season.toString(),
      });
      router.push(`/compare?${params.toString()}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : '比較データの取得に失敗しました');
    } finally {
      setLoading(false);
    }
  };

  const chartData = selectedPlayers.map((player) => {
    const playerStats = comparisonData?.rows.find((s) => s.id === player.id);
    if (!playerStats || statDefs.length === 0) return null;

    const mainStat = statDefs[0];
    return {
      playerName: player.name_ja,
      [mainStat.stat_key]: playerStats.stats[mainStat.stat_key] || 0,
    };
  });

  const validChartData = chartData.filter((d) => d !== null);

  return (
    <div className="p-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-4xl font-bold text-white mb-2">選手比較</h1>
        <p className="text-gray-400">複数の選手の統計を並べて比較</p>
      </div>

      {/* Season Selector */}
      <div className="mb-8 flex items-center gap-4">
        <label className="text-gray-300 font-medium">シーズン:</label>
        <SeasonSelector value={season} onChange={setSeason} />
      </div>

      {/* Player Selection */}
      <div className="mb-8 bg-gray-800 rounded-lg border border-gray-700 p-6">
        <h2 className="text-lg font-semibold text-white mb-4">選手を選択</h2>

        <div className="flex gap-4 mb-6">
          <input
            type="number"
            value={playerSearch}
            onChange={(e) => setPlayerSearch(e.target.value)}
            placeholder="選手IDを入力"
            disabled={selectedPlayers.length >= 4}
            className="flex-1 px-4 py-2 bg-gray-700 border border-gray-600 rounded text-gray-200 placeholder-gray-500 hover:border-blue-500 transition disabled:opacity-50"
            onKeyPress={(e) => {
              if (e.key === 'Enter') {
                addPlayer();
              }
            }}
          />
          <button
            onClick={addPlayer}
            disabled={selectedPlayers.length >= 4 || !playerSearch}
            className="px-6 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded font-medium transition disabled:opacity-50 disabled:cursor-not-allowed"
          >
            追加
          </button>
        </div>

        {error && (
          <div className="mb-6 p-3 bg-red-900 border border-red-700 rounded text-red-100 text-sm">
            {error}
          </div>
        )}

        {selectedPlayers.length > 0 && (
          <div className="mb-6">
            <p className="text-gray-300 text-sm mb-3">
              選択済み: {selectedPlayers.length}/4
            </p>
            <div className="flex flex-wrap gap-3">
              {selectedPlayers.map((player) => (
                <div
                  key={player.id}
                  className="bg-gray-700 rounded px-3 py-2 flex items-center gap-2"
                >
                  <span className="text-gray-100">{player.name_ja}</span>
                  <button
                    onClick={() => removePlayer(player.id)}
                    className="text-red-400 hover:text-red-300 transition"
                  >
                    ×
                  </button>
                </div>
              ))}
            </div>
          </div>
        )}

        {selectedPlayers.length >= 2 && (
          <button
            onClick={performComparison}
            disabled={loading}
            className="w-full px-6 py-3 bg-green-600 hover:bg-green-700 text-white rounded font-medium transition disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? '比較中...' : '比較を実行'}
          </button>
        )}
      </div>

      {/* Comparison Results */}
      {comparisonData && selectedPlayers.length > 0 && (
        <>
          {/* Player Cards */}
          <div className="mb-12">
            <h2 className="text-2xl font-bold text-white mb-6">選手情報</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              {selectedPlayers.map((player) => (
                <PlayerCard key={player.id} player={player} showRemove={false} />
              ))}
            </div>
          </div>

          {/* Comparison Chart */}
          {validChartData.length > 0 && statDefs.length > 0 && (
            <div className="mb-12">
              <StatsChart
                data={validChartData}
                type="bar"
                dataKey={statDefs[0].stat_key}
                xAxisKey="playerName"
                title={`${statDefs[0].display_name_ja}の比較`}
                loading={loading}
              />
            </div>
          )}

          {/* Comparison Table */}
          <div className="bg-gray-800 rounded-lg border border-gray-700 overflow-hidden">
            <div className="px-6 py-4 border-b border-gray-700">
              <h2 className="text-xl font-bold text-white">
                {season}年シーズン統計比較
              </h2>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full min-w-max">
                <thead>
                  <tr className="border-b border-gray-700 bg-gray-900">
                    <th className="px-6 py-3 text-left text-sm font-semibold text-gray-300 sticky left-0 bg-gray-900">
                      統計項目
                    </th>
                    {selectedPlayers.map((player) => (
                      <th
                        key={player.id}
                        className="px-6 py-3 text-left text-sm font-semibold text-blue-300"
                      >
                        {player.name_ja}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {statDefs.map((def) => (
                    <tr key={def.stat_key} className="border-b border-gray-800 hover:bg-gray-700 transition">
                      <td className="px-6 py-4 text-sm font-semibold text-gray-300 sticky left-0 bg-gray-800 hover:bg-gray-700">
                        {def.display_name_ja}
                      </td>
                      {selectedPlayers.map((player) => {
                        const playerStats = comparisonData?.rows.find(
                          (s) => s.id === player.id
                        );
                        const value = playerStats ? playerStats.stats[def.stat_key] : undefined;
                        const displayValue =
                          value !== undefined && typeof value === 'number'
                            ? value.toFixed(def.decimal_places)
                            : value || '-';
                        return (
                          <td
                            key={`${player.id}-${def.stat_key}`}
                            className="px-6 py-4 text-sm text-gray-200 font-medium"
                          >
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
        </>
      )}

      {!comparisonData && selectedPlayers.length > 0 && (
        <div className="text-center py-12 text-gray-400">
          上記の「比較を実行」ボタンをクリックして結果を表示してください
        </div>
      )}
    </div>
  );
}
