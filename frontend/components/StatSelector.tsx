'use client';

import { useEffect, useState } from 'react';
import { fetchStatDefinitions, StatDefinition } from '@/lib/api';

interface StatSelectorProps {
  category: 'batter' | 'pitcher' | 'team';
  value: string;
  onChange: (stat: string) => void;
  onStatDefChange?: (def: StatDefinition | null) => void;
  loading?: boolean;
}

export default function StatSelector({
  category,
  value,
  onChange,
  onStatDefChange,
  loading,
}: StatSelectorProps) {
  const [stats, setStats] = useState<StatDefinition[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const loadStats = async () => {
      try {
        setIsLoading(true);
        const response = await fetchStatDefinitions(category);
        setStats(response.stats);
        setError(null);
      } catch (err) {
        setError('統計データ読み込みエラー');
        setStats([]);
      } finally {
        setIsLoading(false);
      }
    };

    loadStats();
  }, [category]);

  const handleChange = (statKey: string) => {
    onChange(statKey);
    const selected = stats.find((s) => s.stat_key === statKey);
    onStatDefChange?.(selected || null);
  };

  if (isLoading || loading) {
    return (
      <select
        disabled
        className="px-4 py-2 bg-gray-800 border border-gray-700 rounded text-gray-300 cursor-not-allowed"
      >
        <option>読み込み中...</option>
      </select>
    );
  }

  if (error) {
    return (
      <select disabled className="px-4 py-2 bg-gray-800 border border-red-700 rounded text-red-400">
        <option>エラー</option>
      </select>
    );
  }

  return (
    <select
      value={value}
      onChange={(e) => handleChange(e.target.value)}
      className="px-4 py-2 bg-gray-800 border border-gray-700 rounded text-gray-200 hover:border-blue-500 transition cursor-pointer"
    >
      {stats.map((stat) => (
        <option key={stat.stat_key} value={stat.stat_key}>
          {stat.display_name_ja}
        </option>
      ))}
    </select>
  );
}
