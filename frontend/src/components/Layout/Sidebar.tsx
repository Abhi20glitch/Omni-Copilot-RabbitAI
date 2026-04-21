"use client";

import React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useChatStore } from "@/lib/store/chatStore";

export default function Sidebar() {
  const pathname = usePathname();
  const { sessions, activeSessionId, setActiveSession, createSession, deleteSession } =
    useChatStore();

  const navItems = [
    { href: "/chat", label: "Chat", icon: "💬" },
    { href: "/integrations", label: "Integrations", icon: "🔗" },
    { href: "/memory", label: "Memory", icon: "🧠" },
  ];

  return (
    <aside className="w-[260px] min-w-[260px] h-screen bg-[#191919] border-r border-white/[0.06] flex flex-col">
      {/* Logo */}
      <div className="px-4 py-5 flex items-center gap-3 border-b border-white/[0.06]">
        <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-[#6C63FF] to-[#a78bfa] flex items-center justify-center text-sm font-bold">
          O
        </div>
        <h1 className="text-[15px] font-semibold tracking-tight">Omni Copilot</h1>
      </div>

      {/* New Chat Button */}
      <div className="px-3 pt-4 pb-2">
        <button
          id="new-chat-btn"
          onClick={() => {
            createSession();
            if (pathname !== "/chat") window.location.href = "/chat";
          }}
          className="w-full px-3 py-2.5 rounded-lg bg-accent/10 hover:bg-accent/20 text-accent text-sm font-medium transition-all duration-200 flex items-center gap-2"
        >
          <span className="text-lg">+</span>
          New Chat
        </button>
      </div>

      {/* Navigation */}
      <nav className="px-3 pt-2 pb-3 space-y-0.5">
        {navItems.map((item) => {
          const isActive = pathname === item.href;
          return (
            <Link
              key={item.href}
              href={item.href}
              className={`flex items-center gap-3 px-3 py-2 rounded-lg text-sm transition-all duration-150 ${
                isActive
                  ? "bg-white/[0.08] text-white"
                  : "text-white/50 hover:text-white/80 hover:bg-white/[0.04]"
              }`}
            >
              <span className="text-base">{item.icon}</span>
              {item.label}
            </Link>
          );
        })}
      </nav>

      {/* Divider */}
      <div className="px-4">
        <div className="border-t border-white/[0.06]" />
      </div>

      {/* Recent Chats */}
      <div className="flex-1 overflow-y-auto px-3 pt-3">
        <p className="px-3 pb-2 text-[11px] font-medium text-white/30 uppercase tracking-wider">
          Recent
        </p>
        {sessions.length === 0 && (
          <p className="px-3 text-xs text-white/20">No conversations yet</p>
        )}
        {sessions.slice(0, 20).map((s) => (
          <button
            key={s.id}
            onClick={() => {
              setActiveSession(s.id);
              if (pathname !== "/chat") window.location.href = "/chat";
            }}
            className={`group w-full text-left flex items-center justify-between px-3 py-2 rounded-lg text-sm transition-all duration-150 mb-0.5 ${
              activeSessionId === s.id
                ? "bg-white/[0.08] text-white"
                : "text-white/40 hover:text-white/70 hover:bg-white/[0.04]"
            }`}
          >
            <span className="truncate flex-1">{s.title}</span>
            <span
              onClick={(e) => {
                e.stopPropagation();
                deleteSession(s.id);
              }}
              className="opacity-0 group-hover:opacity-100 text-white/30 hover:text-red-400 transition-opacity ml-2 text-xs"
            >
              ✕
            </span>
          </button>
        ))}
      </div>

      {/* Bottom */}
      <div className="px-4 py-3 border-t border-white/[0.06]">
        <p className="text-[11px] text-white/20 text-center">
          ⌘K to open command palette
        </p>
      </div>
    </aside>
  );
}
