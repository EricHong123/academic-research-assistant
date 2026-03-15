'use client';

import { useState } from 'react';
import {
  Search,
  BookOpen,
  Download,
  ExternalLink,
  Filter,
  FileText,
  Quote,
  Star,
  Plus,
  ChevronDown,
  ChevronUp,
  Loader2,
  Brain,
  Database,
  Calendar,
  CheckCircle,
  X
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
  hasPdf: boolean;
}

export default function SearchPage() {
  const { t, locale } = useI18n();
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<Paper[]>([]);
  const [loading, setLoading] = useState(false);
  const [searched, setSearched] = useState(false);
  const [showFilters, setShowFilters] = useState(false);
  const [selectedPapers, setSelectedPapers] = useState<Set<string>>(new Set());
  const [expandedPaper, setExpandedPaper] = useState<string | null>(null);

  const [filters, setFilters] = useState<SearchFilters>({
    yearFrom: 2020,
    yearTo: 2024,
    databases: ['pubmed'],
    hasPdf: false,
  });

  const databases = [
    { id: 'pubmed', name: 'PubMed', nameZh: 'PubMed生物医学', color: 'bg-green-500' },
    { id: 'wos', name: 'Web of Science', nameZh: 'Web of Science', color: 'bg-blue-500' },
    { id: 'scopus', name: 'Scopus', nameZh: 'Scopus学术', color: 'bg-orange-500' },
    { id: 'google_scholar', name: 'Google Scholar', nameZh: '谷歌学术', color: 'bg-gray-500' },
  ];

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;

    setLoading(true);
    setSearched(true);
    setResults([]);
    setSelectedPapers(new Set());

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
          limit: 50,
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

  const togglePaperSelection = (id: string) => {
    const newSelected = new Set(selectedPapers);
    if (newSelected.has(id)) {
      newSelected.delete(id);
    } else {
      newSelected.add(id);
    }
    setSelectedPapers(newSelected);
  };

  const selectAll = () => {
    if (selectedPapers.size === results.length) {
      setSelectedPapers(new Set());
    } else {
      setSelectedPapers(new Set(results.map(r => r.id)));
    }
  };

  return (
    <div className="min-h-screen bg-slate-50">
      {/* Hero Search Section */}
      <div className="bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 pt-12 pb-20">
        <div className="max-w-4xl mx-auto px-6 text-center">
          {/* Badge */}
          <div className="inline-flex items-center gap-2 px-4 py-1.5 bg-white/10 backdrop-blur-sm rounded-full border border-white/20 mb-6">
            <Brain className="w-4 h-4 text-blue-400" />
            <span className="text-sm text-blue-200 font-medium">AI-Powered Academic Search</span>
          </div>

          <h1 className="text-3xl md:text-4xl font-bold text-white mb-4">
            {locale === 'zh' ? '探索学术文献的智能助手' : 'Your AI-Powered Research Companion'}
          </h1>
          <p className="text-lg text-slate-300 mb-8 max-w-2xl mx-auto">
            {locale === 'zh'
              ? '全渠道搜索 Web of Science、Scopus、PubMed 等数据库，AI 驱动的相关性排序，助您快速找到前沿研究。'
              : 'Search across Web of Science, Scopus, PubMed and more with AI-powered relevance ranking to discover cutting-edge research.'}
          </p>

          {/* Search Form */}
          <form onSubmit={handleSearch} className="relative">
            <div className="relative flex flex-col sm:flex-row gap-3 bg-white rounded-2xl p-2 shadow-2xl">
              <div className="relative flex-1">
                <Search className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-400 w-5 h-5" />
                <input
                  type="text"
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  placeholder={t('search.placeholder')}
                  className="w-full pl-12 pr-4 py-4 text-base bg-transparent text-slate-900 placeholder:text-slate-400 outline-none"
                />
              </div>
              <div className="flex gap-2">
                <button
                  type="button"
                  onClick={() => setShowFilters(!showFilters)}
                  className={`px-5 py-3 rounded-xl flex items-center gap-2 font-medium transition-colors ${
                    showFilters ? 'bg-blue-100 text-blue-700' : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
                  }`}
                >
                  <Filter className="w-5 h-5" />
                  <span className="hidden sm:inline">{locale === 'zh' ? '筛选' : 'Filters'}</span>
                </button>
                <button
                  type="submit"
                  disabled={loading}
                  className="px-8 py-3 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-xl transition-colors shadow-lg shadow-blue-600/25 disabled:opacity-50 flex items-center gap-2"
                >
                  {loading ? (
                    <Loader2 className="w-5 h-5 animate-spin" />
                  ) : (
                    <Search className="w-5 h-5" />
                  )}
                  <span>{t('search.button')}</span>
                </button>
              </div>
            </div>

            {/* Filters Panel */}
            {showFilters && (
              <div className="mt-4 p-6 bg-white/10 backdrop-blur-sm rounded-2xl border border-white/20 text-left animate-slide-down">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  {/* Database Selection */}
                  <div>
                    <label className="block text-sm font-medium text-slate-200 mb-3">
                      <Database className="w-4 h-4 inline mr-2" />
                      {locale === 'zh' ? '数据库' : 'Databases'}
                    </label>
                    <div className="space-y-2">
                      {databases.map((db) => (
                        <label key={db.id} className="flex items-center gap-3 cursor-pointer group">
                          <div className={`w-5 h-5 rounded-md flex items-center justify-center transition-colors ${filters.databases.includes(db.id) ? 'bg-blue-500' : 'bg-white/20 group-hover:bg-white/30'}`}>
                            {filters.databases.includes(db.id) && <CheckCircle className="w-3.5 h-3.5 text-white" />}
                          </div>
                          <input
                            type="checkbox"
                            checked={filters.databases.includes(db.id)}
                            onChange={(e) => {
                              const newDbs = e.target.checked
                                ? [...filters.databases, db.id]
                                : filters.databases.filter(d => d !== db.id);
                              setFilters({ ...filters, databases: newDbs });
                            }}
                            className="hidden"
                          />
                          <span className="text-sm text-slate-300">
                            {locale === 'zh' ? db.nameZh : db.name}
                          </span>
                        </label>
                      ))}
                    </div>
                  </div>

                  {/* Year Range */}
                  <div>
                    <label className="block text-sm font-medium text-slate-200 mb-3">
                      <Calendar className="w-4 h-4 inline mr-2" />
                      {locale === 'zh' ? '发表年份' : 'Publication Year'}
                    </label>
                    <div className="flex gap-3 items-center">
                      <input
                        type="number"
                        value={filters.yearFrom}
                        onChange={(e) => setFilters({ ...filters, yearFrom: parseInt(e.target.value) })}
                        className="w-full px-4 py-2.5 text-sm bg-white/10 border border-white/20 rounded-lg text-white placeholder:text-slate-400 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
                      />
                      <span className="text-slate-400">-</span>
                      <input
                        type="number"
                        value={filters.yearTo}
                        onChange={(e) => setFilters({ ...filters, yearTo: parseInt(e.target.value) })}
                        className="w-full px-4 py-2.5 text-sm bg-white/10 border border-white/20 rounded-lg text-white placeholder:text-slate-400 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
                      />
                    </div>
                  </div>

                  {/* Other Options */}
                  <div>
                    <label className="block text-sm font-medium text-slate-200 mb-3">
                      {locale === 'zh' ? '其他选项' : 'Other Options'}
                    </label>
                    <label className="flex items-center gap-3 cursor-pointer">
                      <div className={`w-5 h-5 rounded-md flex items-center justify-center transition-colors ${filters.hasPdf ? 'bg-blue-500' : 'bg-white/20'}`}>
                        {filters.hasPdf && <CheckCircle className="w-3.5 h-3.5 text-white" />}
                      </div>
                      <input
                        type="checkbox"
                        checked={filters.hasPdf}
                        onChange={(e) => setFilters({ ...filters, hasPdf: e.target.checked })}
                        className="hidden"
                      />
                      <span className="text-sm text-slate-300">
                        {locale === 'zh' ? '仅显示有PDF的' : 'Has PDF only'}
                      </span>
                    </label>
                  </div>
                </div>

                {/* Close Filters */}
                <div className="mt-4 pt-4 border-t border-white/20 flex justify-end">
                  <button
                    type="button"
                    onClick={() => setShowFilters(false)}
                    className="text-sm text-slate-300 hover:text-white flex items-center gap-1"
                  >
                    <X className="w-4 h-4" />
                    {locale === 'zh' ? '收起筛选' : 'Close Filters'}
                  </button>
                </div>
              </div>
            )}
          </form>

          {/* Supported syntax hint */}
          <div className="mt-4 text-xs text-slate-400">
            {t('search.supported')}
          </div>
        </div>
      </div>

      {/* Results Section */}
      <div className="max-w-5xl mx-auto px-6 -mt-8 pb-12">
        {/* Results Header */}
        {searched && (
          <div className="flex items-center justify-between mb-6 bg-white rounded-xl p-4 shadow-sm border border-slate-200">
            <div className="flex items-center gap-4">
              <h2 className="text-lg font-semibold text-slate-800">
                {results.length > 0 ? `${results.length} ${t('search.results')}` : t('search.noResults')}
              </h2>
              {results.length > 0 && (
                <button
                  onClick={selectAll}
                  className="text-sm text-blue-600 hover:text-blue-700 font-medium"
                >
                  {selectedPapers.size === results.length
                    ? (locale === 'zh' ? '取消全选' : 'Deselect All')
                    : (locale === 'zh' ? '全选' : 'Select All')}
                </button>
              )}
            </div>

            {selectedPapers.size > 0 && (
              <div className="flex gap-2">
                <button className="btn btn-secondary btn-sm">
                  <Download className="w-4 h-4" />
                  {locale === 'zh' ? '导出' : 'Export'}
                </button>
                <button className="btn btn-primary btn-sm">
                  <Plus className="w-4 h-4" />
                  {locale === 'zh' ? '添加到项目' : 'Add to Project'}
                </button>
              </div>
            )}
          </div>
        )}

        {/* Loading State */}
        {loading && (
          <div className="flex flex-col items-center justify-center py-20">
            <div className="relative">
              <div className="w-16 h-16 border-4 border-blue-100 border-t-blue-600 rounded-full animate-spin"></div>
              <div className="absolute inset-0 flex items-center justify-center">
                <Search className="w-6 h-6 text-blue-600 animate-pulse" />
              </div>
            </div>
            <p className="mt-4 text-slate-500">{locale === 'zh' ? '搜索中...' : 'Searching...'}</p>
          </div>
        )}

        {/* Results List */}
        {!loading && results.length > 0 && (
          <div className="space-y-4">
            {results.map((paper, index) => (
              <div
                key={paper.id || index}
                className={`card card-hover stagger-item ${selectedPapers.has(paper.id) ? 'ring-2 ring-blue-500 ring-offset-2' : ''}`}
              >
                <div className="p-5">
                  <div className="flex items-start gap-4">
                    {/* Selection Checkbox */}
                    <div className="pt-1">
                      <button
                        onClick={() => togglePaperSelection(paper.id || String(index))}
                        className={`w-6 h-6 rounded-lg border-2 flex items-center justify-center transition-colors ${
                          selectedPapers.has(paper.id)
                            ? 'bg-blue-500 border-blue-500'
                            : 'border-slate-300 hover:border-blue-400'
                        }`}
                      >
                        {selectedPapers.has(paper.id) && <CheckCircle className="w-4 h-4 text-white" />}
                      </button>
                    </div>

                    {/* Paper Info */}
                    <div className="flex-1 min-w-0">
                      <div className="flex items-start justify-between gap-4 mb-2">
                        <div className="flex-1">
                          <h3 className="text-base font-semibold text-slate-900 leading-snug hover:text-blue-600 cursor-pointer line-clamp-2">
                            {paper.title}
                          </h3>
                          <div className="flex flex-wrap items-center gap-2 text-sm text-slate-600 mt-2">
                            <span className="font-medium">{paper.authors.join(', ')}</span>
                            <span className="text-slate-300">|</span>
                            <span className="font-medium">{paper.year}</span>
                            <span className="text-slate-300">|</span>
                            <span className="italic">{paper.journal}</span>
                            {paper.source && (
                              <>
                                <span className="text-slate-300">|</span>
                                <span className="px-2 py-0.5 bg-slate-100 rounded text-xs font-semibold uppercase tracking-wider">
                                  {paper.source}
                                </span>
                              </>
                            )}
                          </div>
                        </div>

                        {/* Relevance Score */}
                        {paper.relevance_score !== undefined && (
                          <div className="text-right flex-shrink-0">
                            <div className="text-xs text-slate-500 mb-1">{t('search.relevance')}</div>
                            <div className="px-3 py-1.5 bg-gradient-to-r from-blue-500 to-indigo-500 text-white rounded-lg font-bold text-sm">
                              {(paper.relevance_score * 100).toFixed(0)}%
                            </div>
                          </div>
                        )}
                      </div>

                      {/* Abstract */}
                      {paper.abstract && (
                        <p className="text-sm text-slate-600 leading-relaxed mb-4 line-clamp-3">
                          {paper.abstract}
                        </p>
                      )}

                      {/* Action Buttons */}
                      <div className="flex items-center gap-3 pt-3 border-t border-slate-100 flex-wrap">
                        {paper.doi && (
                          <a
                            href={`https://doi.org/${paper.doi}`}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="inline-flex items-center gap-1.5 text-sm text-blue-600 hover:text-blue-700 font-medium"
                          >
                            <ExternalLink className="w-4 h-4" />
                            DOI
                          </a>
                        )}
                        <button className="inline-flex items-center gap-1.5 text-sm text-slate-600 hover:text-slate-900 font-medium">
                          <FileText className="w-4 h-4" />
                          {t('search.parsePaper')}
                        </button>
                        <button className="inline-flex items-center gap-1.5 text-sm text-slate-600 hover:text-slate-900 font-medium">
                          <Quote className="w-4 h-4" />
                          {locale === 'zh' ? '引用' : 'Cite'}
                        </button>
                        <button className="inline-flex items-center gap-1.5 text-sm text-slate-600 hover:text-slate-900 font-medium">
                          <Star className="w-4 h-4" />
                          {locale === 'zh' ? '收藏' : 'Save'}
                        </button>
                        <button
                          onClick={() => setExpandedPaper(expandedPaper === (paper.id || String(index)) ? null : (paper.id || String(index)))}
                          className="inline-flex items-center gap-1.5 text-sm text-slate-600 hover:text-slate-900 font-medium ml-auto"
                        >
                          {expandedPaper === (paper.id || String(index)) ? (
                            <>
                              <ChevronUp className="w-4 h-4" />
                              {locale === 'zh' ? '收起' : 'Less'}
                            </>
                          ) : (
                            <>
                              <ChevronDown className="w-4 h-4" />
                              {locale === 'zh' ? '更多' : 'More'}
                            </>
                          )}
                        </button>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Expanded Details */}
                {expandedPaper === (paper.id || String(index)) && (
                  <div className="px-5 py-4 bg-slate-50 border-t border-slate-200 rounded-b-2xl animate-slide-down">
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                      <div>
                        <div className="text-xs font-medium text-slate-500 mb-1">{locale === 'zh' ? 'DOI' : 'DOI'}</div>
                        <div className="text-sm text-slate-700 font-mono break-all">{paper.doi || '-'}</div>
                      </div>
                      <div>
                        <div className="text-xs font-medium text-slate-500 mb-1">{locale === 'zh' ? '发表年份' : 'Year'}</div>
                        <div className="text-sm text-slate-700">{paper.year || '-'}</div>
                      </div>
                      <div>
                        <div className="text-xs font-medium text-slate-500 mb-1">{locale === 'zh' ? '被引次数' : 'Citations'}</div>
                        <div className="text-sm text-slate-700">{paper.citations || 0}</div>
                      </div>
                      <div>
                        <div className="text-xs font-medium text-slate-500 mb-1">{locale === 'zh' ? '来源' : 'Source'}</div>
                        <div className="text-sm text-slate-700">{paper.source || '-'}</div>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}

        {/* Empty State */}
        {!loading && searched && results.length === 0 && (
          <div className="text-center py-20 bg-white rounded-2xl border border-slate-200">
            <div className="w-20 h-20 bg-slate-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <Search className="w-10 h-10 text-slate-300" />
            </div>
            <h3 className="text-lg font-semibold text-slate-700 mb-2">
              {locale === 'zh' ? '未找到相关文献' : 'No results found'}
            </h3>
            <p className="text-slate-500 max-w-md mx-auto">
              {locale === 'zh'
                ? '尝试调整搜索词或筛选条件，或者使用更通用的关键词。'
                : 'Try adjusting your search terms or filters, or use more general keywords.'}
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
