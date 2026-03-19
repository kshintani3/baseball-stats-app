'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';

const navigationItems = [
  { href: '/', label: 'ダッシュボード', icon: '📊' },
  { href: '/batters', label: '打者ランキング', icon: '⚾' },
  { href: '/pitchers', label: '投手ランキング', icon: '🎯' },
  { href: '/teams', label: 'チーム', icon: '🏟️' },
  { href: '/compare', label: '選手比較', icon: '⚖️' },
];

export default function Navbar() {
  const pathname = usePathname();

  return (
    <nav className="fixed left-0 top-0 h-screen w-64 bg-gray-900 border-r border-gray-800 flex flex-col">
      {/* Logo */}
      <Link href="/" className="flex items-center gap-3 px-6 py-6 border-b border-gray-800 hover:bg-gray-800 transition">
        <span className="text-3xl">⚾</span>
        <div className="flex flex-col">
          <span className="text-xl font-bold text-blue-400">NPB Stats</span>
          <span className="text-xs text-gray-400">日本野球</span>
        </div>
      </Link>

      {/* Navigation Items */}
      <div className="flex-1 overflow-y-auto py-4">
        {navigationItems.map((item) => {
          const isActive = pathname === item.href || (pathname.startsWith(item.href) && item.href !== '/');
          return (
            <Link
              key={item.href}
              href={item.href}
              className={`flex items-center gap-3 px-6 py-4 transition border-l-4 ${
                isActive
                  ? 'bg-gray-800 border-l-blue-500 text-blue-400'
                  : 'border-l-transparent text-gray-300 hover:bg-gray-800'
              }`}
            >
              <span className="text-xl">{item.icon}</span>
              <span className="font-medium">{item.label}</span>
            </Link>
          );
        })}
      </div>

      {/* Footer */}
      <div className="px-6 py-4 border-t border-gray-800 text-xs text-gray-500">
        <p>NPB Stats v1.0</p>
      </div>
    </nav>
  );
}
