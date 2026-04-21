"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useThemeStore } from "@/lib/store/themeStore";
import { useChatStore } from "@/lib/store/chatStore";

export default function Home() {
  const router = useRouter();
  const { loadFromStorage } = useThemeStore();
  const { loadFromStorage: loadChats } = useChatStore();

  useEffect(() => {
    loadFromStorage();
    loadChats();
  }, [loadFromStorage, loadChats]);

  return (
    <main className="min-h-screen bg-[#111111] flex flex-col items-center justify-center px-6 relative overflow-hidden">
      {/* Background gradient orbs */}
      <div className="absolute top-1/4 -left-40 w-96 h-96 bg-[#6C63FF]/10 rounded-full blur-[120px]" />
      <div className="absolute bottom-1/4 -right-40 w-96 h-96 bg-[#a78bfa]/10 rounded-full blur-[120px]" />

      {/* Content */}
      <div className="relative z-10 text-center max-w-2xl animate-fade-in">
        {/* Logo */}
        <div className="w-20 h-20 rounded-2xl bg-gradient-to-br from-[#6C63FF] to-[#a78bfa] flex items-center justify-center text-3xl mx-auto mb-8 shadow-2xl shadow-accent/30">
          🤖
        </div>

        <h1 className="text-5xl font-bold mb-4 tracking-tight">
          <span className="text-gradient">Omni Copilot</span>
        </h1>
        <p className="text-lg text-white/40 mb-10 leading-relaxed">
          Your universal AI workspace. Orchestrate Gmail, Calendar, GitHub,
          Notion, Slack, and more — all from a single chat interface.
        </p>

        {/* CTA Buttons */}
        <div className="flex items-center justify-center gap-4 mb-12">
          <button
            id="get-started-btn"
            onClick={() => router.push("/chat")}
            className="px-8 py-3.5 rounded-xl bg-accent hover:bg-accent-hover text-white text-sm font-semibold transition-all duration-200 shadow-lg shadow-accent/25 hover:shadow-xl hover:shadow-accent/35 active:scale-95"
          >
            Get Started →
          </button>
          <button
            onClick={() => router.push("/integrations")}
            className="px-8 py-3.5 rounded-xl bg-white/[0.06] hover:bg-white/[0.1] text-white/70 text-sm font-medium transition-all duration-200 border border-white/[0.08] active:scale-95"
          >
            View Integrations
          </button>
        </div>

        {/* Feature chips */}
        <div className="flex flex-wrap justify-center gap-3">
          {[
            "📧 Gmail",
            "📅 Calendar",
            "🐙 GitHub",
            "📝 Notion",
            "💬 Slack",
            "💾 Drive",
            "🎮 Discord",
            "📱 WhatsApp",
          ].map((chip) => (
            <span
              key={chip}
              className="px-3 py-1.5 rounded-lg bg-white/[0.04] border border-white/[0.06] text-xs text-white/40"
            >
              {chip}
            </span>
          ))}
        </div>
      </div>

      {/* Footer */}
      <footer className="absolute bottom-6 text-center">
        <p className="text-[11px] text-white/15">
          Press <kbd className="px-1.5 py-0.5 bg-white/[0.06] rounded text-[10px]">⌘K</kbd> to open command palette
        </p>
      </footer>
    </main>
  );
}
