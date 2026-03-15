'use client';

import { useState } from 'react';
import {
  Search,
  Filter,
  Loader2,
  BookOpen,
  ExternalLink,
  Star,
  FileText,
  MoreVertical,
  Database,
  Calendar,
  ChevronDown,
  X,
  Sparkles,
  Brain,
  Target,
  TrendingUp,
  Zap
} from 'lucide-react';
import { useI18n } from '@/lib/i18n';

interface Paper {
  id: string;
  title: string;
  authors: string[];
  year: number;
  journal: string;
  doi?: string;
  abstract?: string;
  relevance_score?: number;
  citations?: number;
  source?: string;
}

interface SearchFilters {
  yearFrom: number;
  yearTo: number;
  databases: string[];
}

export default function SearchPage() {
  const { t, locale } = useI18n();
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<Paper[]>([]);
  const [loading, setLoading] = useState(false);
  const [searched, setSearched] = useState(false);
  const [showFilters, setShowFilters] = useState(false);

  const [filters, setFilters] = useState<SearchFilters>({
    yearFrom: 2020,
    yearTo: 2024,
    databases: ['pubmed'],
  });

  const databases = [
    { id: 'pubmed', name: 'PubMed', color: 'from-green-500 to-emerald-600' },
    { id: 'wos', name: 'Web of Science', color: 'from-blue-500 to-cyan-500' },
    { id: 'scopus', name: 'Scopus', color: 'from-orange-500 to-amber-500' },
    { id: 'google_scholar', name: 'Google Scholar', color: 'from-gray-500 to-slate-600' },
  ];

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
        body: JSON.stringify({
          query,
          databases: filters.databases,
          filters: {
            year_from: filters.yearFrom,
            year_to: filters.yearTo,
          },
          limit: 20,
        }),
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
    <div className="min-h-screen pt-16">
      {/* Hero Section */}
      <div className="relative overflow-hidden">
        {/* Background Effects */}
        <div className="absolute inset-0 bg-[#0a0a0f]" />
        <div className="absolute inset-0 grid-bg opacity-50" />
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-indigo-500/10 rounded-full blur-[120px]" />
        <div className="absolute top-1/4 right-1/4 w-[400px] h-[400px] bg-purple-500/10 rounded-full blur-[100px]" />

        <div className="relative max-w-4xl mx-auto px-6 py-20 text-center">
          {/* Badge */}
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-white/5 border border-white/10 mb-8">
            <Brain className="w-4 h-4 text-indigo-400" />
            <span className="text-sm text-white/60">AI-Powered Academic Search</span>
          </div>

          <h1 className="text-4xl md:text-5xl font-bold mb-4">
            <span className="bg-gradient-to-r from-white via-indigo-200 to-cyan-200 bg-clip-text text-transparent">
              {locale === 'zh' ? '探索学术前沿' : 'Discover Academic Insights'}
            </span>
          </h1>
          <p className="text-lg text-white/50 mb-10 max-w-2xl mx-auto">
            {locale === 'zh'
              ? '全渠道搜索 Web of Science、Scopus、PubMed，AI 驱动的智能排序'
              : 'Search across WOS, Scopus, PubMed with AI-powered relevance ranking'}
          </p>

          {/* Search Form */}
          <form onSubmit={handleSearch} className="relative max-w-2xl mx-auto">
            <div className="relative flex items-center gap-2 p-2 pr-3 bg-[#12121a]/80 backdrop-blur-xl border border-white/10 rounded-2xl">
              <div className="flex-1 relative">
                <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-white/30" />
                <input
                  type="text"
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  placeholder={t('search.placeholder')}
                  className="w-full pl-12 pr-4 py-4 bg-transparent text-white placeholder:text-white/30 text-base outline-none"
                />
              </div>
              <button
                type="button"
                onClick={() => setShowFilters(!showFilters)}
                className={`p-3 rounded-xl transition-all ${
                  showFilters ? 'bg-indigo-500/20 text-indigo-400' : 'text-white/40 hover:text-white hover:bg-white/5'
                }`}
              >
                <Filter className="w-5 h-5" />
              </button>
              <button
                type="submit"
                disabled={loading}
                className="px-6 py-3 bg-gradient-to-r from-indigo-500 via-purple-500 to-cyan-500 text-white font-semibold rounded-xl hover:opacity-90 transition-all disabled:opacity-50 flex items-center gap-2"
              >
                {loading ? (
                  <Loader2 className="w-5 h-5 animate-spin" />
                ) : (
                  <Zap className="w-5 h-5" />
                )}
                <span>{t('search.button')}</span>
              </button>
            </div>

            {/* Filters Panel */}
            {showFilters && (
              <div className="absolute top-full left-0 right-0 mt-4 p-6 bg-[#12121a]/95 backdrop-blur-xl border border-white/10 rounded-2xl animate-fade-in">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-white font-medium flex items-center gap-2">
                    <Target className="w-4 h-4 text-indigo-400" />
                    {locale === 'zh' ? '筛选条件' : 'Filters'}
                  </h3>
                  <button onClick={() => setShowFilters(false)} className="text-white/40 hover:text-white">
                    <X className="w-4 h-4" />
                  </button>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {/* Database Selection */}
                  <div>
                    <label className="block text-sm text-white/50 mb-3 flex items-center gap-2">
                      <Database className="w-4 h-4" />
                      {locale === 'zh' ? '数据库' : 'Databases'}
                    </label>
                    <div className="flex flex-wrap gap-2">
                      {databases.map((db) => (
                        <button
                          key={db.id}
                          onClick={() => {
                            const newDbs = filters.databases.includes(db.id)
                              ? filters.databases.filter(d => d !== db.id)
                              : [...filters.databases, db.id];
                            setFilters({ ...filters, databases: newDbs });
                          }}
                          className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                            filters.databases.includes(db.id)
                              ? `bg-gradient-to-r ${db.color} text-white`
                              : 'bg-white/5 text-white/40 hover:text-white hover:bg-white/10'
                          }`}
                        >
                          {locale === 'zh' ? db.name : db.name}
                        </button>
                      ))}
                    </div>
                  </div>

                  {/* Year Range */}
                  <div>
                    <label className="block text-sm text-white/50 mb-3 flex items-center gap-2">
                      <Calendar className="w-4 h-4" />
                      {locale === 'zh' ? '发表年份' : 'Publication Year'}
                    </label>
                    <div className="flex items-center gap-3">
                      <input
                        type="number"
                        value={filters.yearFrom}
                        onChange={(e) => setFilters({ ...filters, yearFrom: parseInt(e.target.value) })}
                        className="w-24 px-4 py-2 bg-white/5 border border-white/10 rounded-lg text-white text-sm focus:border-indigo-500 outline-none"
                      />
                      <span className="text-white/30">-</span>
                      <input
                        type="number"
                        value={filters.yearTo}
                        onChange={(e) => setFilters({ ...filters, yearTo: parseInt(e.target.value) })}
                        className="w-24 px-4 py-2 bg-white/5 border border-white/10 rounded-lg text-white text-sm focus:border-indigo-500 outline-none"
                      />
                    </div>
                  </div>
                </div>
              </div>
            )}
          </form>

          {/* Stats */}
          <div className="flex flex-wrap justify-center gap-8 mt-12">
            <div className="text-center">
              <div className="text-2xl font-bold text-white">500M+</div>
              <div className="text-sm text-white/40">{locale === 'zh' ? '学术论文' : 'Academic Papers'}</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-white">10+</div>
              <div className="text-sm text-white/40">{locale === 'zh' ? '数据源' : 'Data Sources'}</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-white">99.9%</div>
              <div className="text-sm text-white/40">{locale === 'zh' ? '准确率' : 'Accuracy'}</div>
            </div>
          </div>
        </div>
      </div>

      {/* Results Section */}
      <div className="max-w-5xl mx-auto px-6 py-12">
        {searched && (
          <div className="flex items-center justify-between mb-8">
            <div className="flex items-center gap-3">
              <div className="w-px h-6 bg-white/10" />
              <h2 className="text-xl font-semibold text-white">
                {results.length > 0 ? `${results.length} ${t('search.results')}` : t('search.noResults')}
              </h2>
            </div>
            {results.length > 0 && (
              <div className="flex items-center gap-2 text-sm text-white/40">
                <TrendingUp className="w-4 h-4" />
                {locale === 'zh' ? '按相关性排序' : 'Sorted by relevance'}
              </div>
            )}
          </div>
        )}

        {/* Loading */}
        {loading && (
          <div className="flex flex-col items-center justify-center py-20">
            <div className="relative mb-4">
              <div className="w-16 h-16 border-2 border-white/10 border-t-indigo-500 rounded-full animate-spin" />
              <Search className="absolute inset-0 m-auto w-6 h-6 text-indigo-500 animate-pulse" />
            </div>
            <p className="text-white/40">{locale === 'zh' ? '搜索中...' : 'Searching...'}</p>
          </div>
        )}

        {/* Results */}
        {!loading && results.length > 0 && (
          <div className="space-y-4">
            {results.map((paper, index) => (
              <div
                key={paper.id || index}
                className="glass-card p-6 animate-slide-up"
                style={{ animationDelay: `${index * 0.05}s` }}
              >
                <div className="flex items-start justify-between gap-4">
                  <div className="flex-1 min-w-0">
                    {/* Source Badge */}
                    {paper.source && (
                      <span className={`inline-block px-2 py-0.5 rounded text-xs font-medium mb-2 bg-gradient-to-r ${
                        paper.source === 'pubmed' ? 'from-green-500 to-emerald-600' :
                        paper.source === 'wos' ? 'from-blue-500 to-cyan-500' :
                        paper.source === 'scopus' ? 'from-orange-500 to-amber-500' :
                        'from-gray-500 to-slate-600'
                      } text-white`}>
                        {paper.source.toUpperCase()}
                      </span>
                    )}

                    <h3 className="text-lg font-semibold text-white mb-2 hover:text-indigo-400 cursor-pointer line-clamp-2">
                      {paper.title}
                    </h3>

                    <div className="flex flex-wrap items-center gap-2 text-sm text-white/50 mb-3">
                      <span className="text-white/70">{paper.authors.join(', ')}</span>
                      <span className="w-1 h-1 rounded-full bg-white/20" />
                      <span>{paper.year}</span>
                      <span className="w-1 h-1 rounded-full bg-white/20" />
                      <span className="italic">{paper.journal}</span>
                    </div>

                    {paper.abstract && (
                      <p className="text-sm text-white/40 line-clamp-2 mb-4">{paper.abstract}</p>
                    )}

                    <div className="flex items-center gap-3">
                      {paper.doi && (
                        <a
                          href={`https://doi.org/${paper.doi}`}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="inline-flex items-center gap-1.5 text-sm text-indigo-400 hover:text-indigo-300"
                        >
                          <ExternalLink className="w-4 h-4" />
                          DOI
                        </a>
                      )}
                      <button className="inline-flex items-center gap-1.5 text-sm text-white/40 hover:text-white">
                        <FileText className="w-4 h-4" />
                        {locale === 'zh' ? '解析' : 'Parse'}
                      </button>
                      <button className="inline-flex items-center gap-1.5 text-sm text-white/40 hover:text-white">
                        <Star className="w-4 h-4" />
                        {locale === 'zh' ? '收藏' : 'Save'}
                      </button>
                    </div>
                  </div>

                  {/* Relevance Score */}
                  {paper.relevance_score !== undefined && (
                    <div className="flex-shrink-0 text-center">
                      <div className="text-xs text-white/40 mb-1">{t('search.relevance')}</div>
                      <div className="w-14 h-14 rounded-xl bg-gradient-to-br from-indigo-500/20 to-purple-500/20 border border-indigo-500/30 flex items-center justify-center">
                        <span className="text-lg font-bold text-indigo-400">
                          {(paper.relevance_score * 100).toFixed(0)}%
                        </span>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Empty State */}
        {!loading && searched && results.length === 0 && (
          <div className="text-center py-20">
            <div className="w-20 h-20 mx-auto mb-6 rounded-2xl bg-white/5 flex items-center justify-center">
              <Search className="w-10 h-10 text-white/20" />
            </div>
            <h3 className="text-xl font-semibold text-white mb-2">
              {locale === 'zh' ? '未找到相关文献' : 'No results found'}
            </h3>
            <p className="text-white/40">
              {locale === 'zh' ? '尝试调整搜索词或筛选条件' : 'Try adjusting your search terms or filters'}
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
