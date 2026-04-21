"use client";

import { useEffect } from "react";
import Sidebar from "@/components/Layout/Sidebar";
import ChatWindow from "@/components/Chat/ChatWindow";
import CommandPalette from "@/components/Layout/CommandPalette";
import ActionHistory from "@/components/Layout/ActionHistory";
import { useChatStore } from "@/lib/store/chatStore";

export default function ChatPage() {
  const { loadFromStorage, sessions, createSession } = useChatStore();

  useEffect(() => {
    loadFromStorage();
  }, [loadFromStorage]);

  useEffect(() => {
    if (sessions.length === 0) {
      createSession();
    }
  }, [sessions.length, createSession]);

  return (
    <div className="flex h-screen w-full bg-[#111111] overflow-hidden">
      <Sidebar />
      <main className="flex-1 flex flex-col min-w-0">
        <ChatWindow />
      </main>
      <CommandPalette />
      <ActionHistory />
    </div>
  );
}
