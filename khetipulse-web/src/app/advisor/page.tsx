"use client";
import React, { useState, useRef, useEffect } from 'react';
import { useAppStore } from '@/lib/store';
import { useTranslation } from '@/lib/i18n';
import { chatService } from '@/services/api';
import Layout from '@/components/Layout';
import { MessageSquare, Send, Bot, User, Loader2, Sparkles } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

interface Message {
  role: 'user' | 'bot';
  text: string;
}

export default function AdvisorPage() {
  const { profile } = useAppStore();
  const { t } = useTranslation();
  const [messages, setMessages] = useState<Message[]>([
    { role: 'bot', text: t('advisor.welcome') }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    scrollRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim() || loading) return;

    const userMsg = input.trim();
    setInput('');
    setMessages(prev => [...prev, { role: 'user', text: userMsg }]);
    setLoading(true);

    try {
      const res = await chatService.ask({
        question: userMsg,
        language: profile.language,
        crop: profile.crop,
        location: profile.location,
      });
      
      setMessages(prev => [...prev, { 
        role: 'bot', 
        text: res.answer || t('advisor.connectionError') 
      }]);
    } catch (err) {
      setMessages(prev => [...prev, { role: 'bot', text: t('advisor.connectionError') }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Layout>
      <div className="flex flex-col h-[calc(100vh-140px)]">
        {/* Chat Header */}
        <div className="p-4 bg-white/50 backdrop-blur-md border-b border-slate-100 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="bg-primary-600 p-2 rounded-xl text-white shadow-lg shadow-primary-200">
              <Sparkles className="w-5 h-5" />
            </div>
            <div>
              <h2 className="font-bold text-slate-900 leading-tight">{t('advisor.title')}</h2>
              <div className="flex items-center gap-1.5 mt-0.5">
                <span className="w-2 h-2 bg-emerald-500 rounded-full animate-pulse"></span>
                <p className="text-[10px] text-emerald-600 font-bold uppercase tracking-widest">
                  {t('advisor.aiOnline')}
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-4 space-y-6 scrollbar-hide bg-slate-50/50">
          <AnimatePresence>
            {messages.map((msg, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, y: 10, scale: 0.98 }}
                animate={{ opacity: 1, y: 0, scale: 1 }}
                className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div className={`max-w-[85%] flex gap-2 ${msg.role === 'user' ? 'flex-row-reverse' : ''}`}>
                  <div className={`p-4 rounded-2xl text-sm font-medium leading-relaxed shadow-sm ${
                    msg.role === 'user' 
                      ? 'bg-primary-600 text-white rounded-tr-none' 
                      : 'bg-white text-slate-800 border border-slate-100 rounded-tl-none'
                  }`}>
                    {msg.text}
                    {msg.role === 'bot' && (
                      <div className="mt-2 pt-2 border-t border-slate-50 flex justify-end">
                        <p className="text-[8px] font-bold text-slate-400 uppercase tracking-widest">{t('advisor.aiLabel')}</p>
                      </div>
                    )}
                  </div>
                </div>
              </motion.div>
            ))}
          </AnimatePresence>
          {loading && (
            <motion.div 
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="flex justify-start"
            >
              <div className="bg-white/50 border border-slate-100 p-4 rounded-2xl rounded-tl-none shadow-sm">
                <div className="flex gap-1">
                  <motion.div animate={{ opacity: [0.3, 1, 0.3] }} transition={{ repeat: Infinity, duration: 1 }} className="w-1.5 h-1.5 bg-primary-400 rounded-full"></motion.div>
                  <motion.div animate={{ opacity: [0.3, 1, 0.3] }} transition={{ repeat: Infinity, duration: 1, delay: 0.2 }} className="w-1.5 h-1.5 bg-primary-400 rounded-full"></motion.div>
                  <motion.div animate={{ opacity: [0.3, 1, 0.3] }} transition={{ repeat: Infinity, duration: 1, delay: 0.4 }} className="w-1.5 h-1.5 bg-primary-400 rounded-full"></motion.div>
                </div>
              </div>
            </motion.div>
          )}
          <div ref={scrollRef} />
        </div>

        {/* Input Area */}
        <div className="p-4 bg-white/80 backdrop-blur-lg border-t border-slate-100">
          <div className="flex gap-2 bg-slate-100 p-2 rounded-2xl border border-slate-200 focus-within:border-primary-300 focus-within:bg-white transition-all">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleSend()}
              placeholder={t('advisor.placeholder')}
              className="flex-1 bg-transparent px-3 text-sm font-semibold text-slate-800 placeholder:text-slate-400 focus:outline-none"
            />
            <button
              onClick={handleSend}
              disabled={loading}
              className="bg-primary-600 text-white p-2.5 rounded-xl disabled:opacity-50 shadow-md shadow-primary-100 active:scale-90 transition-transform"
            >
              <Send size={18} className="stroke-[2.5px]" />
            </button>
          </div>
        </div>
      </div>
    </Layout>
  );
}
