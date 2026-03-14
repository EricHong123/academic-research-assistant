'use client';

import { useI18n } from '@/lib/i18n';

export function Header() {
  const { t, locale, setLocale } = useI18n();

  const toggleLang = () => {
    setLocale(locale === 'en' ? 'zh' : 'en');
    // Reload to apply new locale
    window.location.href = `/${locale === 'en' ? 'zh' : 'en'}`;
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
