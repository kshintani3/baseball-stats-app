'use client';

import Link from 'next/link';
import { RankingRow, StatDefinition, LEAGUE_LABELS } from '@/types/index';

interface RankingTableProps {
  data: RankingRow[];
  statDef?: StatDefinition;
  loading?: boolean;
  error?: string;
  onRowClick?: (item: RankingRow) => void;
}

function LeagueBadge({ league }: { league?: string }) {
  if (!league) return null;
  const iscentral = league === 'central';
  return (
    <span
      className={`inline-block px-1.5 py-0.5 rounded text-xs font-medium ${
        iscentral
          ? 'bg-orange-900/40 text-orange-400 border border-orange-800'
          : 'bg-blue-900/40 text-blue-400 border border-blue-800'
      }`}
    >
      {iscentral ? 'セ' : 'パ'}
    </span>
  );
}

export default function RankingTable({
  data,
  statDef,
  loading,
  error,
  onRowClick,
}: RankingTableProps) {
  if (loading) {
    return (
      <div className="flex justify-center items-center py-12">
        <div className="text-gray-400">読み込み中...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex justify-center items-center py-12">
        <div className="text-red-400">エラー: {error}</div>
      </div>
    );
  }

  if (data.length === 0) {
    return (
      <div className="flex justify-center items-center py-12">
        <div className="text-gray-400">データがありません</div>
      </div>
    );
  }

  const formatValue = (value: any) => {
    if (statDef && typeof value === 'number') {
      return value.toFixed(statDef.decimal_places);
    }
    return value;
  };

  const isTeamRanking = data.length > 0 && data[0].team_id !== undefined && data[0].player_id === undefined;

  return (
    <div className="overflow-x-auto">
      <table className="w-full">
        <thead>
          <tr className="border-b border-gray-700 bg-gray-800">
            <th className="px-6 py-3 text-left text-sm font-semibold text-gray-300 whitespace-nowrap">
              順位
            </th>
            <th className="px-6 py-3 text-left text-sm font-semibold text-gray-300 whitespace-nowrap">
              {isTeamRanking ? 'チーム' : '選手名'}
            </th>
            {!isTeamRanking && (
              <th className="px-6 py-3 text-left text-sm font-semibold text-gray-300 whitespace-nowrap">
                チーム
              </th>
            )}
            {!isTeamRanking && (
              <th className="px-6 py-3 text-left text-sm font-semibold text-gray-300 whitespace-nowrap">
                ポジション
              </th>
            )}
            {isTeamRanking && (
              <th className="px-6 py-3 text-left text-sm font-semibold text-gray-300 whitespace-nowrap">
                リーグ
              </th>
            )}
            <th className="px-6 py-3 text-left text-sm font-semibold text-gray-300 whitespace-nowrap">
              {statDef?.display_name_ja || '成績'}
            </th>
          </tr>
        </thead>
        <tbody>
          {data.map((item, index) => (
            <tr
              key={index}
              className="border-b border-gray-800 hover:bg-gray-700 transition cursor-pointer"
              onClick={() => onRowClick?.(item)}
            >
              <td className="px-6 py-4 text-sm font-bold text-blue-400 whitespace-nowrap">
                {item.rank}
              </td>
              <td className="px-6 py-4 text-sm text-gray-300 whitespace-nowrap">
                {isTeamRanking ? (
                  <span className="font-medium">{item.name_ja}</span>
                ) : (
                  <Link
                    href={`/players/${item.player_id}`}
                    className="text-blue-400 hover:text-blue-300 font-medium transition"
                    onClick={(e) => e.stopPropagation()}
                  >
                    {item.name_ja}
                  </Link>
                )}
              </td>
              {!isTeamRanking && (
                <td className="px-6 py-4 text-sm text-gray-300 whitespace-nowrap">
                  <div className="flex items-center gap-2">
                    <LeagueBadge league={item.team_league} />
                    <span>{item.team_short_name || item.team_code || '-'}</span>
                  </div>
                </td>
              )}
              {!isTeamRanking && (
                <td className="px-6 py-4 text-sm text-gray-300 whitespace-nowrap">
                  {item.position || '-'}
                </td>
              )}
              {isTeamRanking && (
                <td className="px-6 py-4 text-sm text-gray-300 whitespace-nowrap">
                  <LeagueBadge league={item.team_league} />
                </td>
              )}
              <td className="px-6 py-4 text-sm font-semibold text-blue-300 whitespace-nowrap">
                {formatValue(item.stat_value)}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
