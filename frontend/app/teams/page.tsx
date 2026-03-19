'use client';

import { useEffect, useState } from 'react';
import { useSearchParams, useRouter } from 'next/navigation';
import SeasonSelector from '@/components/SeasonSelector';
import StatSelector from '@/components/StatSelector';
import RankingTable from '@/components/RankingTable';
import { fetchTeamRankings, fetchStatDefinitions, StatDefinition } from '@/lib/api';
import { RankingRow } from '@/types/index';

type ViewMode = 'ranking';

export default function TeamsPage() {
  const router = useRouter();
  const searchParams = useSearchParams();

  const [season, setSeason] = useState<number>(parseInt(searchParams.get('season') || '2024'));
  const [statKey, setStatKey] = useState(searchParams.get('stat_key') || '');

  const [rankings, setRankings] = useState<RankingRow[]>([]);
  const [statDef, setStatDef] = useState<StatDefinition | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Initialize default stat
  useEffect(() => {
    const initStat = async () => {
      if (!statKey) {
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
  }, [statKey]);

  // Update URL params
  useEffect(() => {
    const params = new URLSearchParams({
      season: season.toString(),
    });
    if (statKey) {
      params.append('stat_key', statKey);
    }
    router.push(`/teams?${params.toString()}`);
  }, [season, statKey, router]);

  // Load team rankings
  useEffect(() => {
    if (!statKey) return;

    const loadRankings = async () => {
      try {
        setLoading(true);
        setError(null);

        const response = await fetchTeamRankings(statKey, season);

        setRankings(response.rows);

        // Get stat definition
        const defs = await fetchStatDefinitions('team');
        const def = defs.stats.find((s) => s.stat_key === statKey);
        setStatDef(def || null);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'エラーが発生しました');
        setRankings([]);
      } finally {
        setLoading(false);
      }
    };

    loadRankings();
  }, [statKey, season]);

  return (
    <div className="p-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-4xl font-bold text-white mb-2">チーム</h1>
        <p className="text-gray-400">チーム統計情報</p>
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
              統計項目
            </label>
            <StatSelector category="team" value={statKey} onChange={setStatKey} />
          </div>
        </div>
      </div>

      {error && (
        <div className="mb-8 p-4 bg-red-900 border border-red-700 rounded text-red-100">
          エラー: {error}
        </div>
      )}

      {/* Ranking View */}
      <div className="bg-gray-800 rounded-lg border border-gray-700 overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-700">
          <h2 className="text-lg font-semibold text-white">
            チームランキング {statDef ? `(${statDef.display_name_ja})` : ''}
          </h2>
        </div>

        {loading ? (
          <div className="flex justify-center items-center py-12">
            <div className="text-gray-400">読み込み中...</div>
          </div>
        ) : rankings.length === 0 ? (
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
    </div>
  );
}
