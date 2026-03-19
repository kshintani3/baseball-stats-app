'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import SeasonSelector from '@/components/SeasonSelector';
import RankingTable from '@/components/RankingTable';
import {
  fetchBatterRankings,
  fetchPitcherRankings,
  fetchSeasons,
  fetchStatDefinitions,
  StatDefinition,
} from '@/lib/api';
import { RankingRow } from '@/types/index';

export default function Dashboard() {
  const [season, setSeason] = useState<number>(2024);
  const [batterStats, setBatterStats] = useState<RankingRow[]>([]);
  const [pitcherStats, setPitcherStats] = useState<RankingRow[]>([]);
  const [batterStatDef, setBatterStatDef] = useState<StatDefinition | null>(null);
  const [pitcherStatDef, setPitcherStatDef] = useState<StatDefinition | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const defaultMinPA = 300;
  const defaultMinIP = 100;

  useEffect(() => {
    const loadDashboard = async () => {
      try {
        setLoading(true);
        setError(null);

        // Load stat definitions
        const batterDefs = await fetchStatDefinitions('batter');
        const pitcherDefs = await fetchStatDefinitions('pitcher');

        // Load top 5 batters (OPS if available, otherwise first stat)
        const batterStat = batterDefs.stats.find((s) => s.stat_key === 'ops') || batterDefs.stats[0];
        if (batterStat) {
          const batterResp = await fetchBatterRankings(batterStat.stat_key, season, {
            limit: 5,
            min_pa: defaultMinPA,
          });
          setBatterStats(batterResp.rows);
          setBatterStatDef(batterStat);
        }

        // Load top 5 pitchers (ERA if available, otherwise first stat)
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
          href="/teams"
          className="bg-gradient-to-br from-purple-600 to-purple-700 rounded-lg p-6 hover:shadow-lg hover:from-purple-500 hover:to-purple-600 transition transform hover:scale-105"
        >
          <div className="text-3xl mb-2">🏟️</div>
          <h3 className="text-lg font-bold text-white mb-1">チーム</h3>
          <p className="text-purple-100 text-sm">チーム順位</p>
        </Link>

        <Link
          href="/compare"
          className="bg-gradient-to-br from-orange-600 to-orange-700 rounded-lg p-6 hover:shadow-lg hover:from-orange-500 hover:to-orange-600 transition transform hover:scale-105"
        >
          <div className="text-3xl mb-2">⚖️</div>
          <h3 className="text-lg font-bold text-white mb-1">選手比較</h3>
          <p className="text-orange-100 text-sm">複数選手の比較</p>
        </Link>
      </div>

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
