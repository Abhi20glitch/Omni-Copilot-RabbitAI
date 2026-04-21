"use client";

import { useState } from "react";

interface Props {
  integration: {
    id: string;
    name: string;
    icon: string;
    category: string;
    connected: boolean;
  };
  onConnect: (id: string) => Promise<{ oauth_url?: string; message?: string; status: string } | void>;
  onDisconnect: (id: string) => void;
}

export default function IntegrationCard({ integration, onConnect, onDisconnect }: Props) {
  const { id, name, icon, connected } = integration;
  const [loading, setLoading] = useState(false);
  const [feedback, setFeedback] = useState<string | null>(null);

  const handleConnect = async () => {
    setLoading(true);
    setFeedback(null);
    try {
      const result = await onConnect(id);
      if (result?.oauth_url) {
        // Will redirect — nothing else to do
        return;
      }
      if (result?.status === "error") {
        setFeedback(result.message || "OAuth credentials not configured.");
      }
      // demo mode or success — feedback clears after 3s
      if (result?.message) {
        setFeedback(result.message);
        setTimeout(() => setFeedback(null), 3000);
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="group p-5 rounded-xl bg-white/[0.03] border border-white/[0.06] hover:border-white/[0.12] hover:bg-white/[0.05] transition-all duration-300">
      <div className="flex items-start justify-between mb-4">
        <div className="w-12 h-12 rounded-xl bg-white/[0.06] flex items-center justify-center text-2xl group-hover:scale-110 transition-transform duration-300">
          {icon}
        </div>
        <span
          className={`px-2.5 py-1 rounded-full text-[10px] font-medium ${
            connected
              ? "bg-emerald-500/15 text-emerald-400"
              : "bg-white/[0.06] text-white/30"
          }`}
        >
          {connected ? "Connected" : "Not connected"}
        </span>
      </div>

      <h3 className="text-sm font-semibold mb-1">{name}</h3>
      <p className="text-[12px] text-white/30 mb-3 leading-relaxed">
        {connected
          ? `${name} is connected and ready to use.`
          : `Connect ${name} to enable AI-powered automation.`}
      </p>

      {/* Feedback message */}
      {feedback && (
        <p
          className={`text-[11px] mb-3 px-2.5 py-1.5 rounded-lg leading-snug ${
            feedback.includes("not configured") || feedback.includes("error")
              ? "bg-amber-500/10 text-amber-400 border border-amber-500/20"
              : "bg-emerald-500/10 text-emerald-400 border border-emerald-500/20"
          }`}
        >
          {feedback.includes("not configured") || feedback.includes("GOOGLE_CLIENT_ID")
            ? `⚠️ OAuth credentials not set. Add ${name} credentials to backend .env to enable real OAuth.`
            : feedback.includes("demo mode")
            ? `✓ Connected in demo mode`
            : feedback}
        </p>
      )}

      <button
        id={`integration-${id}-btn`}
        onClick={() => (connected ? onDisconnect(id) : handleConnect())}
        disabled={loading}
        className={`w-full py-2.5 rounded-lg text-xs font-medium transition-all duration-200 active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed ${
          connected
            ? "bg-white/[0.06] text-white/50 hover:bg-red-500/15 hover:text-red-400"
            : "bg-accent/15 text-accent hover:bg-accent/25"
        }`}
      >
        {loading ? (
          <span className="animate-pulse">Connecting…</span>
        ) : connected ? (
          "Disconnect"
        ) : (
          "Connect"
        )}
      </button>
    </div>
  );
}
