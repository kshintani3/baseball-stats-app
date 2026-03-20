'use client';

import { LEAGUE_LABELS } from '@/types/index';

interface LeagueFilterProps {
  value: string;
  onChange: (league: string) => void;
  loading?: boolean;
}

export default function LeagueFilter({
  value,
  onChange,
  loading,
}: LeagueFilterProps) {
  if (loading) {
    return (
      <select
        disabled
        className="px-4 py-2 bg-gray-800 border border-gray-700 rounded text-gray-300 cursor-not-allowed"
      >
        <option>読み込み中...</option>
      </select>
    );
  }

  return (
    <select
      value={value}
      onChange={(e) => onChange(e.target.value)}
      className="px-4 py-2 bg-gray-800 border border-gray-700 rounded text-gray-200 hover:border-blue-500 transition cursor-pointer"
    >
      <option value="">両リーグ</option>
      <option value="central">{LEAGUE_LABELS.central}</option>
      <option value="pacific">{LEAGUE_LABELS.pacific}</option>
    </select>
  );
}
