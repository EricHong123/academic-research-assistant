'use client';

import { useState } from 'react';
import { Search, Filter, Loader2, BookOpen, ExternalLink, Star, FileText } from 'lucide-react';
import { useI18n } from '@/lib/i18n';

interface Paper {
  id: string;
  title: string;
  authors: string[];
  year: number;
  journal: string;
  doi?: string;
  abstract?: string;
}

export default function SearchPage() {
  const { t, locale } = useI18n();
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<Paper[]>([]);
  const [loading, setLoading] = useState(false);
  const [searched, setSearched] = useState(false);

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;

    setLoading(true);
    setSearched(true);
    setResults([]);

    try {
      const response = await fetch('/api/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query, limit: 20 }),
      });
      const data = await response.json();
      setResults(data.data?.papers || []);
    } catch (error) {
      console.error('Search error:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Search Hero */}
      <div className="bg-gradient-to-r from-blue-600 to-indigo-700 py-16">
        <div className="max-w-3xl mx-auto px-6 text-center">
          <h1 className="text-3xl font-bold text-white mb-3">
            {locale === 'zh' ? '学术文献智能搜索' : 'Academic Literature Search'}
          </h1>
          <p className="text-blue-100 mb-8">
            {locale === 'zh'
              ? '全渠道搜索 Web of Science、Scopus、PubMed 等数据库'
              : 'Search Web of Science, Scopus, PubMed and more'}
          </p>

          <form onSubmit={handleSearch} className="relative">
            <div className="flex gap-2">
              <div className="relative flex-1">
                <Search className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400 w-5 h-5" />
                <input
                  type="text"
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  placeholder={t('search.placeholder')}
                  className="w-full pl-12 pr-4 py-4 text-gray-900 rounded-lg shadow-lg focus:outline-none focus:ring-2 focus:ring-blue-300"
                />
              </div>
              <button
                type="submit"
                disabled={loading}
                className="px-8 py-4 bg-white text-blue-600 font-semibold rounded-lg shadow hover:bg-gray-50 transition disabled:opacity-50"
              >
                {loading ? <Loader2 className="w-5 h-5 animate-spin" /> : t('search.button')}
              </button>
            </div>
          </form>
        </div>
      </div>

      {/* Results */}
      <div className="max-w-4xl mx-auto px-6 py-8">
        {searched && (
          <div className="mb-6">
            <h2 className="text-lg font-semibold text-gray-800">
              {results.length > 0 ? `${results.length} ${t('search.results')}` : t('search.noResults')}
            </h2>
          </div>
        )}

        {loading && (
          <div className="flex items-center justify-center py-12">
            <Loader2 className="w-8 h-8 text-blue-600 animate-spin" />
            <span className="ml-3 text-gray-500">{locale === 'zh' ? '搜索中...' : 'Searching...'}</span>
          </div>
        )}

        {!loading && results.length > 0 && (
          <div className="space-y-4">
            {results.map((paper, index) => (
              <div key={paper.id || index} className="bg-white rounded-lg shadow-sm border p-5 hover:shadow-md transition">
                <h3 className="text-lg font-semibold text-gray-900 mb-2">{paper.title}</h3>
                <p className="text-sm text-gray-600 mb-2">
                  {paper.authors.join(', ')} • {paper.year} • {paper.journal}
                </p>
                {paper.abstract && (
                  <p className="text-sm text-gray-500 line-clamp-3 mb-3">{paper.abstract}</p>
                )}
                <div className="flex gap-4 text-sm">
                  {paper.doi && (
                    <a href={`https://doi.org/${paper.doi}`} target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline flex items-center gap-1">
                      <ExternalLink className="w-4 h-4" /> DOI
                    </a>
                  )}
                  <button className="text-gray-600 hover:text-gray-900 flex items-center gap-1">
                    <FileText className="w-4 h-4" /> {locale === 'zh' ? '解析' : 'Parse'}
                  </button>
                  <button className="text-gray-600 hover:text-gray-900 flex items-center gap-1">
                    <Star className="w-4 h-4" /> {locale === 'zh' ? '收藏' : 'Save'}
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}

        {!loading && searched && results.length === 0 && (
          <div className="text-center py-12 bg-white rounded-lg border">
            <BookOpen className="w-12 h-12 text-gray-300 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-700 mb-2">
              {locale === 'zh' ? '未找到相关文献' : 'No results found'}
            </h3>
            <p className="text-gray-500">
              {locale === 'zh' ? '尝试调整搜索词' : 'Try adjusting your search terms'}
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
