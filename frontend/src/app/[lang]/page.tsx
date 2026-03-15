'use client';

import { I18nProvider } from '@/lib/i18n';
import { Header } from '@/components/header';
import SearchPage from './search-page';

export default function Home({
  params: { lang },
}: {
  params: { lang: string };
}) {
  return (
    <I18nProvider locale={lang}>
      <div className="min-h-screen flex flex-col">
        <Header />
        <main className="flex-1">
          <SearchPage />
        </main>
      </div>
    </I18nProvider>
  );
}
