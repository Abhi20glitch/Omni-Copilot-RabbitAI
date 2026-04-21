"use client";

import { useState } from "react";

interface Props {
  plan: Record<string, unknown>;
  onAccept?: () => void;
  onDecline?: () => void;
}

export default function PlanCard({ plan, onAccept, onDecline }: Props) {
  const [status, setStatus] = useState<"pending" | "accepted" | "declined">("pending");

  if (!plan) return null;

  const handleAccept = () => {
    setStatus("accepted");
    onAccept?.();
  };

  const handleDecline = () => {
    setStatus("declined");
    onDecline?.();
  };

  return (
    <div className="mb-3 ml-9 p-4 rounded-xl bg-accent/[0.08] border border-accent/20 animate-slide-up">
      <div className="flex items-center gap-2 mb-3">
        <span className="text-base">📋</span>
        <h3 className="text-sm font-semibold text-accent">Action Plan</h3>
        {status !== "pending" && (
          <span
            className={`ml-auto text-[11px] px-2 py-0.5 rounded-full font-medium ${
              status === "accepted"
                ? "bg-emerald-500/15 text-emerald-400"
                : "bg-red-500/15 text-red-400"
            }`}
          >
            {status === "accepted" ? "✓ Accepted" : "✕ Declined"}
          </span>
        )}
      </div>
      <pre className="text-xs text-white/60 bg-black/20 rounded-lg p-3 mb-3 overflow-x-auto">
        {JSON.stringify(plan, null, 2)}
      </pre>
      {status === "pending" && (
        <div className="flex gap-2">
          <button
            onClick={handleAccept}
            className="px-4 py-2 rounded-lg bg-accent hover:bg-accent-hover text-white text-xs font-medium transition-all active:scale-95"
          >
            ✓ Accept
          </button>
          <button
            onClick={handleDecline}
            className="px-4 py-2 rounded-lg bg-white/[0.06] hover:bg-white/[0.1] text-white/60 text-xs font-medium transition-all active:scale-95"
          >
            ✕ Decline
          </button>
        </div>
      )}
    </div>
  );
}
