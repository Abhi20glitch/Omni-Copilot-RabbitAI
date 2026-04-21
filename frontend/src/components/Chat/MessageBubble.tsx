"use client";

import type { Message } from "@/lib/store/chatStore";

interface Props {
  message: Message;
}

/** Minimal markdown renderer — handles code blocks, bold, inline code, and line breaks */
function renderMarkdown(text: string) {
  const lines = text.split("\n");
  const elements: React.ReactNode[] = [];
  let i = 0;

  while (i < lines.length) {
    const line = lines[i];

    // Fenced code block
    if (line.startsWith("```")) {
      const lang = line.slice(3).trim();
      const codeLines: string[] = [];
      i++;
      while (i < lines.length && !lines[i].startsWith("```")) {
        codeLines.push(lines[i]);
        i++;
      }
      elements.push(
        <pre
          key={i}
          className="my-2 p-3 rounded-lg bg-black/30 border border-white/[0.06] overflow-x-auto text-[12px] font-mono text-white/80"
        >
          {lang && (
            <span className="block text-[10px] text-accent/60 mb-1 font-sans">{lang}</span>
          )}
          {codeLines.join("\n")}
        </pre>
      );
      i++;
      continue;
    }

    // Heading
    if (line.startsWith("### ")) {
      elements.push(<p key={i} className="font-semibold text-white/90 mt-2 mb-0.5">{inlineFormat(line.slice(4))}</p>);
    } else if (line.startsWith("## ")) {
      elements.push(<p key={i} className="font-bold text-white mt-2 mb-1">{inlineFormat(line.slice(3))}</p>);
    } else if (line.startsWith("# ")) {
      elements.push(<p key={i} className="font-bold text-white text-base mt-2 mb-1">{inlineFormat(line.slice(2))}</p>);
    }
    // Bullet list
    else if (line.match(/^[-*•]\s/)) {
      elements.push(
        <div key={i} className="flex gap-2 my-0.5">
          <span className="text-accent/60 shrink-0 mt-0.5">•</span>
          <span>{inlineFormat(line.slice(2))}</span>
        </div>
      );
    }
    // Numbered list
    else if (line.match(/^\d+\.\s/)) {
      const match = line.match(/^(\d+)\.\s(.*)$/);
      if (match) {
        elements.push(
          <div key={i} className="flex gap-2 my-0.5">
            <span className="text-accent/60 shrink-0 font-mono text-[11px] mt-0.5">{match[1]}.</span>
            <span>{inlineFormat(match[2])}</span>
          </div>
        );
      }
    }
    // Empty line → spacer
    else if (line.trim() === "") {
      elements.push(<div key={i} className="h-1.5" />);
    }
    // Normal paragraph
    else {
      elements.push(<p key={i} className="leading-relaxed">{inlineFormat(line)}</p>);
    }

    i++;
  }

  return elements;
}

function inlineFormat(text: string): React.ReactNode {
  // Split on **bold**, *italic*, and `code`
  const parts = text.split(/(\*\*[^*]+\*\*|\*[^*]+\*|`[^`]+`)/g);
  return parts.map((part, idx) => {
    if (part.startsWith("**") && part.endsWith("**")) {
      return <strong key={idx} className="font-semibold text-white">{part.slice(2, -2)}</strong>;
    }
    if (part.startsWith("*") && part.endsWith("*")) {
      return <em key={idx} className="italic text-white/80">{part.slice(1, -1)}</em>;
    }
    if (part.startsWith("`") && part.endsWith("`")) {
      return (
        <code key={idx} className="px-1.5 py-0.5 rounded bg-black/30 font-mono text-[11px] text-accent/80 border border-white/[0.06]">
          {part.slice(1, -1)}
        </code>
      );
    }
    return part;
  });
}

export default function MessageBubble({ message }: Props) {
  const isUser = message.role === "user";

  return (
    <div
      className={`flex ${isUser ? "justify-end" : "justify-start"} mb-3 animate-slide-up`}
    >
      <div
        className={`max-w-[80%] px-4 py-3 rounded-2xl text-sm leading-relaxed ${
          isUser
            ? "bg-accent text-white rounded-br-md"
            : "bg-white/[0.05] text-white/90 border border-white/[0.06] rounded-bl-md"
        }`}
      >
        {!isUser && (
          <div className="flex items-center gap-2 mb-1.5">
            <div className="w-5 h-5 rounded-md bg-gradient-to-br from-[#6C63FF] to-[#a78bfa] flex items-center justify-center text-[10px]">
              AI
            </div>
            <span className="text-[11px] text-white/30 font-medium">Omni Copilot</span>
          </div>
        )}
        {isUser ? (
          <p className="whitespace-pre-wrap">{message.content}</p>
        ) : (
          <div className="space-y-0.5">{renderMarkdown(message.content)}</div>
        )}
        <span className="block text-[10px] mt-2 opacity-30">
          {new Date(message.timestamp).toLocaleTimeString([], {
            hour: "2-digit",
            minute: "2-digit",
          })}
        </span>
      </div>
    </div>
  );
}
