"use client";

import { useState } from "react";
import type { AgentStep } from "@/lib/store/chatStore";

interface Props {
  steps: AgentStep[];
}

const AGENT_COLORS: Record<string, string> = {
  orchestrator: "text-violet-400",
  calendar: "text-blue-400",
  comms: "text-green-400",
  docs: "text-yellow-400",
  code: "text-orange-400",
  browser: "text-cyan-400",
  memory: "text-pink-400",
  general: "text-white/50",
};

export default function AgentTimeline({ steps }: Props) {
  const [expanded, setExpanded] = useState(false);

  if (steps.length === 0) return null;

  return (
    <div className="mb-2 ml-9">
      <button
        onClick={() => setExpanded(!expanded)}
        className="flex items-center gap-2 text-[11px] text-white/30 hover:text-white/50 transition-colors"
      >
        <span className={`transition-transform ${expanded ? "rotate-90" : ""}`}>▶</span>
        {steps.length} agent step{steps.length > 1 ? "s" : ""}
      </button>
      {expanded && (
        <div className="mt-2 ml-2 border-l border-white/[0.08] pl-3 space-y-1.5 animate-fade-in">
          {steps.map((step, i) => (
            <div key={i} className="flex items-start gap-2">
              <div className="w-1.5 h-1.5 rounded-full bg-white/20 mt-1.5 shrink-0" />
              <div>
                <span className={`text-[11px] font-medium ${AGENT_COLORS[step.agent] || "text-white/50"}`}>
                  {step.agent}
                </span>
                <span className="text-[11px] text-white/30 ml-1.5">{step.action}</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
