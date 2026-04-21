"use client";

interface Props {
  content: string;
}

export default function StreamingMessage({ content }: Props) {
  return (
    <div className="flex justify-start mb-3">
      <div className="max-w-[80%] px-4 py-3 rounded-2xl rounded-bl-md bg-white/[0.05] border border-white/[0.06] text-sm leading-relaxed text-white/90">
        <div className="flex items-center gap-2 mb-1.5">
          <div className="w-5 h-5 rounded-md bg-gradient-to-br from-[#6C63FF] to-[#a78bfa] flex items-center justify-center text-[10px]">
            AI
          </div>
          <span className="text-[11px] text-white/30 font-medium">Omni Copilot</span>
          <span className="ml-1 w-1.5 h-1.5 rounded-full bg-accent animate-pulse-soft" />
        </div>
        {content ? (
          <p className="whitespace-pre-wrap">
            {content}
            <span className="animate-pulse-soft text-accent">▊</span>
          </p>
        ) : (
          <div className="flex items-center gap-1.5 text-white/40 py-1">
            <span className="w-1.5 h-1.5 rounded-full bg-white/30 animate-pulse-soft" />
            <span className="w-1.5 h-1.5 rounded-full bg-white/30 animate-pulse-soft" style={{ animationDelay: "0.2s" }} />
            <span className="w-1.5 h-1.5 rounded-full bg-white/30 animate-pulse-soft" style={{ animationDelay: "0.4s" }} />
          </div>
        )}
      </div>
    </div>
  );
}
