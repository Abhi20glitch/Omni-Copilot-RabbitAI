"use client";

import { useState } from "react";
import { useActionStore } from "@/lib/store/actionStore";

const AGENT_ICONS: Record<string, string> = {
  orchestrator: "🎯",
  calendar: "📅",
  comms: "📧",
  docs: "📄",
  code: "💻",
  browser: "🌐",
  memory: "🧠",
  general: "🤖",
};

export default function ActionHistory() {
  const [isOpen, setIsOpen] = useState(false);
  const { actions, clearActions } = useActionStore();

  return (
    <>
      {/* Toggle Button */}
      <button
        id="action-history-toggle"
        onClick={() => setIsOpen(!isOpen)}
        className="fixed bottom-6 right-6 w-12 h-12 rounded-full bg-[#1e1e1e] border border-white/[0.08] flex items-center justify-center text-lg shadow-lg hover:bg-[#252525] transition-all z-40"
        title="Action History"
      >
        {actions.length > 0 ? (
          <span className="relative">
            📜
            <span className="absolute -top-1 -right-1 w-4 h-4 rounded-full bg-accent text-[9px] flex items-center justify-center text-white font-bold">
              {actions.length > 9 ? "9+" : actions.length}
            </span>
          </span>
        ) : (
          "📜"
        )}
      </button>

      {/* Drawer */}
      {isOpen && (
        <div className="fixed inset-y-0 right-0 w-[380px] bg-[#1a1a1a] border-l border-white/[0.06] shadow-2xl z-50 animate-slide-in-right flex flex-col">
          {/* Header */}
          <div className="flex items-center justify-between px-5 py-4 border-b border-white/[0.06]">
            <h2 className="text-sm font-semibold">Action History</h2>
            <div className="flex items-center gap-2">
              {actions.length > 0 && (
                <button
                  onClick={clearActions}
                  className="text-[11px] text-white/30 hover:text-red-400 transition-colors px-2 py-1 rounded hover:bg-red-500/10"
                >
                  Clear
                </button>
              )}
              <button
                onClick={() => setIsOpen(false)}
                className="text-white/30 hover:text-white/60 text-lg transition-colors"
              >
                ✕
              </button>
            </div>
          </div>

          {/* Content */}
          <div className="flex-1 overflow-y-auto p-4">
            {actions.length === 0 ? (
              <div className="flex flex-col items-center justify-center h-full text-white/20">
                <span className="text-4xl mb-3">📋</span>
                <p className="text-sm">No actions yet</p>
                <p className="text-xs mt-1">AI agent actions will appear here</p>
              </div>
            ) : (
              <div className="space-y-2">
                {actions.map((action) => (
                  <div
                    key={action.id}
                    className="p-3 rounded-lg bg-white/[0.03] border border-white/[0.04] group"
                  >
                    <div className="flex items-start gap-2">
                      <span className="text-base mt-0.5 shrink-0">
                        {AGENT_ICONS[action.agent] || "🤖"}
                      </span>
                      <div className="flex-1 min-w-0">
                        <p className="text-sm text-white/80 leading-snug">{action.label}</p>
                        {action.details && (
                          <p className="text-[11px] text-white/30 mt-0.5 truncate">{action.details}</p>
                        )}
                        <div className="flex items-center gap-2 mt-1">
                          <span className="text-[11px] text-accent/60 capitalize">{action.agent}</span>
                          <span className="text-[11px] text-white/20">·</span>
                          <span className="text-[11px] text-white/20">
                            {new Date(action.timestamp).toLocaleTimeString([], {
                              hour: "2-digit",
                              minute: "2-digit",
                            })}
                          </span>
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}
    </>
  );
}
