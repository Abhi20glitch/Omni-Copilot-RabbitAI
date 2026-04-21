import { create } from "zustand";

export interface ActionItem {
  id: string;
  label: string;
  agent: string;
  timestamp: number;
  undoable: boolean;
  details?: string;
}

interface ActionState {
  actions: ActionItem[];
  addAction: (action: Omit<ActionItem, "id" | "timestamp">) => void;
  clearActions: () => void;
}

const generateId = () => Math.random().toString(36).slice(2, 10);

export const useActionStore = create<ActionState>((set) => ({
  actions: [],

  addAction: (action) => {
    set((s) => ({
      actions: [
        { ...action, id: generateId(), timestamp: Date.now() },
        ...s.actions,
      ].slice(0, 50), // keep last 50
    }));
  },

  clearActions: () => set({ actions: [] }),
}));
