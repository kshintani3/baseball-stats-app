'use client';

import {
  LineChart,
  Line,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';

interface StatsChartProps {
  data: any[];
  type: 'line' | 'bar';
  dataKey: string;
  xAxisKey?: string;
  title?: string;
  colors?: string[];
  loading?: boolean;
}

export default function StatsChart({
  data,
  type,
  dataKey,
  xAxisKey = 'season',
  title,
  colors = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444'],
  loading,
}: StatsChartProps) {
  if (loading) {
    return (
      <div className="w-full h-96 flex items-center justify-center bg-gray-800 rounded">
        <div className="text-gray-400">読み込み中...</div>
      </div>
    );
  }

  if (!data || data.length === 0) {
    return (
      <div className="w-full h-96 flex items-center justify-center bg-gray-800 rounded">
        <div className="text-gray-400">グラフデータがありません</div>
      </div>
    );
  }

  const chartProps = {
    data,
    margin: { top: 5, right: 30, left: 0, bottom: 5 },
  };

  return (
    <div className="w-full bg-gray-800 rounded-lg p-6">
      {title && <h3 className="text-lg font-semibold text-gray-100 mb-4">{title}</h3>}
      <ResponsiveContainer width="100%" height={400}>
        {type === 'line' ? (
          <LineChart {...chartProps}>
            <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
            <XAxis dataKey={xAxisKey} stroke="#9ca3af" />
            <YAxis stroke="#9ca3af" />
            <Tooltip
              contentStyle={{
                backgroundColor: '#1f2937',
                border: '1px solid #374151',
                borderRadius: '0.5rem',
              }}
              labelStyle={{ color: '#f3f4f6' }}
            />
            <Legend />
            {Array.isArray(dataKey) ? (
              dataKey.map((key, idx) => (
                <Line
                  key={key}
                  type="monotone"
                  dataKey={key}
                  stroke={colors[idx % colors.length]}
                  strokeWidth={2}
                  dot={{ fill: colors[idx % colors.length] }}
                />
              ))
            ) : (
              <Line
                type="monotone"
                dataKey={dataKey}
                stroke={colors[0]}
                strokeWidth={2}
                dot={{ fill: colors[0] }}
              />
            )}
          </LineChart>
        ) : (
          <BarChart {...chartProps}>
            <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
            <XAxis dataKey={xAxisKey} stroke="#9ca3af" />
            <YAxis stroke="#9ca3af" />
            <Tooltip
              contentStyle={{
                backgroundColor: '#1f2937',
                border: '1px solid #374151',
                borderRadius: '0.5rem',
              }}
              labelStyle={{ color: '#f3f4f6' }}
            />
            <Legend />
            {Array.isArray(dataKey) ? (
              dataKey.map((key, idx) => (
                <Bar
                  key={key}
                  dataKey={key}
                  fill={colors[idx % colors.length]}
                  radius={[8, 8, 0, 0]}
                />
              ))
            ) : (
              <Bar dataKey={dataKey} fill={colors[0]} radius={[8, 8, 0, 0]} />
            )}
          </BarChart>
        )}
      </ResponsiveContainer>
    </div>
  );
}
