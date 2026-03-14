import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import { I18nProvider, useI18n } from '@/lib/i18n';
import '../globals.css';

const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = {
  title: '学术文献智能搜索 | Academic Research Assistant',
  description: '基于 LangGraph 的学术文献智能搜索与分析系统',
};

function Header() {
  const { t, locale, setLocale } = useI18n();

  const toggleLang = () => {
    setLocale(locale === 'en' ? 'zh' : 'en');
  };

  return (
    <header className="bg-white shadow-sm border-b">
      <div className="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
        <h1 className="text-xl font-semibold text-gray-900">
          {t('search.title')}
        </h1>
        <nav className="flex gap-4 items-center">
          <a href={`/${locale}`} className="text-gray-600 hover:text-gray-900">
            {t('nav.search')}
          </a>
          <a href={`/${locale}/projects`} className="text-gray-600 hover:text-gray-900">
            {t('nav.projects')}
          </a>
          <a href={`/${locale}/chat`} className="text-gray-600 hover:text-gray-900">
            {t('nav.chat')}
          </a>
          <button
            onClick={toggleLang}
            className="ml-4 px-3 py-1 text-sm bg-gray-100 hover:bg-gray-200 rounded"
          >
            {locale === 'en' ? '中文' : 'EN'}
          </button>
        </nav>
      </div>
    </header>
  );
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
  params: { lang: string };
}) {
  return (
    <html lang={children ? 'zh' : 'zh'}>
      <body className={inter.className}>
        <I18nProvider locale="zh">
          <div className="min-h-screen bg-gray-50">
            <Header />
            <main>{children}</main>
          </div>
        </I18nProvider>
      </body>
    </html>
  );
}
