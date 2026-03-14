import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import { I18nProvider } from '@/lib/i18n';
import { Header } from '@/components/header';
import '../globals.css';

const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = {
  title: '学术文献智能搜索 | Academic Research Assistant',
  description: '基于 LangGraph 的学术文献智能搜索与分析系统',
};

export default function RootLayout({
  children,
  params,
}: {
  children: React.ReactNode;
  params: { lang: string };
}) {
  return (
    <html lang={params.lang}>
      <body className={inter.className}>
        <I18nProvider locale={params.lang}>
          <div className="min-h-screen bg-gray-50">
            <Header />
            <main>{children}</main>
          </div>
        </I18nProvider>
      </body>
    </html>
  );
}
