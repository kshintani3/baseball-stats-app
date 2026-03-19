'use client';

import { useEffect, useState } from 'react';
import { fetchSeasons } from '@/lib/api';

interface SeasonSelectorProps {
  value: number;
  onChange: (season: number) => void;
  loading?: boolean;
}

export default function SeasonSelector({
  value,
  onChange,
  loading,
}: SeasonSelectorProps) {
  const [seasons, setSeasons] = useState<number[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const loadSeasons = async () => {
      try {
        setIsLoading(true);
        const response = await fetchSeasons();
        setSeasons(response.seasons.sort((a, b) => b - a));
        setError(null);
      } catch (err) {
        setError('シーズン読み込みエラー');
        setSeasons([]);
      } finally {
        setIsLoading(false);
      }
    };

    loadSeasons();
  }, []);

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
      onChange={(e) => onChange(parseInt(e.target.value))}
      className="px-4 py-2 bg-gray-800 border border-gray-700 rounded text-gray-200 hover:border-blue-500 transition cursor-pointer"
    >
      {seasons.map((season) => (
        <option key={season} value={season}>
          {season}年
        </option>
      ))}
    </select>
  );
}
