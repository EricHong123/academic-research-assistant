import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import './globals.css';

const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = {
  title: 'Academic Research Assistant',
  description: 'AI-powered academic literature search and analysis',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <div className="min-h-screen bg-gray-50">
          <header className="bg-white shadow-sm border-b">
            <div className="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
              <h1 className="text-xl font-semibold text-gray-900">
                Academic Research Assistant
              </h1>
              <nav className="flex gap-4">
                <a href="/" className="text-gray-600 hover:text-gray-900">Search</a>
                <a href="/projects" className="text-gray-600 hover:text-gray-900">Projects</a>
                <a href="/chat" className="text-gray-600 hover:text-gray-900">Chat</a>
              </nav>
            </div>
          </header>
          <main>{children}</main>
        </div>
      </body>
    </html>
  );
}
