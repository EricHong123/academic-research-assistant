'use client';

import { useState, useEffect } from 'react';
import { Plus, Folder, FileText, Trash2, Search, MoreVertical, Calendar, ChevronRight } from 'lucide-react';
import { useI18n } from '@/lib/i18n';

interface Project {
  id: string;
  name: string;
  description?: string;
  paper_count: number;
  created_at: string;
  updated_at: string;
}

export default function ProjectsPage() {
  const { t, locale } = useI18n();
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);
  const [showCreate, setShowCreate] = useState(false);
  const [newProject, setNewProject] = useState({ name: '', description: '' });
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    fetchProjects();
  }, []);

  const fetchProjects = async () => {
    try {
      const response = await fetch('/api/projects');
      const data = await response.json();
      setProjects(data.data?.projects || []);
    } catch (error) {
      console.error('Error fetching projects:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const response = await fetch('/api/projects', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(newProject),
      });
      const data = await response.json();
      if (data.success) {
        setProjects((prev) => [data.data, ...prev]);
        setShowCreate(false);
        setNewProject({ name: '', description: '' });
      }
    } catch (error) {
      console.error('Error creating project:', error);
    }
  };

  const handleDelete = async (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    if (!confirm(locale === 'zh' ? '确定删除此项目？' : 'Delete this project?')) return;
    try {
      await fetch(`/api/projects/${id}`, { method: 'DELETE' });
      setProjects((prev) => prev.filter((p) => p.id !== id));
    } catch (error) {
      console.error('Error deleting project:', error);
    }
  };

  const filteredProjects = projects.filter(
    (p) =>
      p.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      p.description?.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="min-h-screen bg-slate-50">
      {/* 头部 */}
      <div className="bg-white border-b border-slate-200">
        <div className="max-w-6xl mx-auto px-6 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-slate-800">{t('projects.title')}</h1>
              <p className="text-slate-500 mt-1">
                {locale === 'zh'
                  ? '管理您的文献收藏和研究项目'
                  : 'Manage your literature collections and research projects'}
              </p>
            </div>
            <button
              onClick={() => setShowCreate(true)}
              className="px-5 py-2.5 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-xl transition-colors flex items-center gap-2 shadow-sm"
            >
              <Plus className="w-5 h-5" />
              {t('projects.new')}
            </button>
          </div>

          {/* 搜索框 */}
          <div className="mt-6 max-w-md relative">
            <Search className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-400 w-5 h-5" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder={locale === 'zh' ? '搜索项目...' : 'Search projects...'}
              className="w-full pl-12 pr-4 py-3 bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
            />
          </div>
        </div>
      </div>

      {/* 内容区域 */}
      <div className="max-w-6xl mx-auto px-6 py-8">
        {/* 创建模态框 */}
        {showCreate && (
          <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
            <div className="bg-white rounded-2xl p-6 w-full max-w-md shadow-xl">
              <h3 className="text-lg font-semibold text-slate-800 mb-4">{t('projects.create')}</h3>
              <form onSubmit={handleCreate}>
                <div className="mb-4">
                  <label className="block text-sm font-medium text-slate-700 mb-1.5">
                    {t('projects.name')} *
                  </label>
                  <input
                    type="text"
                    value={newProject.name}
                    onChange={(e) => setNewProject({ ...newProject, name: e.target.value })}
                    className="w-full px-4 py-2.5 border border-slate-200 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
                    required
                    autoFocus
                  />
                </div>
                <div className="mb-5">
                  <label className="block text-sm font-medium text-slate-700 mb-1.5">
                    {t('projects.description')}
                  </label>
                  <textarea
                    value={newProject.description}
                    onChange={(e) => setNewProject({ ...newProject, description: e.target.value })}
                    className="w-full px-4 py-2.5 border border-slate-200 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
                    rows={3}
                  />
                </div>
                <div className="flex gap-3 justify-end">
                  <button
                    type="button"
                    onClick={() => setShowCreate(false)}
                    className="px-4 py-2 text-slate-600 hover:bg-slate-100 rounded-lg transition-colors"
                  >
                    {t('projects.cancel')}
                  </button>
                  <button
                    type="submit"
                    className="px-5 py-2 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg transition-colors"
                  >
                    {t('projects.createBtn')}
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}

        {/* 加载状态 */}
        {loading ? (
          <div className="text-center py-20">
            <div className="w-8 h-8 border-2 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto" />
            <p className="mt-3 text-slate-500">{t('common.loading')}</p>
          </div>
        ) : filteredProjects.length === 0 ? (
          /* 空状态 */
          <div className="text-center py-20">
            <div className="w-20 h-20 bg-slate-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <Folder className="w-10 h-10 text-slate-300" />
            </div>
            <h3 className="text-lg font-medium text-slate-700 mb-2">
              {searchQuery
                ? (locale === 'zh' ? '未找到匹配项目' : 'No matching projects')
                : t('projects.empty')}
            </h3>
            <p className="text-slate-500 mb-6">
              {locale === 'zh'
                ? '创建一个新项目开始管理您的文献'
                : 'Create a new project to start managing your literature'}
            </p>
            <button
              onClick={() => setShowCreate(true)}
              className="px-5 py-2.5 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-xl transition-colors inline-flex items-center gap-2"
            >
              <Plus className="w-5 h-5" />
              {locale === 'zh' ? '创建项目' : 'Create Project'}
            </button>
          </div>
        ) : (
          /* 项目列表 */
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
            {filteredProjects.map((project) => (
              <div
                key={project.id}
                className="bg-white rounded-xl border border-slate-200 hover:border-blue-300 hover:shadow-md transition-all cursor-pointer group"
              >
                <div className="p-5">
                  <div className="flex items-start justify-between mb-3">
                    <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-xl flex items-center justify-center">
                      <Folder className="w-6 h-6 text-white" />
                    </div>
                    <button
                      onClick={(e) => handleDelete(project.id, e)}
                      className="p-2 text-slate-300 hover:text-red-500 hover:bg-red-50 rounded-lg transition-colors opacity-0 group-hover:opacity-100"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>

                  <h3 className="font-semibold text-slate-800 mb-1 group-hover:text-blue-600 transition-colors">
                    {project.name}
                  </h3>
                  {project.description && (
                    <p className="text-sm text-slate-500 mb-4 line-clamp-2">{project.description}</p>
                  )}

                  <div className="flex items-center justify-between pt-3 border-t border-slate-100">
                    <div className="flex items-center gap-4 text-sm text-slate-500">
                      <span className="flex items-center gap-1">
                        <FileText className="w-4 h-4" />
                        {project.paper_count} {t('projects.papers')}
                      </span>
                    </div>
                    <ChevronRight className="w-5 h-5 text-slate-300 group-hover:text-blue-500 transition-colors" />
                  </div>
                </div>

                <div className="px-5 py-3 bg-slate-50 rounded-b-xl border-t border-slate-100 flex items-center gap-2 text-xs text-slate-400">
                  <Calendar className="w-3.5 h-3.5" />
                  {new Date(project.created_at).toLocaleDateString()}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
