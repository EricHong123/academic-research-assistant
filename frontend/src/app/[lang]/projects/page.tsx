'use client';

import { useState, useEffect } from 'react';
import { Plus, Folder, FileText, Trash2, Search, Calendar, ChevronRight, X, Sparkles, Brain } from 'lucide-react';
import { useI18n } from '@/lib/i18n';

interface Project {
  id: string;
  name: string;
  description?: string;
  paper_count: number;
  created_at: string;
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
    <div className="min-h-screen pt-16 bg-[#0a0a0f]">
      {/* Header */}
      <div className="relative overflow-hidden border-b border-white/5">
        <div className="absolute inset-0 grid-bg opacity-30" />
        <div className="absolute top-0 right-0 w-[400px] h-[400px] bg-indigo-500/10 rounded-full blur-[100px]" />
        <div className="relative max-w-6xl mx-auto px-6 py-12">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div>
              <h1 className="text-3xl font-bold text-white mb-2">{t('projects.title')}</h1>
              <p className="text-white/40">
                {locale === 'zh' ? '管理您的文献收藏和研究项目' : 'Manage your literature collections and projects'}
              </p>
            </div>
            <button
              onClick={() => setShowCreate(true)}
              className="btn-primary"
            >
              <Plus className="w-5 h-5" />
              {t('projects.new')}
            </button>
          </div>

          {/* Search */}
          <div className="mt-6 max-w-md relative">
            <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-white/30" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder={locale === 'zh' ? '搜索项目...' : 'Search projects...'}
              className="input pl-12"
            />
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-6xl mx-auto px-6 py-8">
        {/* Create Modal */}
        {showCreate && (
          <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50 p-4">
            <div className="w-full max-w-md bg-[#12121a] border border-white/10 rounded-2xl animate-fade-in">
              <div className="flex items-center justify-between p-6 border-b border-white/5">
                <h3 className="text-lg font-semibold text-white flex items-center gap-2">
                  <Sparkles className="w-5 h-5 text-indigo-400" />
                  {t('projects.create')}
                </h3>
                <button
                  onClick={() => setShowCreate(false)}
                  className="p-2 text-white/40 hover:text-white hover:bg-white/5 rounded-lg transition-all"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>
              <form onSubmit={handleCreate} className="p-6">
                <div className="mb-5">
                  <label className="block text-sm text-white/60 mb-2">{t('projects.name')} *</label>
                  <input
                    type="text"
                    value={newProject.name}
                    onChange={(e) => setNewProject({ ...newProject, name: e.target.value })}
                    className="input"
                    placeholder={locale === 'zh' ? '输入项目名称' : 'Enter project name'}
                    required
                    autoFocus
                  />
                </div>
                <div className="mb-6">
                  <label className="block text-sm text-white/60 mb-2">{t('projects.description')}</label>
                  <textarea
                    value={newProject.description}
                    onChange={(e) => setNewProject({ ...newProject, description: e.target.value })}
                    className="input resize-none"
                    rows={3}
                    placeholder={locale === 'zh' ? '输入项目描述（可选）' : 'Enter description (optional)'}
                  />
                </div>
                <div className="flex gap-3 justify-end">
                  <button type="button" onClick={() => setShowCreate(false)} className="btn-secondary">
                    {t('projects.cancel')}
                  </button>
                  <button type="submit" className="btn-primary">
                    {t('projects.createBtn')}
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}

        {/* Loading */}
        {loading ? (
          <div className="flex flex-col items-center justify-center py-20">
            <div className="w-10 h-10 border-2 border-white/10 border-t-indigo-500 rounded-full animate-spin mb-4" />
            <p className="text-white/40">{t('common.loading')}</p>
          </div>
        ) : filteredProjects.length === 0 ? (
          /* Empty */
          <div className="text-center py-20">
            <div className="w-20 h-20 mx-auto mb-6 rounded-2xl bg-gradient-to-br from-indigo-500/10 to-purple-500/10 flex items-center justify-center">
              <Folder className="w-10 h-10 text-indigo-400/50" />
            </div>
            <h3 className="text-xl font-semibold text-white mb-2">
              {searchQuery ? (locale === 'zh' ? '未找到匹配项目' : 'No matching projects') : t('projects.empty')}
            </h3>
            <p className="text-white/40 mb-6">
              {locale === 'zh' ? '创建一个新项目开始管理您的文献' : 'Create a new project to start managing your literature'}
            </p>
            <button onClick={() => setShowCreate(true)} className="btn-primary inline-flex">
              <Plus className="w-5 h-5" />
              {locale === 'zh' ? '创建项目' : 'Create Project'}
            </button>
          </div>
        ) : (
          /* Grid */
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {filteredProjects.map((project, index) => (
              <div
                key={project.id}
                className="glass-card group p-5 cursor-pointer animate-slide-up"
                style={{ animationDelay: `${index * 0.05}s` }}
              >
                <div className="flex items-start justify-between mb-4">
                  <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-indigo-500 to-purple-500 flex items-center justify-center shadow-lg">
                    <Folder className="w-6 h-6 text-white" />
                  </div>
                  <button
                    onClick={(e) => handleDelete(project.id, e)}
                    className="p-2 text-white/20 hover:text-red-400 hover:bg-red-400/10 rounded-lg transition-all opacity-0 group-hover:opacity-100"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>

                <h3 className="font-semibold text-white mb-2 group-hover:text-indigo-400 transition-colors">
                  {project.name}
                </h3>
                {project.description && (
                  <p className="text-sm text-white/40 mb-4 line-clamp-2">{project.description}</p>
                )}

                <div className="flex items-center justify-between pt-3 border-t border-white/5">
                  <div className="flex items-center gap-2 text-sm text-white/40">
                    <FileText className="w-4 h-4" />
                    <span>{project.paper_count} {t('projects.papers')}</span>
                  </div>
                  <ChevronRight className="w-5 h-5 text-white/20 group-hover:text-indigo-400 transition-colors" />
                </div>

                <div className="mt-3 flex items-center gap-2 text-xs text-white/30">
                  <Calendar className="w-3.5 h-3.5" />
                  {new Date(project.created_at).toLocaleDateString(locale === 'zh' ? 'zh-CN' : 'en-US')}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
