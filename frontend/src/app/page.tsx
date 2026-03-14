'use client';

import { useState } from 'react';
import { Search, BookOpen, Download, ExternalLink } from 'lucide-react';

interface Paper {
  id: string;
  title: string;
  authors: string[];
  year: number;
  journal: string;
  doi?: string;
  abstract?: string;
  relevance_score?: number;
}

export default function Home() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<Paper[]>([]);
  const [loading, setLoading] = useState(false);
  const [searched, setSearched] = useState(false);

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;

    setLoading(true);
    setSearched(true);

    try {
      const response = await fetch('/api/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query,
          databases: ['pubmed'],
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
    <div className="max-w-4xl mx-auto px-4 py-8">
      {/* Search Section */}
      <div className="text-center mb-12">
        <h2 className="text-3xl font-bold text-gray-900 mb-4">
          Academic Literature Search
        </h2>
        <p className="text-gray-600 mb-8">
          Search across Web of Science, Scopus, PubMed, and more
        </p>

        <form onSubmit={handleSearch} className="relative max-w-2xl mx-auto">
          <Search className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400 w-5 h-5" />
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder='Enter your search query (e.g., "machine learning" AND "healthcare")'
            className="input pl-12 py-4 text-lg"
          />
          <button
            type="submit"
            disabled={loading}
            className="btn btn-primary absolute right-2 top-1/2 -translate-y-1/2"
          >
            {loading ? 'Searching...' : 'Search'}
          </button>
        </form>

        <div className="mt-4 text-sm text-gray-500">
          Supports: AND, OR, NOT, "exact phrases"
        </div>
      </div>

      {/* Results Section */}
      {searched && (
        <div>
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-xl font-semibold">
              {results.length > 0 ? `${results.length} Results` : 'No Results'}
            </h3>
            {results.length > 0 && (
              <button className="btn btn-secondary text-sm">
                <Download className="w-4 h-4 mr-2 inline" />
                Export
              </button>
            )}
          </div>

          <div className="space-y-4">
            {results.map((paper, index) => (
              <div key={paper.id || index} className="card hover:shadow-md transition-shadow">
                <div className="flex justify-between items-start">
                  <div className="flex-1">
                    <h4 className="font-semibold text-lg text-gray-900 mb-2">
                      {paper.title}
                    </h4>
                    <p className="text-sm text-gray-600 mb-2">
                      {paper.authors.join(', ')} • {paper.year} • {paper.journal}
                    </p>
                    {paper.abstract && (
                      <p className="text-sm text-gray-700 line-clamp-3">
                        {paper.abstract}
                      </p>
                    )}
                  </div>
                  {paper.relevance_score !== undefined && (
                    <div className="ml-4 text-right">
                      <div className="text-xs text-gray-500">Relevance</div>
                      <div className="text-lg font-semibold text-blue-600">
                        {(paper.relevance_score * 100).toFixed(0)}%
                      </div>
                    </div>
                  )}
                </div>

                <div className="mt-4 flex gap-3">
                  {paper.doi && (
                    <a
                      href={`https://doi.org/${paper.doi}`}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-sm text-blue-600 hover:underline flex items-center gap-1"
                    >
                      <ExternalLink className="w-4 h-4" />
                      DOI
                    </a>
                  )}
                  <button className="text-sm text-gray-600 hover:text-gray-900 flex items-center gap-1">
                    <BookOpen className="w-4 h-4" />
                    Parse Paper
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
