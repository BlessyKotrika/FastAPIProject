"use client";

import React, { useState, useRef, useEffect } from "react";
import { useAppStore } from "@/lib/store";
import { useTranslation } from "@/lib/i18n";
import { chatService, ChatAskResponse } from "@/services/api";
import Layout from "@/components/Layout";
import { Send, Sparkles, RefreshCw } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import { useRouter } from "next/navigation";

type AdvisoryMode = "llm" | "schemes";

interface Message {
  role: "user" | "bot";
  text: string;
  payload?: ChatAskResponse;
}

export default function AdvisorPage() {
  const { profile, auth, _hasHydrated } = useAppStore();
  const { t } = useTranslation();
  const router = useRouter();

  const welcomeText =
     "Namaste! I can help with Crop Care, Pests, Irrigation, Fertilizer, and Yield. What do you need help with today?";

  const [messages, setMessages] = useState<Message[]>([
    { role: "bot", text: welcomeText },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  // IMPORTANT: no localStorage persistence => new session each load
  const [conversationId, setConversationId] = useState<string | null>(null);

  // Mode selector
  const [mode, setMode] = useState<AdvisoryMode>("llm");

  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!_hasHydrated) return;
    if (!auth.isAuthenticated) {
      router.push("/login");
      return;
    }
    // Force fresh session on page load
    setConversationId(null);
    setMessages([{ role: "bot", text: welcomeText }]);
  }, [_hasHydrated, auth.isAuthenticated, router]);

  useEffect(() => {
    scrollRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  const startNewChat = () => {
    setConversationId(null);
    setMessages([
      {
        role: "bot",
        text:
          mode === "schemes"
            ? "You are now in Schemes & Policies mode. Ask about eligibility, documents, and application links."
            : welcomeText,
      },
    ]);
    setInput("");
  };

  const onModeChange = (nextMode: AdvisoryMode) => {
    setMode(nextMode);
    // Start clean chat when mode changes
    setConversationId(null);
    setMessages([
      {
        role: "bot",
        text:
          nextMode === "schemes"
            ? "Schemes & Policies mode enabled. Please ask your scheme question with state/crop details."
            : welcomeText,
      },
    ]);
  };

  const handleSend = async () => {
    if (!input.trim() || loading) return;

    const userMsg = input.trim();
    setInput("");
    setMessages((prev) => [...prev, { role: "user", text: userMsg }]);
    setLoading(true);

    try {
      const res = await chatService.ask({
        question: userMsg,
        language: profile.language,
        crop: profile.crop || undefined,
        location: profile.location || undefined,
        conversation_id: conversationId || undefined,
        advisory_mode: mode, // NEW
      });

      if (res.conversation_id && res.conversation_id !== conversationId) {
        setConversationId(res.conversation_id);
      }

      setMessages((prev) => [
        ...prev,
        {
          role: "bot",
          text: res.answer || "Sorry, I could not generate a response.",
          payload: res,
        },
      ]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        { role: "bot", text: t("advisor.connectionError") },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const renderBotStructuredContent = (payload?: ChatAskResponse) => {
    if (!payload) return null;

    return (
      <div className="mt-3 space-y-3">
        <div className="flex items-center gap-2 text-[10px] font-bold uppercase tracking-wider">
          <span className="px-2 py-0.5 rounded-full bg-slate-100 text-slate-600">
            {payload.message_type}
          </span>
          <span className="px-2 py-0.5 rounded-full bg-emerald-50 text-emerald-700">
            Confidence: {Math.round((payload.confidence_score || 0) * 100)}%
          </span>
        </div>

        {payload.checklist?.length > 0 && (
          <div>
            <p className="text-xs font-bold text-slate-700 mb-1">Checklist</p>
            <ul className="list-disc pl-4 text-xs text-slate-700 space-y-0.5">
              {payload.checklist.map((item, idx) => (
                <li key={`check-${idx}`}>{item}</li>
              ))}
            </ul>
          </div>
        )}

        {payload.do?.length > 0 && (
          <div>
            <p className="text-xs font-bold text-emerald-700 mb-1">Do</p>
            <ul className="list-disc pl-4 text-xs text-slate-700 space-y-0.5">
              {payload.do.map((item, idx) => (
                <li key={`do-${idx}`}>{item}</li>
              ))}
            </ul>
          </div>
        )}

        {payload.dont?.length > 0 && (
          <div>
            <p className="text-xs font-bold text-rose-700 mb-1">Don’t</p>
            <ul className="list-disc pl-4 text-xs text-slate-700 space-y-0.5">
              {payload.dont.map((item, idx) => (
                <li key={`dont-${idx}`}>{item}</li>
              ))}
            </ul>
          </div>
        )}

        {payload.schemes?.length > 0 && (
          <div>
            <p className="text-xs font-bold text-slate-700 mb-2">Schemes</p>
            <div className="space-y-2">
              {payload.schemes.map((s, idx) => (
                <div
                  key={`scheme-${idx}`}
                  className="rounded-xl border border-slate-200 p-2 bg-slate-50"
                >
                  <p className="text-xs font-bold text-slate-800">{s.name}</p>
                  <p className="text-xs text-slate-600 mt-1">{s.description}</p>
                  {s.documents?.length > 0 && (
                    <p className="text-[11px] text-slate-600 mt-1">
                      <span className="font-semibold">Documents:</span>{" "}
                      {s.documents.join(", ")}
                    </p>
                  )}
                  {s.link && (
                    <a
                      href={s.link}
                      target="_blank"
                      rel="noreferrer"
                      className="inline-block mt-1 text-[11px] font-semibold text-primary-600 underline"
                    >
                      Apply / Details
                    </a>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {payload.citations?.length > 0 && (
          <div>
            <p className="text-xs font-bold text-slate-700 mb-1">Sources</p>
            <ul className="list-disc pl-4 text-[11px] text-slate-600 space-y-0.5 break-all">
              {payload.citations.map((c, idx) => (
                <li key={`cit-${idx}`}>{c}</li>
              ))}
            </ul>
          </div>
        )}
      </div>
    );
  };

  return (
    <Layout>
      <div className="flex flex-col h-[calc(100vh-140px)]">
        {/* Header */}
        <div className="p-4 bg-white/50 backdrop-blur-md border-b border-slate-100 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="bg-primary-600 p-2 rounded-xl text-white shadow-lg shadow-primary-200">
              <Sparkles className="w-5 h-5" />
            </div>
            <div>
              <h2 className="font-bold text-slate-900 leading-tight">{t("advisor.title")}</h2>
              <p className="text-[10px] text-emerald-600 font-bold uppercase tracking-widest">
                AI ONLINE
              </p>
            </div>
          </div>

          <button
            onClick={startNewChat}
            className="inline-flex items-center gap-1 text-xs px-3 py-1.5 rounded-lg border border-slate-200 bg-white hover:bg-slate-50"
          >
            <RefreshCw size={14} />
            New Chat
          </button>
        </div>

        {/* Mode Selector */}
        <div className="px-4 py-2 bg-white border-b border-slate-100 flex gap-2">
          <button
            onClick={() => onModeChange("llm")}
            className={`px-3 py-1.5 rounded-full text-xs font-semibold ${
              mode === "llm"
                ? "bg-primary-600 text-white"
                : "bg-slate-100 text-slate-700"
            }`}
          >
            Farming Advisor
          </button>
          <button
            onClick={() => onModeChange("schemes")}
            className={`px-3 py-1.5 rounded-full text-xs font-semibold ${
              mode === "schemes"
                ? "bg-primary-600 text-white"
                : "bg-slate-100 text-slate-700"
            }`}
          >
            Schemes and Policies
          </button>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-4 space-y-6 bg-slate-50/50">
          <AnimatePresence>
            {messages.map((msg, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, y: 10, scale: 0.98 }}
                animate={{ opacity: 1, y: 0, scale: 1 }}
                className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
              >
                <div className={`max-w-[90%] ${msg.role === "user" ? "text-right" : ""}`}>
                  <div
                    className={`p-4 rounded-2xl text-sm font-medium leading-relaxed shadow-sm ${
                      msg.role === "user"
                        ? "bg-primary-600 text-white rounded-tr-none"
                        : "bg-white text-slate-800 border border-slate-100 rounded-tl-none"
                    }`}
                  >
                    <div>{msg.text}</div>
                    {msg.role === "bot" && renderBotStructuredContent(msg.payload)}
                    {msg.role === "bot" && (
                      <div className="mt-2 pt-2 border-t border-slate-100 flex justify-end">
                        <p className="text-[8px] font-bold text-slate-400 uppercase tracking-widest">
                          KHETIPULSE AI
                        </p>
                      </div>
                    )}
                  </div>
                </div>
              </motion.div>
            ))}
          </AnimatePresence>

          {loading && (
            <div className="flex justify-start">
              <div className="bg-white border border-slate-100 p-4 rounded-2xl rounded-tl-none shadow-sm">
                <div className="flex gap-1">
                  <div className="w-1.5 h-1.5 bg-primary-400 rounded-full animate-pulse"></div>
                  <div className="w-1.5 h-1.5 bg-primary-400 rounded-full animate-pulse"></div>
                  <div className="w-1.5 h-1.5 bg-primary-400 rounded-full animate-pulse"></div>
                </div>
              </div>
            </div>
          )}

          <div ref={scrollRef} />
        </div>

        {/* Input */}
        <div className="p-4 bg-white/80 backdrop-blur-lg border-t border-slate-100">
          <div className="flex gap-2 bg-slate-100 p-2 rounded-2xl border border-slate-200 focus-within:border-primary-300 focus-within:bg-white transition-all">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleSend()}
              placeholder={
                mode === "schemes"
                  ? "Ask about eligibility, documents, application links..."
                  : t("advisor.placeholder")
              }
              className="flex-1 bg-transparent px-3 text-sm font-semibold text-slate-800 placeholder:text-slate-400 focus:outline-none"
            />
            <button
              onClick={handleSend}
              disabled={loading || !input.trim()}
              className="bg-primary-600 text-white p-2.5 rounded-xl disabled:opacity-50"
            >
              <Send size={18} />
            </button>
          </div>
        </div>
      </div>
    </Layout>
  );
}