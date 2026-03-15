'use client';

import { useState, useEffect } from 'react';
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
      <div className="min-h-screen bg-[#0a0a0f]">
        <Header />
        <SearchPage />
      </div>
    </I18nProvider>
  );
}
