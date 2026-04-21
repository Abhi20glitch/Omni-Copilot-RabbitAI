"use client";

import { useEffect, useState, useRef } from "react";
import { useRouter } from "next/navigation";
import { useChatStore } from "@/lib/store/chatStore";
import { useThemeStore } from "@/lib/store/themeStore";

interface Action {
  id: string;
  label: string;
  icon: string;
  action: () => void;
}

export default function CommandPalette() {
  const [isOpen, setIsOpen] = useState(false);
  const [search, setSearch] = useState("");
  const inputRef = useRef<HTMLInputElement>(null);
  const router = useRouter();
  const { createSession, clearAll } = useChatStore();
  const { setTheme } = useThemeStore();

  const actions: Action[] = [
    {
      id: "new-chat",
      label: "New Chat",
      icon: "💬",
      action: () => {
        createSession();
        router.push("/chat");
      },
    },
    {
      id: "integrations",
      label: "Open Integrations",
      icon: "🔗",
      action: () => router.push("/integrations"),
    },
    {
      id: "memory",
      label: "View Memory",
      icon: "🧠",
      action: () => router.push("/memory"),
    },
    {
      id: "clear-history",
      label: "Clear Chat History",
      icon: "🗑️",
      action: () => clearAll(),
    },
    {
      id: "home",
      label: "Go to Home",
      icon: "🏠",
      action: () => router.push("/"),
    },
    {
      id: "dark",
      label: "Switch to Dark Mode",
      icon: "🌙",
      action: () => setTheme("dark"),
    },
    {
      id: "light",
      label: "Switch to Light Mode",
      icon: "☀️",
      action: () => setTheme("light"),
    },
  ];

  const filtered = actions.filter((a) =>
    a.label.toLowerCase().includes(search.toLowerCase())
  );

  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === "k") {
        e.preventDefault();
        setIsOpen((v) => !v);
        setSearch("");
      }
      if (e.key === "Escape") setIsOpen(false);
    };
    window.addEventListener("keydown", handler);
    return () => window.removeEventListener("keydown", handler);
  }, []);

  useEffect(() => {
    if (isOpen) inputRef.current?.focus();
  }, [isOpen]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-start justify-center pt-[20vh]">
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-black/60 backdrop-blur-sm"
        onClick={() => setIsOpen(false)}
      />

      {/* Modal */}
      <div className="relative w-full max-w-lg bg-[#1e1e1e] border border-white/[0.08] rounded-2xl shadow-2xl shadow-black/40 animate-fade-in overflow-hidden">
        {/* Search Input */}
        <div className="flex items-center gap-3 px-5 py-4 border-b border-white/[0.06]">
          <span className="text-white/30">🔍</span>
          <input
            ref={inputRef}
            id="command-palette-input"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Type a command..."
            className="flex-1 bg-transparent text-sm text-white placeholder:text-white/30 outline-none"
            onKeyDown={(e) => {
              if (e.key === "Enter" && filtered.length > 0) {
                filtered[0].action();
                setIsOpen(false);
              }
            }}
          />
          <kbd className="text-[10px] text-white/20 bg-white/[0.06] px-2 py-1 rounded">
            ESC
          </kbd>
        </div>

        {/* Actions */}
        <div className="max-h-[300px] overflow-y-auto py-2">
          {filtered.map((action) => (
            <button
              key={action.id}
              id={`cmd-${action.id}`}
              onClick={() => {
                action.action();
                setIsOpen(false);
              }}
              className="w-full flex items-center gap-3 px-5 py-3 text-sm text-white/70 hover:text-white hover:bg-white/[0.06] transition-all duration-100"
            >
              <span className="text-base">{action.icon}</span>
              {action.label}
            </button>
          ))}
          {filtered.length === 0 && (
            <p className="px-5 py-4 text-sm text-white/30 text-center">
              No results found
            </p>
          )}
        </div>
      </div>
    </div>
  );
}
