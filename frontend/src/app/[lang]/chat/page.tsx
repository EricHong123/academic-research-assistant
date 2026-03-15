'use client';

import { useState, useRef, useEffect } from 'react';
import { Send, BookOpen, User, Bot, Trash2, Sparkles, Copy, Check, X } from 'lucide-react';
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
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const [copiedIndex, setCopiedIndex] = useState<number | null>(null);

  useEffect(() => {
    setMessages([
      { role: 'assistant', content: t('chat.welcome') }
    ]);
  }, [t]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

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
        body: JSON.stringify({ project_id: 'default', message: input }),
      });
      const data = await response.json();
      const assistantMessage: Message = {
        role: 'assistant',
        content: data.data?.message?.content || (locale === 'zh' ? '抱歉，我遇到了一些问题。' : 'Sorry, I encountered an error.'),
        citations: data.data?.message?.citations,
      };
      setMessages((prev) => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Chat error:', error);
      setMessages((prev) => [
        ...prev,
        { role: 'assistant', content: locale === 'zh' ? '抱歉，我遇到了一些问题。' : 'Sorry, I encountered an error.' }
      ]);
    } finally {
      setLoading(false);
    }
  };

  const clearChat = () => {
    if (confirm(locale === 'zh' ? '确定清空对话？' : 'Clear all messages?')) {
      setMessages([{ role: 'assistant', content: t('chat.welcome') }]);
    }
  };

  const copyToClipboard = async (text: string, index: number) => {
    await navigator.clipboard.writeText(text);
    setCopiedIndex(index);
    setTimeout(() => setCopiedIndex(null), 2000);
  };

  return (
    <div className="h-screen pt-16 bg-[#0a0a0f] flex flex-col">
      {/* Header */}
      <div className="border-b border-white/5 bg-[#0a0a0f]/80 backdrop-blur-xl">
        <div className="max-w-4xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="relative">
                <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-green-500 to-emerald-600 flex items-center justify-center">
                  <Bot className="w-6 h-6 text-white" />
                </div>
                <div className="absolute -bottom-1 -right-1 w-4 h-4 bg-green-500 rounded-full border-2 border-[#0a0a0f]" />
              </div>
              <div>
                <h2 className="text-lg font-semibold text-white flex items-center gap-2">
                  {t('chat.title')}
                  <span className="badge bg-green-500/20 text-green-400">AI</span>
                </h2>
                <p className="text-sm text-white/40">
                  {locale === 'zh' ? '基于已有文献的智能问答' : 'AI-powered Q&A based on your literature'}
                </p>
              </div>
            </div>
            <button
              onClick={clearChat}
              className="p-2.5 text-white/40 hover:text-red-400 hover:bg-red-400/10 rounded-xl transition-all"
              title={locale === 'zh' ? '清空对话' : 'Clear chat'}
            >
              <Trash2 className="w-5 h-5" />
            </button>
          </div>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-6 py-4 space-y-4">
        {messages.map((msg, index) => (
          <div
            key={index}
            className={`flex gap-4 animate-fade-in ${msg.role === 'user' ? 'flex-row-reverse' : ''}`}
          >
            {/* Avatar */}
            <div className={`w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0 ${
              msg.role === 'user'
                ? 'bg-gradient-to-br from-blue-500 to-indigo-600'
                : 'bg-gradient-to-br from-green-500 to-emerald-600'
            }`}>
              {msg.role === 'user' ? (
                <User className="w-5 h-5 text-white" />
              ) : (
                <Bot className="w-5 h-5 text-white" />
              )}
            </div>

            {/* Content */}
            <div className={`flex-1 max-w-[75%] ${msg.role === 'user' ? 'text-right' : ''}`}>
              <div className={`inline-block px-5 py-4 rounded-2xl ${
                msg.role === 'user'
                  ? 'bg-gradient-to-br from-blue-500 to-indigo-600 text-white'
                  : 'glass-card text-white'
              }`}>
                <div className="text-sm leading-relaxed whitespace-pre-wrap">{msg.content}</div>
                {msg.role === 'assistant' && (
                  <button
                    onClick={() => copyToClipboard(msg.content, index)}
                    className="mt-2 inline-flex items-center gap-1 text-xs text-white/40 hover:text-white"
                  >
                    {copiedIndex === index ? (
                      <>
                        <Check className="w-3 h-3" />
                        {locale === 'zh' ? '已复制' : 'Copied'}
                      </>
                    ) : (
                      <>
                        <Copy className="w-3 h-3" />
                        {locale === 'zh' ? '复制' : 'Copy'}
                      </>
                    )}
                  </button>
                )}
              </div>

              {/* Citations */}
              {msg.citations && msg.citations.length > 0 && (
                <div className="mt-3 p-4 glass-card rounded-xl">
                  <div className="flex items-center gap-2 mb-3 text-sm font-medium text-white/70">
                    <BookOpen className="w-4 h-4 text-indigo-400" />
                    {locale === 'zh' ? '参考来源' : 'References'}
                    <span className="text-xs text-white/30">({msg.citations.length})</span>
                  </div>
                  <div className="space-y-2">
                    {msg.citations.map((cite, i) => (
                      <div key={i} className="flex items-start gap-3 text-xs bg-white/5 p-3 rounded-lg">
                        <BookOpen className="w-4 h-4 text-white/30 flex-shrink-0 mt-0.5" />
                        <div>
                          <div className="font-medium text-white/70">
                            {cite.authors}, {cite.year}
                          </div>
                          <div className="text-white/40 mt-1 line-clamp-2">{cite.text}</div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        ))}

        {/* Loading */}
        {loading && (
          <div className="flex gap-4">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-green-500 to-emerald-600 flex items-center justify-center">
              <Bot className="w-5 h-5 text-white" />
            </div>
            <div className="glass-card px-5 py-4 rounded-2xl">
              <div className="flex gap-1.5">
                <span className="w-2.5 h-2.5 bg-white/30 rounded-full animate-bounce" style={{ animationDelay: '0s' }} />
                <span className="w-2.5 h-2.5 bg-white/30 rounded-full animate-bounce" style={{ animationDelay: '0.15s' }} />
                <span className="w-2.5 h-2.5 bg-white/30 rounded-full animate-bounce" style={{ animationDelay: '0.3s' }} />
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="border-t border-white/5 bg-[#0a0a0f]/80 backdrop-blur-xl p-4">
        <div className="max-w-3xl mx-auto">
          <div className="relative flex items-center gap-2 p-2 pr-3 bg-[#12121a] border border-white/10 rounded-2xl">
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
              className="flex-1 px-4 py-3 bg-transparent text-white placeholder:text-white/30 text-sm outline-none resize-none"
              rows={1}
              disabled={loading}
            />
            <button
              onClick={handleSend}
              disabled={loading || !input.trim()}
              className="p-3 bg-gradient-to-r from-indigo-500 to-purple-500 rounded-xl text-white hover:opacity-90 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <Send className="w-5 h-5" />
            </button>
          </div>
          <p className="text-xs text-white/30 mt-2 text-center">
            {locale === 'zh' ? '按 Enter 发送，Shift + Enter 换行' : 'Press Enter to send, Shift + Enter for new line'}
          </p>
        </div>
      </div>
    </div>
  );
}
