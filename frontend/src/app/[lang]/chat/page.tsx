'use client';

import { useState, useRef, useEffect } from 'react';
import { Send, BookOpen, User, Bot, Trash2, Info, X, Copy, CheckCircle } from 'lucide-react';
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
  timestamp?: Date;
}

export default function ChatPage() {
  const { t, locale } = useI18n();
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const [copiedIndex, setCopiedIndex] = useState<number | null>(null);

  // Initialize with welcome message
  useEffect(() => {
    setMessages([
      {
        role: 'assistant',
        content: t('chat.welcome'),
        timestamp: new Date()
      }
    ]);
  }, [t]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(scrollToBottom, [messages]);

  const handleSend = async () => {
    if (!input.trim()) return;

    const userMessage: Message = { role: 'user', content: input, timestamp: new Date() };
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
        timestamp: new Date()
      };
      setMessages((prev) => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Chat error:', error);
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: locale === 'zh' ? '抱歉，我遇到了一些问题。' : 'Sorry, I encountered an error.',
          timestamp: new Date()
        }
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
          timestamp: new Date()
        }
      ]);
    }
  };

  const copyToClipboard = async (text: string, index: number) => {
    await navigator.clipboard.writeText(text);
    setCopiedIndex(index);
    setTimeout(() => setCopiedIndex(null), 2000);
  };

  return (
    <div className="h-[calc(100vh-4rem)] bg-slate-50">
      <div className="max-w-4xl mx-auto h-full flex flex-col">
        {/* Header */}
        <div className="bg-white border-b border-slate-200 px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 bg-gradient-to-br from-green-500 to-emerald-600 rounded-xl flex items-center justify-center shadow-md">
                <Bot className="w-6 h-6 text-white" />
              </div>
              <div>
                <h2 className="text-xl font-bold text-slate-800">{t('chat.title')}</h2>
                <p className="text-sm text-slate-500">
                  {locale === 'zh' ? '基于已有文献的智能问答' : 'AI-powered Q&A based on your literature'}
                </p>
              </div>
            </div>
            <button
              onClick={clearChat}
              className="p-2.5 text-slate-400 hover:text-red-500 hover:bg-red-50 rounded-xl transition-colors"
              title={locale === 'zh' ? '清空对话' : 'Clear chat'}
            >
              <Trash2 className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Messages Area */}
        <div className="flex-1 overflow-y-auto px-6 py-4 space-y-4">
          {messages.map((msg, index) => (
            <div
              key={index}
              className={`flex gap-4 animate-fade-in ${msg.role === 'user' ? 'flex-row-reverse' : ''}`}
            >
              {/* Avatar */}
              <div
                className={`w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0 shadow-sm ${
                  msg.role === 'user'
                    ? 'bg-gradient-to-br from-blue-500 to-blue-600'
                    : 'bg-gradient-to-br from-green-500 to-emerald-600'
                }`}
              >
                {msg.role === 'user' ? (
                  <User className="w-5 h-5 text-white" />
                ) : (
                  <Bot className="w-5 h-5 text-white" />
                )}
              </div>

              {/* Message Content */}
              <div
                className={`flex-1 max-w-[80%] ${
                  msg.role === 'user' ? 'text-right' : ''
                }`}
              >
                <div
                  className={`inline-block px-5 py-4 rounded-2xl shadow-sm ${
                    msg.role === 'user'
                      ? 'bg-gradient-to-br from-blue-500 to-blue-600 text-white'
                      : 'bg-white border border-slate-200 text-slate-800'
                  }`}
                >
                  <div className="text-sm leading-relaxed whitespace-pre-wrap">
                    {msg.content}
                  </div>
                  {msg.role === 'assistant' && (
                    <button
                      onClick={() => copyToClipboard(msg.content, index)}
                      className="mt-2 inline-flex items-center gap-1 text-xs text-slate-400 hover:text-slate-600"
                    >
                      {copiedIndex === index ? (
                        <>
                          <CheckCircle className="w-3 h-3" />
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
                  <div className="mt-3 p-4 bg-slate-50 rounded-xl border border-slate-200">
                    <div className="flex items-center gap-2 mb-3 text-sm font-semibold text-slate-700">
                      <Info className="w-4 h-4 text-blue-500" />
                      {locale === 'zh' ? '参考来源' : 'References'}
                      <span className="text-xs text-slate-400">({msg.citations.length})</span>
                    </div>
                    <div className="space-y-2">
                      {msg.citations.map((cite, i) => (
                        <div
                          key={i}
                          className="flex items-start gap-3 text-xs bg-white p-3 rounded-lg border border-slate-100"
                        >
                          <BookOpen className="w-4 h-4 text-slate-400 flex-shrink-0 mt-0.5" />
                          <div className="flex-1 min-w-0">
                            <div className="font-semibold text-slate-800">
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

                {/* Timestamp */}
                <div className={`mt-2 text-xs text-slate-400 ${msg.role === 'user' ? 'text-right' : ''}`}>
                  {msg.timestamp?.toLocaleTimeString(locale === 'zh' ? 'zh-CN' : 'en-US', {
                    hour: '2-digit',
                    minute: '2-digit'
                  })}
                </div>
              </div>
            </div>
          ))}

          {/* Loading State */}
          {loading && (
            <div className="flex gap-4">
              <div className="w-10 h-10 bg-gradient-to-br from-green-500 to-emerald-600 rounded-xl flex items-center justify-center flex-shrink-0">
                <Bot className="w-5 h-5 text-white" />
              </div>
              <div className="bg-white border border-slate-200 px-5 py-4 rounded-2xl">
                <div className="flex gap-1.5">
                  <span className="w-2.5 h-2.5 bg-slate-400 rounded-full animate-bounce"></span>
                  <span className="w-2.5 h-2.5 bg-slate-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></span>
                  <span className="w-2.5 h-2.5 bg-slate-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></span>
                </div>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Input Area */}
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
                className="input pr-14 resize-none"
                rows={2}
                disabled={loading}
              />
              <button
                onClick={handleSend}
                disabled={loading || !input.trim()}
                className="absolute right-3 bottom-3 p-2.5 bg-blue-600 hover:bg-blue-700 disabled:bg-slate-300 text-white rounded-xl transition-colors shadow-md disabled:shadow-none"
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
