'use client';

import { useState, useRef, useEffect } from 'react';
import { Send, BookOpen, User, Bot } from 'lucide-react';
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
  const { t } = useI18n();
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
        content: data.data?.message?.content || 'No response',
        citations: data.data?.message?.citations,
      };
      setMessages((prev) => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Chat error:', error);
      setMessages((prev) => [
        ...prev,
        { role: 'assistant', content: 'Sorry, I encountered an error.' },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto px-4 py-8 h-[calc(100vh-120px)]">
      <div className="card h-full flex flex-col">
        <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
          <Bot className="w-5 h-5" />
          {t('chat.title')}
        </h2>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto space-y-4 mb-4">
          {messages.map((msg, index) => (
            <div
              key={index}
              className={`flex gap-3 ${msg.role === 'user' ? 'flex-row-reverse' : ''}`}
            >
              <div
                className={`w-8 h-8 rounded-full flex items-center justify-center ${
                  msg.role === 'user' ? 'bg-blue-100' : 'bg-green-100'
                }`}
              >
                {msg.role === 'user' ? (
                  <User className="w-4 h-4 text-blue-600" />
                ) : (
                  <Bot className="w-4 h-4 text-green-600" />
                )}
              </div>
              <div
                className={`flex-1 p-4 rounded-lg ${
                  msg.role === 'user' ? 'bg-blue-50' : 'bg-gray-50'
                }`}
              >
                <p className="text-sm whitespace-pre-wrap">{msg.content}</p>
                {msg.citations && msg.citations.length > 0 && (
                  <div className="mt-3 pt-3 border-t text-xs text-gray-500">
                    <p className="font-medium mb-1">{t('chat.sources')}:</p>
                    {msg.citations.map((cite, i) => (
                      <div key={i} className="flex items-start gap-2 mb-1">
                        <BookOpen className="w-3 h-3 mt-0.5 flex-shrink-0" />
                        <span>
                          {cite.authors}, {cite.year}: {cite.text.slice(0,100)}...
                        </span>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          ))}
          {loading && (
            <div className="flex gap-3">
              <div className="w-8 h-8 rounded-full bg-green-100 flex items-center justify-center">
                <Bot className="w-4 h-4 text-green-600" />
              </div>
              <div className="bg-gray-50 p-4 rounded-lg">
                <div className="flex gap-1">
                  <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" />
                  <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }} />
                  <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }} />
                </div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Input */}
        <div className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && !e.shiftKey && handleSend()}
            placeholder={t('chat.placeholder')}
            className="input flex-1"
            disabled={loading}
          />
          <button
            onClick={handleSend}
            disabled={loading || !input.trim()}
            className="btn btn-primary px-4"
          >
            <Send className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  );
}
