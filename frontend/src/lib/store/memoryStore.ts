import { create } from "zustand";

export interface MemoryEntry {
  id: string;
  key: string;
  value: string;
  createdAt: string;
  updatedAt: string;
}

interface MemoryState {
  memories: MemoryEntry[];
  loading: boolean;
  fetchMemories: () => Promise<void>;
  addMemory: (key: string, value: string) => Promise<void>;
  deleteMemory: (id: string) => Promise<void>;
}

const API = process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000";

export const useMemoryStore = create<MemoryState>((set, get) => ({
  memories: [],
  loading: false,

  fetchMemories: async () => {
    set({ loading: true });
    try {
      const res = await fetch(`${API}/api/memory`);
      const data = await res.json();
      set({ memories: data.memories || [], loading: false });
    } catch {
      set({ loading: false });
    }
  },

  addMemory: async (key, value) => {
    try {
      await fetch(`${API}/api/memory`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ key, value }),
      });
      get().fetchMemories();
    } catch {
      /* handle error */
    }
  },

  deleteMemory: async (id) => {
    try {
      await fetch(`${API}/api/memory/${id}`, { method: "DELETE" });
      get().fetchMemories();
    } catch {
      /* handle error */
    }
  },
}));
