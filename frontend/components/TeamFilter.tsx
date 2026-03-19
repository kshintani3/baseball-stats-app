'use client';

import { useEffect, useState } from 'react';
import { fetchTeams } from '@/lib/api';
import { Team } from '@/types/index';

interface TeamFilterProps {
  value: string;
  onChange: (teamCode: string) => void;
  loading?: boolean;
}

export default function TeamFilter({
  value,
  onChange,
  loading,
}: TeamFilterProps) {
  const [teams, setTeams] = useState<Team[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const loadTeams = async () => {
      try {
        setIsLoading(true);
        const response = await fetchTeams();
        setTeams(response.teams);
        setError(null);
      } catch (err) {
        setError('チーム読み込みエラー');
        setTeams([]);
      } finally {
        setIsLoading(false);
      }
    };

    loadTeams();
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
      onChange={(e) => onChange(e.target.value)}
      className="px-4 py-2 bg-gray-800 border border-gray-700 rounded text-gray-200 hover:border-blue-500 transition cursor-pointer"
    >
      <option value="">全チーム</option>
      {teams.map((team) => (
        <option key={team.code} value={team.code}>
          {team.short_name}
        </option>
      ))}
    </select>
  );
}
