import { create } from "zustand";

export interface AgentStep {
  agent: string;
  action: string;
}

export interface Message {
  id: string;
  role: "user" | "assistant" | "system";
  content: string;
  agentSteps?: AgentStep[];
  plan?: Record<string, unknown> | null;
  timestamp: number;
}

export interface ChatSession {
  id: string;
  title: string;
  messages: Message[];
  createdAt: number;
  updatedAt: number;
}

interface ChatState {
  sessions: ChatSession[];
  activeSessionId: string | null;
  isStreaming: boolean;

  createSession: () => string;
  setActiveSession: (id: string) => void;
  addMessage: (msg: Message) => void;
  updateLastAssistantMessage: (content: string) => void;
  setAgentSteps: (messageId: string, steps: AgentStep[]) => void;
  setStreaming: (v: boolean) => void;
  deleteSession: (id: string) => void;
  clearAll: () => void;
  loadFromStorage: () => void;
  persist: () => void;
}

const generateId = () => Math.random().toString(36).slice(2, 10);

export const useChatStore = create<ChatState>((set, get) => ({
  sessions: [],
  activeSessionId: null,
  isStreaming: false,

  createSession: () => {
    const id = generateId();
    const session: ChatSession = {
      id,
      title: "New Chat",
      messages: [],
      createdAt: Date.now(),
      updatedAt: Date.now(),
    };
    set((s) => ({
      sessions: [session, ...s.sessions],
      activeSessionId: id,
    }));
    get().persist();
    return id;
  },

  setActiveSession: (id) => set({ activeSessionId: id }),

  addMessage: (msg) => {
    set((s) => {
      const sessions = s.sessions.map((sess) => {
        if (sess.id !== s.activeSessionId) return sess;
        const updated = {
          ...sess,
          messages: [...sess.messages, msg],
          updatedAt: Date.now(),
          title:
            sess.messages.length === 0 && msg.role === "user"
              ? msg.content.slice(0, 40) + (msg.content.length > 40 ? "…" : "")
              : sess.title,
        };
        return updated;
      });
      return { sessions };
    });
    get().persist();
  },

  updateLastAssistantMessage: (content) => {
    set((s) => {
      const sessions = s.sessions.map((sess) => {
        if (sess.id !== s.activeSessionId) return sess;
        const msgs = [...sess.messages];
        const lastIdx = msgs.length - 1;
        if (lastIdx >= 0 && msgs[lastIdx].role === "assistant") {
          msgs[lastIdx] = { ...msgs[lastIdx], content };
        }
        return { ...sess, messages: msgs, updatedAt: Date.now() };
      });
      return { sessions };
    });
  },

  setAgentSteps: (messageId, steps) => {
    set((s) => {
      const sessions = s.sessions.map((sess) => {
        if (sess.id !== s.activeSessionId) return sess;
        const msgs = sess.messages.map((m) =>
          m.id === messageId ? { ...m, agentSteps: steps } : m
        );
        return { ...sess, messages: msgs };
      });
      return { sessions };
    });
  },

  setStreaming: (v) => set({ isStreaming: v }),

  deleteSession: (id) => {
    set((s) => ({
      sessions: s.sessions.filter((sess) => sess.id !== id),
      activeSessionId: s.activeSessionId === id ? null : s.activeSessionId,
    }));
    get().persist();
  },

  clearAll: () => {
    set({ sessions: [], activeSessionId: null });
    if (typeof window !== "undefined") localStorage.removeItem("omni-chats");
  },

  loadFromStorage: () => {
    if (typeof window === "undefined") return;
    try {
      const raw = localStorage.getItem("omni-chats");
      if (raw) {
        const sessions = JSON.parse(raw) as ChatSession[];
        set({ sessions });
      }
    } catch {
      /* ignore corrupt data */
    }
  },

  persist: () => {
    if (typeof window === "undefined") return;
    const { sessions } = get();
    localStorage.setItem("omni-chats", JSON.stringify(sessions));
  },
}));
