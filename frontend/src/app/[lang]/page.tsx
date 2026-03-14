import { I18nProvider } from '@/lib/i18n';
import SearchPage from './search-page';

export default function Home({
  params: { lang },
}: {
  params: { lang: string };
}) {
  return (
    <I18nProvider locale={lang}>
      <SearchPage />
    </I18nProvider>
  );
}
