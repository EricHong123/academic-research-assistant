'use client';

import { useState } from 'react';
import Link from 'next/link';
import { useI18n } from '@/lib/i18n';
import { Search, FolderOpen, MessageSquare, BookMarked } from 'lucide-react';

export function Header() {
  const { t, locale, setLocale } = useI18n();

  const navItems = [
    { href: `/${locale}`, icon: Search, label: t('nav.search') },
    { href: `/${locale}/projects`, icon: FolderOpen, label: t('nav.projects') },
    { href: `/${locale}/chat`, icon: MessageSquare, label: t('nav.chat') },
  ];

  return (
    <header className="bg-white shadow-sm border-b border-gray-200">
      <div className="max-w-6xl mx-auto px-6">
        <div className="flex items-center justify-between h-14">
          {/* Logo */}
          <Link href={`/${locale}`} className="flex items-center gap-2">
            <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
              <BookMarked className="w-4 h-4 text-white" />
            </div>
            <span className="text-lg font-bold text-gray-800">ARA</span>
          </Link>

          {/* Navigation */}
          <nav className="flex items-center gap-1">
            {navItems.map((item) => (
              <Link
                key={item.href}
                href={item.href}
                className="flex items-center gap-2 px-3 py-2 text-sm text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition"
              >
                <item.icon className="w-4 h-4" />
                {item.label}
              </Link>
            ))}
          </nav>

          {/* Language */}
          <button
            onClick={() => {
              const newLocale = locale === 'en' ? 'zh' : 'en';
              setLocale(newLocale);
              window.location.href = `/${newLocale}`;
            }}
            className="px-3 py-1 text-sm text-gray-600 hover:bg-gray-100 rounded transition"
          >
            {locale === 'en' ? '中文' : 'EN'}
          </button>
        </div>
      </div>
    </header>
  );
}
