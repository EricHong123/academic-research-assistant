'use client';

import { useState, useRef, useEffect } from 'react';
import { Send, BookOpen, User, Bot, Copy, RefreshCw, Trash2, Info } from 'lucide-react';
import { useI18n } from '@/lib/i18n';

interface Message {
  role: 'user' | 'assistant';
  content: string;
  citations?: Array<{
    paper_id: string;
    authors: string;
    year: number;
    text: string;
  }>;
}

export default function ChatPage() {
  const { t, locale } = useI18n();
  const [messages, setMessages] = useState<Message[]>([
    {
      role: 'assistant',
      content: t('chat.welcome'),
    },
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(scrollToBottom, [messages]);

  const handleSend = async () => {
    if (!input.trim()) return;

    const userMessage: Message = { role: 'user', content: input };
    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          project_id: 'default',
          message: input,
        }),
      });

      const data = await response.json();
      const assistantMessage: Message = {
        role: 'assistant',
        content: data.data?.message?.content || locale === 'zh' ? '抱歉，我遇到了一些问题。' : 'Sorry, I encountered an error.',
        citations: data.data?.message?.citations,
      };
      setMessages((prev) => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Chat error:', error);
      setMessages((prev) => [
        ...prev,
        { role: 'assistant', content: locale === 'zh' ? '抱歉，我遇到了一些问题。' : 'Sorry, I encountered an error.' },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const clearChat = () => {
    if (confirm(locale === 'zh' ? '确定清空对话？' : 'Clear all messages?')) {
      setMessages([
        {
          role: 'assistant',
          content: t('chat.welcome'),
        },
      ]);
    }
  };

  return (
    <div className="h-[calc(100vh-4rem)] bg-slate-50">
      <div className="max-w-4xl mx-auto h-full flex flex-col">
        {/* 标题栏 */}
        <div className="bg-white border-b border-slate-200 px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-gradient-to-br from-green-500 to-emerald-600 rounded-xl flex items-center justify-center">
                <Bot className="w-5 h-5 text-white" />
              </div>
              <div>
                <h2 className="text-lg font-semibold text-slate-800">{t('chat.title')}</h2>
                <p className="text-sm text-slate-500">
                  {locale === 'zh' ? '基于已有文献的智能问答' : 'AI-powered Q&A based on your literature'}
                </p>
              </div>
            </div>
            <button
              onClick={clearChat}
              className="p-2 text-slate-400 hover:text-red-500 hover:bg-red-50 rounded-lg transition-colors"
              title={locale === 'zh' ? '清空对话' : 'Clear chat'}
            >
              <Trash2 className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* 消息区域 */}
        <div className="flex-1 overflow-y-auto px-6 py-4 space-y-4">
          {messages.map((msg, index) => (
            <div
              key={index}
              className={`flex gap-4 ${msg.role === 'user' ? 'flex-row-reverse' : ''}`}
            >
              {/* 头像 */}
              <div
                className={`w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0 ${
                  msg.role === 'user'
                    ? 'bg-blue-600'
                    : 'bg-gradient-to-br from-green-500 to-emerald-600'
                }`}
              >
                {msg.role === 'user' ? (
                  <User className="w-5 h-5 text-white" />
                ) : (
                  <Bot className="w-5 h-5 text-white" />
                )}
              </div>

              {/* 消息内容 */}
              <div
                className={`flex-1 max-w-[80%] ${
                  msg.role === 'user' ? 'text-right' : ''
                }`}
              >
                <div
                  className={`inline-block px-5 py-4 rounded-2xl ${
                    msg.role === 'user'
                      ? 'bg-blue-600 text-white'
                      : 'bg-white border border-slate-200 text-slate-800'
                  }`}
                >
                  <div className="text-sm leading-relaxed whitespace-pre-wrap">
                    {msg.content}
                  </div>
                </div>

                {/* 引用来源 */}
                {msg.citations && msg.citations.length > 0 && (
                  <div className="mt-3 p-4 bg-slate-100 rounded-xl">
                    <div className="flex items-center gap-2 mb-3 text-sm font-medium text-slate-700">
                      <Info className="w-4 h-4" />
                      {t('chat.sources')} ({msg.citations.length})
                    </div>
                    <div className="space-y-2">
                      {msg.citations.map((cite, i) => (
                        <div
                          key={i}
                          className="flex items-start gap-2 text-xs text-slate-600 bg-white p-3 rounded-lg"
                        >
                          <BookOpen className="w-4 h-4 text-slate-400 flex-shrink-0 mt-0.5" />
                          <div>
                            <div className="font-medium text-slate-800">
                              {cite.authors}, {cite.year}
                            </div>
                            <div className="text-slate-500 mt-1 line-clamp-2">
                              {cite.text}
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* 时间 */}
                <div className={`mt-2 text-xs text-slate-400 ${msg.role === 'user' ? 'text-right' : ''}`}>
                  {new Date().toLocaleTimeString()}
                </div>
              </div>
            </div>
          ))}

          {/* 加载状态 */}
          {loading && (
            <div className="flex gap-4">
              <div className="w-10 h-10 bg-gradient-to-br from-green-500 to-emerald-600 rounded-xl flex items-center justify-center">
                <Bot className="w-5 h-5 text-white" />
              </div>
              <div className="bg-white border border-slate-200 px-5 py-4 rounded-2xl">
                <div className="flex gap-1">
                  <span className="w-2 h-2 bg-slate-400 rounded-full animate-bounce" />
                  <span className="w-2 h-2 bg-slate-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }} />
                  <span className="w-2 h-2 bg-slate-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }} />
                </div>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* 输入区域 */}
        <div className="bg-white border-t border-slate-200 px-6 py-4">
          <div className="max-w-3xl mx-auto">
            <div className="relative">
              <textarea
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    handleSend();
                  }
                }}
                placeholder={t('chat.placeholder')}
                className="w-full px-5 py-4 pr-14 bg-slate-50 border border-slate-200 rounded-xl resize-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
                rows={2}
                disabled={loading}
              />
              <button
                onClick={handleSend}
                disabled={loading || !input.trim()}
                className="absolute right-3 bottom-3 p-2 bg-blue-600 hover:bg-blue-700 disabled:bg-slate-300 text-white rounded-lg transition-colors"
              >
                <Send className="w-5 h-5" />
              </button>
            </div>
            <p className="text-xs text-slate-400 mt-2 text-center">
              {locale === 'zh'
                ? '按 Enter 发送，Shift + Enter 换行'
                : 'Press Enter to send, Shift + Enter for new line'}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
