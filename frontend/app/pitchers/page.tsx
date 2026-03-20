'use client';

import { Suspense, useEffect, useState } from 'react';
import { useSearchParams, useRouter } from 'next/navigation';
import SeasonSelector from '@/components/SeasonSelector';
import StatSelector from '@/components/StatSelector';
import TeamFilter from '@/components/TeamFilter';
import LeagueFilter from '@/components/LeagueFilter';
import RankingTable from '@/components/RankingTable';
import { fetchPitcherRankings, fetchStatDefinitions, StatDefinition } from '@/lib/api';
import { RankingRow } from '@/types/index';

export default function PitchersPageWrapper() {
  return (
    <Suspense fallback={<div className="p-8 text-gray-400">読み込み中...</div>}>
      <PitchersPage />
    </Suspense>
  );
}

function PitchersPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const defaultMinIP = '100';

  const [season, setSeason] = useState<number>(parseInt(searchParams.get('season') || '2024'));
  const [statKey, setStatKey] = useState(searchParams.get('stat_key') || '');
  const [teamCode, setTeamCode] = useState(searchParams.get('team_code') || '');
  const [league, setLeague] = useState(searchParams.get('league') || '');
  const [role, setRole] = useState(searchParams.get('role') || '');
  const [minIP, setMinIP] = useState(searchParams.get('min_ip') || defaultMinIP);
  const [limit, setLimit] = useState(parseInt(searchParams.get('limit') || '20'));
  const [offset, setOffset] = useState(parseInt(searchParams.get('offset') || '0'));

  const [data, setData] = useState<RankingRow[]>([]);
  const [total, setTotal] = useState(0);
  const [statDef, setStatDef] = useState<StatDefinition | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Initialize default stat
  useEffect(() => {
    const initStat = async () => {
      if (!statKey) {
        try {
          const response = await fetchStatDefinitions('pitcher');
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

  // Clear team filter when league changes
  useEffect(() => {
    setTeamCode('');
    setOffset(0);
  }, [league]);

  // Update URL params
  useEffect(() => {
    const params = new URLSearchParams({
      season: season.toString(),
      stat_key: statKey,
      limit: limit.toString(),
      offset: offset.toString(),
    });
    if (teamCode) params.append('team_code', teamCode);
    if (league) params.append('league', league);
    if (role) params.append('role', role);
    if (minIP && minIP !== defaultMinIP) params.append('min_ip', minIP);
    router.push(`/pitchers?${params.toString()}`);
  }, [season, statKey, teamCode, league, role, minIP, limit, offset, router]);

  // Load data
  useEffect(() => {
    if (!statKey) return;

    const loadData = async () => {
      try {
        setLoading(true);
        setError(null);

        const response = await fetchPitcherRankings(statKey, season, {
          team_code: teamCode || undefined,
          league: league || undefined,
          role: role || undefined,
          min_ip: minIP ? parseFloat(minIP) : undefined,
          limit,
        });

        setData(response.rows);
        setTotal(response.total_count);

        // Get stat definition
        const defs = await fetchStatDefinitions('pitcher');
        const def = defs.stats.find((s) => s.stat_key === statKey);
        setStatDef(def || null);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'エラーが発生しました');
        setData([]);
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, [statKey, season, teamCode, league, role, minIP, limit]);

  const pageCount = Math.ceil(total / limit);

  return (
    <div className="p-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-4xl font-bold text-white mb-2">投手ランキング</h1>
        <p className="text-gray-400">日本プロ野球の投手の成績をランク付け</p>
      </div>

      {/* Filters */}
      <div className="mb-8 bg-gray-800 rounded-lg border border-gray-700 p-6">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-4">
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
            <StatSelector category="pitcher" value={statKey} onChange={setStatKey} />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              リーグ
            </label>
            <LeagueFilter value={league} onChange={setLeague} />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              チーム
            </label>
            <TeamFilter value={teamCode} onChange={setTeamCode} league={league || undefined} />
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              投手タイプ
            </label>
            <select
              value={role}
              onChange={(e) => {
                setRole(e.target.value);
                setOffset(0);
              }}
              className="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded text-gray-200 hover:border-blue-500 transition"
            >
              <option value="">すべて</option>
              <option value="starter">先発</option>
              <option value="reliever">リリーフ</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              最小投球回
            </label>
            <input
              type="number"
              value={minIP}
              onChange={(e) => {
                setMinIP(e.target.value);
                setOffset(0);
              }}
              min="0"
              step="0.1"
              className="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded text-gray-200 hover:border-blue-500 transition"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              表示件数
            </label>
            <select
              value={limit}
              onChange={(e) => {
                setLimit(parseInt(e.target.value));
                setOffset(0);
              }}
              className="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded text-gray-200 hover:border-blue-500 transition"
            >
              <option value="20">20件</option>
              <option value="50">50件</option>
              <option value="100">100件</option>
            </select>
          </div>
        </div>
      </div>

      {error && (
        <div className="mb-8 p-4 bg-red-900 border border-red-700 rounded text-red-100">
          エラー: {error}
        </div>
      )}

      {/* Table */}
      <div className="mb-8 bg-gray-800 rounded-lg border border-gray-700 overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-700">
          <h2 className="text-lg font-semibold text-white">
            結果: {total}件
          </h2>
        </div>
        <div className="p-6">
          <RankingTable
            data={data}
            statDef={statDef || undefined}
            loading={loading}
          />
        </div>
      </div>

      {/* Pagination */}
      {pageCount > 1 && (
        <div className="flex justify-center items-center gap-2 mb-8">
          <button
            onClick={() => setOffset(Math.max(0, offset - limit))}
            disabled={offset === 0}
            className="px-4 py-2 bg-gray-800 border border-gray-700 rounded text-gray-300 hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed transition"
          >
            前へ
          </button>

          <div className="text-gray-400">
            ページ {Math.floor(offset / limit) + 1} / {pageCount}
          </div>

          <button
            onClick={() => setOffset(offset + limit)}
            disabled={offset + limit >= total}
            className="px-4 py-2 bg-gray-800 border border-gray-700 rounded text-gray-300 hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed transition"
          >
            次へ
          </button>
        </div>
      )}
    </div>
  );
}
