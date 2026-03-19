import type { Metadata } from 'next';
import './globals.css';
import Navbar from '@/components/Navbar';

export const metadata: Metadata = {
  title: 'NPB Stats - 日本野球統計',
  description: '日本プロ野球の統計情報を提供します',
  viewport: 'width=device-width, initial-scale=1',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="ja">
      <body className="bg-gray-900 text-gray-100">
        <Navbar />
        <main className="ml-64 min-h-screen">
          {children}
        </main>
      </body>
    </html>
  );
}
