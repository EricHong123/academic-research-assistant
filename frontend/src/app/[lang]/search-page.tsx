'use client';

import { useState } from 'react';
import {
  Search,
  BookOpen,
  Download,
  ExternalLink,
  Filter,
  Database,
  FileText,
  Citation,
  Settings,
  History,
  Star,
  Trash2,
  Plus,
  ChevronDown,
  ChevronUp,
  Loader2
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
    { id: 'pubmed', name: 'PubMed', nameZh: 'PubMed生物医学' },
    { id: 'wos', name: 'Web of Science', nameZh: 'Web of Science' },
    { id: 'scopus', name: 'Scopus', nameZh: 'Scopus学术' },
    { id: 'google_scholar', name: 'Google Scholar', nameZh: '谷歌学术' },
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
      {/* 搜索头部 */}
      <div className="bg-white border-b border-slate-200 shadow-sm">
        <div className="max-w-7xl mx-auto px-6 py-8">
          <div className="text-center mb-6">
            <h1 className="text-2xl font-bold text-slate-800 mb-2">
              {t('search.title')}
            </h1>
            <p className="text-slate-500 text-sm">
              {t('search.subtitle')}
            </p>
          </div>

          {/* 搜索框 */}
          <form onSubmit={handleSearch} className="max-w-4xl mx-auto">
            <div className="relative flex gap-2">
              <div className="relative flex-1">
                <Search className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-400 w-5 h-5" />
                <input
                  type="text"
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  placeholder={t('search.placeholder')}
                  className="w-full pl-12 pr-4 py-4 text-base bg-white border border-slate-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none shadow-sm"
                />
              </div>
              <button
                type="button"
                onClick={() => setShowFilters(!showFilters)}
                className={`px-4 py-3 border rounded-xl flex items-center gap-2 transition-colors ${
                  showFilters ? 'bg-blue-50 border-blue-300 text-blue-700' : 'bg-white border-slate-300 hover:bg-slate-50'
                }`}
              >
                <Filter className="w-5 h-5" />
                <span className="text-sm font-medium">{locale === 'zh' ? '筛选' : 'Filters'}</span>
              </button>
              <button
                type="submit"
                disabled={loading}
                className="px-8 py-3 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-xl transition-colors shadow-sm disabled:opacity-50"
              >
                {loading ? (
                  <Loader2 className="w-5 h-5 animate-spin" />
                ) : (
                  t('search.button')
                )}
              </button>
            </div>

            {/* 筛选面板 */}
            {showFilters && (
              <div className="mt-4 p-4 bg-slate-50 rounded-xl border border-slate-200">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  {/* 数据库选择 */}
                  <div>
                    <label className="block text-sm font-medium text-slate-700 mb-2">
                      {locale === 'zh' ? '数据库' : 'Databases'}
                    </label>
                    <div className="space-y-2">
                      {databases.map((db) => (
                        <label key={db.id} className="flex items-center gap-2 cursor-pointer">
                          <input
                            type="checkbox"
                            checked={filters.databases.includes(db.id)}
                            onChange={(e) => {
                              const newDbs = e.target.checked
                                ? [...filters.databases, db.id]
                                : filters.databases.filter(d => d !== db.id);
                              setFilters({ ...filters, databases: newDbs });
                            }}
                            className="w-4 h-4 text-blue-600 rounded border-slate-300 focus:ring-blue-500"
                          />
                          <span className="text-sm text-slate-600">
                            {locale === 'zh' ? db.nameZh : db.name}
                          </span>
                        </label>
                      ))}
                    </div>
                  </div>

                  {/* 年份范围 */}
                  <div>
                    <label className="block text-sm font-medium text-slate-700 mb-2">
                      {locale === 'zh' ? '发表年份' : 'Publication Year'}
                    </label>
                    <div className="flex gap-2 items-center">
                      <input
                        type="number"
                        value={filters.yearFrom}
                        onChange={(e) => setFilters({ ...filters, yearFrom: parseInt(e.target.value) })}
                        className="w-24 px-3 py-2 text-sm border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
                        placeholder="From"
                      />
                      <span className="text-slate-400">-</span>
                      <input
                        type="number"
                        value={filters.yearTo}
                        onChange={(e) => setFilters({ ...filters, yearTo: parseInt(e.target.value) })}
                        className="w-24 px-3 py-2 text-sm border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
                        placeholder="To"
                      />
                    </div>
                  </div>

                  {/* 其他选项 */}
                  <div>
                    <label className="block text-sm font-medium text-slate-700 mb-2">
                      {locale === 'zh' ? '其他' : 'Other'}
                    </label>
                    <label className="flex items-center gap-2 cursor-pointer">
                      <input
                        type="checkbox"
                        checked={filters.hasPdf}
                        onChange={(e) => setFilters({ ...filters, hasPdf: e.target.checked })}
                        className="w-4 h-4 text-blue-600 rounded border-slate-300 focus:ring-blue-500"
                      />
                      <span className="text-sm text-slate-600">
                        {locale === 'zh' ? '仅显示有PDF的' : 'Has PDF only'}
                      </span>
                    </label>
                  </div>
                </div>
              </div>
            )}

            {/* 支持的语法 */}
            <div className="mt-3 text-xs text-slate-400 text-center">
              {t('search.supported')}
            </div>
          </form>
        </div>
      </div>

      {/* 结果区域 */}
      <div className="max-w-7xl mx-auto px-6 py-6">
        {searched && (
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-4">
              <h2 className="text-lg font-semibold text-slate-800">
                {results.length > 0 ? `${results.length} ${t('search.results')}` : t('search.noResults')}
              </h2>
              {results.length > 0 && (
                <button
                  onClick={selectAll}
                  className="text-sm text-blue-600 hover:text-blue-700"
                >
                  {selectedPapers.size === results.length
                    ? (locale === 'zh' ? '取消全选' : 'Deselect All')
                    : (locale === 'zh' ? '全选' : 'Select All')}
                </button>
              )}
            </div>

            {selectedPapers.size > 0 && (
              <div className="flex gap-2">
                <button className="px-4 py-2 bg-white border border-slate-300 rounded-lg text-sm font-medium text-slate-700 hover:bg-slate-50 flex items-center gap-2">
                  <Download className="w-4 h-4" />
                  {locale === 'zh' ? '导出选中' : 'Export Selected'}
                </button>
                <button className="px-4 py-2 bg-white border border-slate-300 rounded-lg text-sm font-medium text-slate-700 hover:bg-slate-50 flex items-center gap-2">
                  <Plus className="w-4 h-4" />
                  {locale === 'zh' ? '添加到项目' : 'Add to Project'}
                </button>
              </div>
            )}
          </div>
        )}

        {/* 加载状态 */}
        {loading && (
          <div className="flex items-center justify-center py-20">
            <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
            <span className="ml-3 text-slate-500">{locale === 'zh' ? '搜索中...' : 'Searching...'}</span>
          </div>
        )}

        {/* 结果列表 */}
        {!loading && results.length > 0 && (
          <div className="space-y-4">
            {results.map((paper, index) => (
              <div
                key={paper.id || index}
                className={`bg-white rounded-xl border transition-all ${
                  selectedPapers.has(paper.id) ? 'border-blue-500 shadow-md' : 'border-slate-200 hover:border-slate-300'
                }`}
              >
                <div className="p-5">
                  <div className="flex items-start gap-4">
                    {/* 选择框 */}
                    <div className="pt-1">
                      <input
                        type="checkbox"
                        checked={selectedPapers.has(paper.id)}
                        onChange={() => togglePaperSelection(paper.id || String(index))}
                        className="w-5 h-5 text-blue-600 rounded border-slate-300 focus:ring-blue-500 cursor-pointer"
                      />
                    </div>

                    {/* 论文信息 */}
                    <div className="flex-1 min-w-0">
                      <div className="flex items-start justify-between gap-4">
                        <div className="flex-1">
                          <h3 className="text-base font-semibold text-slate-900 leading-snug mb-2 hover:text-blue-600 cursor-pointer">
                            {paper.title}
                          </h3>
                          <div className="flex flex-wrap items-center gap-2 text-sm text-slate-600 mb-2">
                            <span className="font-medium">{paper.authors.join(', ')}</span>
                            <span className="text-slate-300">|</span>
                            <span>{paper.year}</span>
                            <span className="text-slate-300">|</span>
                            <span className="italic">{paper.journal}</span>
                            {paper.source && (
                              <>
                                <span className="text-slate-300">|</span>
                                <span className="px-2 py-0.5 bg-slate-100 rounded text-xs font-medium">
                                  {paper.source.toUpperCase()}
                                </span>
                              </>
                            )}
                          </div>
                        </div>

                        {/* 相关性分数 */}
                        {paper.relevance_score !== undefined && (
                          <div className="text-right flex-shrink-0">
                            <div className="text-xs text-slate-500 mb-1">{t('search.relevance')}</div>
                            <div className="px-3 py-1 bg-blue-50 text-blue-700 rounded-lg font-semibold">
                              {(paper.relevance_score * 100).toFixed(0)}%
                            </div>
                          </div>
                        )}
                      </div>

                      {/* 摘要 */}
                      {paper.abstract && (
                        <p className="text-sm text-slate-600 leading-relaxed mb-3 line-clamp-2">
                          {paper.abstract}
                        </p>
                      )}

                      {/* 操作按钮 */}
                      <div className="flex items-center gap-4 pt-2 border-t border-slate-100">
                        {paper.doi && (
                          <a
                            href={`https://doi.org/${paper.doi}`}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="inline-flex items-center gap-1 text-sm text-blue-600 hover:text-blue-700"
                          >
                            <ExternalLink className="w-4 h-4" />
                            DOI
                          </a>
                        )}
                        <button className="inline-flex items-center gap-1 text-sm text-slate-600 hover:text-slate-800">
                          <FileText className="w-4 h-4" />
                          {t('search.parsePaper')}
                        </button>
                        <button className="inline-flex items-center gap-1 text-sm text-slate-600 hover:text-slate-800">
                          <Citation className="w-4 h-4" />
                          {locale === 'zh' ? '引用' : 'Cite'}
                        </button>
                        <button className="inline-flex items-center gap-1 text-sm text-slate-600 hover:text-slate-800">
                          <Star className="w-4 h-4" />
                          {locale === 'zh' ? '收藏' : 'Save'}
                        </button>
                        <button
                          onClick={() => setExpandedPaper(expandedPaper === (paper.id || String(index)) ? null : (paper.id || String(index)))}
                          className="inline-flex items-center gap-1 text-sm text-slate-600 hover:text-slate-800 ml-auto"
                        >
                          {expandedPaper === (paper.id || String(index)) ? (
                            <>
                              <ChevronUp className="w-4 h-4" />
                              {locale === 'zh' ? '收起' : 'Collapse'}
                            </>
                          ) : (
                            <>
                              <ChevronDown className="w-4 h-4" />
                              {locale === 'zh' ? '展开' : 'Expand'}
                            </>
                          )}
                        </button>
                      </div>
                    </div>
                  </div>
                </div>

                {/* 展开详情 */}
                {expandedPaper === (paper.id || String(index)) && (
                  <div className="px-5 py-4 bg-slate-50 border-t border-slate-200">
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                      <div>
                        <div className="text-slate-500 mb-1">{locale === 'zh' ? 'DOI' : 'DOI'}</div>
                        <div className="font-mono text-xs text-slate-700 break-all">{paper.doi || '-'}</div>
                      </div>
                      <div>
                        <div className="text-slate-500 mb-1">{locale === 'zh' ? '发表年份' : 'Year'}</div>
                        <div className="text-slate-700">{paper.year || '-'}</div>
                      </div>
                      <div>
                        <div className="text-slate-500 mb-1">{locale === 'zh' ? '被引次数' : 'Citations'}</div>
                        <div className="text-slate-700">{paper.citations || 0}</div>
                      </div>
                      <div>
                        <div className="text-slate-500 mb-1">{locale === 'zh' ? '来源' : 'Source'}</div>
                        <div className="text-slate-700">{paper.source || '-'}</div>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}

        {/* 空状态 */}
        {!loading && searched && results.length === 0 && (
          <div className="text-center py-20">
            <Search className="w-16 h-16 text-slate-300 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-slate-700 mb-2">
              {locale === 'zh' ? '未找到相关文献' : 'No results found'}
            </h3>
            <p className="text-slate-500">
              {locale === 'zh'
                ? '尝试调整搜索词或筛选条件'
                : 'Try adjusting your search terms or filters'}
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
