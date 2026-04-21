import { create } from "zustand";

export interface Integration {
  id: string;
  name: string;
  icon: string;
  category: string;
  connected: boolean;
}

interface ConnectResult {
  status: string;
  oauth_url?: string;
  message?: string;
}

interface IntegrationState {
  integrations: Integration[];
  loading: boolean;
  fetchIntegrations: () => Promise<void>;
  connectTool: (toolId: string) => Promise<ConnectResult | void>;
  disconnectTool: (toolId: string) => Promise<void>;
}

const API = process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000";

export const useIntegrationStore = create<IntegrationState>((set, get) => ({
  integrations: [],
  loading: false,

  fetchIntegrations: async () => {
    set({ loading: true });
    try {
      const res = await fetch(`${API}/api/integrations`);
      const data = await res.json();
      set({ integrations: data.integrations || [], loading: false });
    } catch {
      set({ loading: false });
    }
  },

  connectTool: async (toolId): Promise<ConnectResult | void> => {
    try {
      const res = await fetch(`${API}/api/integrations/${toolId}/connect`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({}),
      });
      const data: ConnectResult = await res.json();

      if (data.oauth_url) {
        window.location.href = data.oauth_url;
        return data;
      }

      // Re-fetch to update status (handles demo mode)
      await get().fetchIntegrations();
      return data;
    } catch (_err) {
      return { status: "error", message: "Could not reach backend." };
    }
  },

  disconnectTool: async (toolId) => {
    try {
      await fetch(`${API}/api/integrations/${toolId}/disconnect`, {
        method: "POST",
      });
      get().fetchIntegrations();
    } catch {
      /* ignore */
    }
  },
}));
