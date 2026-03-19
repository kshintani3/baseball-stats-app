'use client';

import { Player } from '@/types/index';
import Link from 'next/link';

interface PlayerCardProps {
  player: Player;
  stats?: Record<string, any>;
  onRemove?: () => void;
  showRemove?: boolean;
}

export default function PlayerCard({
  player,
  stats,
  onRemove,
  showRemove = false,
}: PlayerCardProps) {
  return (
    <div className="bg-gray-800 rounded-lg border border-gray-700 overflow-hidden hover:border-blue-500 transition">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-600 to-blue-500 px-6 py-4">
        <div className="flex items-start justify-between">
          <div>
            <h3 className="text-xl font-bold text-white">{player.name_ja}</h3>
            <p className="text-blue-100 text-sm">{player.name_en}</p>
          </div>
          {showRemove && (
            <button
              onClick={onRemove}
              className="bg-red-600 hover:bg-red-700 text-white px-3 py-1 rounded text-sm transition"
            >
              削除
            </button>
          )}
        </div>
      </div>

      {/* Body */}
      <div className="px-6 py-4">
        <div className="grid grid-cols-2 gap-4 mb-4">
          <div>
            <p className="text-gray-400 text-sm">ポジション</p>
            <p className="text-gray-100 font-medium">{player.position || '-'}</p>
          </div>
          <div>
            <p className="text-gray-400 text-sm">背番号</p>
            <p className="text-gray-100 font-medium">{player.jersey_number || '-'}</p>
          </div>
          <div>
            <p className="text-gray-400 text-sm">投打</p>
            <p className="text-gray-100 font-medium">{player.bats || '-'}</p>
          </div>
          <div>
            <p className="text-gray-400 text-sm">利き足</p>
            <p className="text-gray-100 font-medium">{player.throws || '-'}</p>
          </div>
        </div>

        {player.birth_date && (
          <div className="mb-4">
            <p className="text-gray-400 text-sm">生年月日</p>
            <p className="text-gray-100">
              {player.birth_date}
            </p>
          </div>
        )}

        {stats && Object.keys(stats).length > 0 && (
          <div className="border-t border-gray-700 pt-4">
            <p className="text-gray-400 text-sm mb-2">シーズン統計</p>
            <div className="space-y-1 text-sm">
              {Object.entries(stats).slice(0, 4).map(([key, value]) => (
                <div key={key} className="flex justify-between">
                  <span className="text-gray-400">{key}:</span>
                  <span className="text-gray-100 font-medium">{value}</span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Footer */}
      <div className="px-6 py-3 bg-gray-900 border-t border-gray-700">
        <Link
          href={`/players/${player.id}`}
          className="text-blue-400 hover:text-blue-300 text-sm font-medium transition"
        >
          詳細を見る →
        </Link>
      </div>
    </div>
  );
}
