"use client";

import React, { useState, useRef, useEffect } from "react";
import { useChatStore } from "@/lib/store/chatStore";
import MessageBubble from "./MessageBubble";
import StreamingMessage from "./StreamingMessage";
import AgentTimeline from "./AgentTimeline";
import PlanCard from "./PlanCard";
import type { AgentStep, Message } from "@/lib/store/chatStore";
import { useActionStore } from "@/lib/store/actionStore";

const API = process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000";

export default function ChatWindow() {
  const [input, setInput] = useState("");
  const [streamContent, setStreamContent] = useState("");
  const [streamSteps, setStreamSteps] = useState<AgentStep[]>([]);
  const [streamPlan, setStreamPlan] = useState<Record<string, unknown> | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const {
    sessions,
    activeSessionId,
    isStreaming,
    addMessage,
    setStreaming,
    createSession,
  } = useChatStore();

  const { addAction } = useActionStore();

  const activeSession = sessions.find((s) => s.id === activeSessionId);
  const messages = activeSession?.messages ?? [];

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, streamContent]);

  const handleSend = async () => {
    const msg = input.trim();
    if (!msg || isStreaming) return;

    // Create session if none active
    let sessionId = activeSessionId;
    if (!sessionId) {
      sessionId = createSession();
    }

    // Add user message
    const userMsg: Message = {
      id: Math.random().toString(36).slice(2),
      role: "user",
      content: msg,
      timestamp: Date.now(),
    };
    addMessage(userMsg);
    setInput("");
    setStreaming(true);
    setStreamContent("");
    setStreamSteps([]);
    setStreamPlan(null);

    try {
      const res = await fetch(`${API}/api/chat/stream`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message: msg,
          user_id: "anonymous",
          history: messages.map((m) => ({ role: m.role, content: m.content })),
        }),
      });

      if (!res.body) throw new Error("No response body");

      const reader = res.body.getReader();
      const decoder = new TextDecoder();
      let fullContent = "";
      const steps: AgentStep[] = [];

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value, { stream: true });
        const lines = chunk.split("\n");

        for (const line of lines) {
          if (!line.startsWith("data: ")) continue;
          const payload = line.slice(6).trim();
          if (payload === "[DONE]") break;

          try {
            const data = JSON.parse(payload);
            if (data.type === "token") {
              fullContent += data.content;
              setStreamContent(fullContent);
            } else if (data.type === "step") {
              steps.push({ agent: data.agent, action: data.action });
              setStreamSteps([...steps]);
              addAction({
                label: data.action,
                agent: data.agent,
                undoable: false,
              });
            } else if (data.type === "done" && data.plan) {
              setStreamPlan(data.plan);
            } else if (data.type === "error") {
              fullContent += `⚠️ Error: ${data.content}`;
              setStreamContent(fullContent);
            }
          } catch {
            /* skip malformed JSON */
          }
        }
      }

      // Add assistant message to store
      const assistantMsg: Message = {
        id: Math.random().toString(36).slice(2),
        role: "assistant",
        content: fullContent,
        agentSteps: steps,
        plan: streamPlan,
        timestamp: Date.now(),
      };
      addMessage(assistantMsg);
    } catch {
      const errorMsg: Message = {
        id: Math.random().toString(36).slice(2),
        role: "assistant",
        content: "⚠️ Failed to connect to the backend. Is the server running on port 8000?",
        timestamp: Date.now(),
      };
      addMessage(errorMsg);
    } finally {
      setStreaming(false);
      setStreamContent("");
      setStreamSteps([]);
    }
  };

  return (
    <div className="flex flex-col h-full">
      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto px-6 py-6">
        {messages.length === 0 && !isStreaming && (
          <div className="flex flex-col items-center justify-center h-full animate-fade-in">
            <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-[#6C63FF] to-[#a78bfa] flex items-center justify-center text-2xl mb-5 shadow-lg shadow-accent/20">
              🤖
            </div>
            <h2 className="text-xl font-semibold mb-2">Welcome to Omni Copilot</h2>
            <p className="text-sm text-white/40 max-w-md text-center leading-relaxed">
              Your universal AI workspace. Ask me to check your calendar, read emails,
              search Notion, manage GitHub issues, or anything else.
            </p>
            <div className="flex flex-wrap gap-2 mt-6 max-w-lg justify-center">
              {[
                "📅 What's on my calendar today?",
                "📧 Summarize my unread emails",
                "📝 Search Notion for meeting notes",
                "🐙 Show open GitHub issues",
              ].map((suggestion) => (
                <button
                  key={suggestion}
                  onClick={() => setInput(suggestion.slice(2).trim())}
                  className="px-3 py-2 rounded-lg bg-white/[0.04] border border-white/[0.06] text-xs text-white/50 hover:text-white/80 hover:bg-white/[0.08] transition-all duration-200"
                >
                  {suggestion}
                </button>
              ))}
            </div>
          </div>
        )}

        <div className="max-w-3xl mx-auto space-y-1">
          {messages.map((msg) => (
            <div key={msg.id}>
              {msg.agentSteps && msg.agentSteps.length > 0 && (
                <AgentTimeline steps={msg.agentSteps} />
              )}
              {msg.plan && <PlanCard plan={msg.plan} />}
              <MessageBubble message={msg} />
            </div>
          ))}

          {/* Streaming state */}
          {isStreaming && (
            <div className="animate-fade-in">
              {streamSteps.length > 0 && <AgentTimeline steps={streamSteps} />}
              <StreamingMessage content={streamContent} />
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Input Area */}
      <div className="border-t border-white/[0.06] px-6 py-4 bg-[#151515]">
        <div className="max-w-3xl mx-auto flex items-center gap-3">
          <div className="flex-1 relative">
            <input
              id="chat-input"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && !e.shiftKey && handleSend()}
              placeholder="Ask Omni Copilot anything..."
              disabled={isStreaming}
              className="w-full px-4 py-3 rounded-xl bg-white/[0.05] border border-white/[0.08] text-sm text-white placeholder:text-white/25 outline-none focus:border-accent/50 focus:bg-white/[0.07] transition-all duration-200 disabled:opacity-50"
            />
          </div>
          <button
            id="send-btn"
            onClick={handleSend}
            disabled={!input.trim() || isStreaming}
            className="px-5 py-3 rounded-xl bg-accent hover:bg-accent-hover text-white text-sm font-medium transition-all duration-200 disabled:opacity-30 disabled:cursor-not-allowed hover:shadow-lg hover:shadow-accent/20 active:scale-95"
          >
            {isStreaming ? (
              <span className="animate-pulse-soft">●●●</span>
            ) : (
              "Send"
            )}
          </button>
        </div>
      </div>
    </div>
  );
}
