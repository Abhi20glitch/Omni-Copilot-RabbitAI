"use client";

import { useEffect } from "react";
import Sidebar from "@/components/Layout/Sidebar";
import CommandPalette from "@/components/Layout/CommandPalette";
import IntegrationCard from "@/components/Integrations/IntegrationCard";
import { useIntegrationStore } from "@/lib/store/integrationStore";

const FALLBACK_INTEGRATIONS = [
  { id: "gmail", name: "Gmail", icon: "📧", category: "google", connected: false },
  { id: "gcal", name: "Google Calendar", icon: "📅", category: "google", connected: false },
  { id: "gmeet", name: "Google Meet", icon: "📹", category: "google", connected: false },
  { id: "gforms", name: "Google Forms", icon: "📋", category: "google", connected: false },
  { id: "gsheets", name: "Google Sheets", icon: "📊", category: "google", connected: false },
  { id: "drive", name: "Google Drive", icon: "💾", category: "google", connected: false },
  { id: "slack", name: "Slack", icon: "💬", category: "messaging", connected: false },
  { id: "discord", name: "Discord", icon: "🎮", category: "messaging", connected: false },
  { id: "notion", name: "Notion", icon: "📝", category: "productivity", connected: false },
  { id: "github", name: "GitHub", icon: "🐙", category: "developer", connected: false },
  { id: "whatsapp", name: "WhatsApp", icon: "📱", category: "messaging", connected: false },
];

export default function IntegrationsPage() {
  const { integrations, fetchIntegrations, connectTool, disconnectTool } =
    useIntegrationStore();

  useEffect(() => {
    fetchIntegrations();
  }, [fetchIntegrations]);

  const displayIntegrations = integrations.length > 0 ? integrations : FALLBACK_INTEGRATIONS;

  return (
    <div className="flex h-screen w-full bg-[#111111] overflow-hidden">
      <Sidebar />
      <main className="flex-1 overflow-y-auto">
        <div className="max-w-5xl mx-auto px-8 py-10">
          {/* Header */}
          <div className="mb-8">
            <h1 className="text-2xl font-bold mb-2">
              <span className="text-gradient">Integrations Hub</span>
            </h1>
            <p className="text-sm text-white/40">
              Connect your tools to unlock AI-powered automation across your workflow.
            </p>
          </div>

          {/* Grid */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {displayIntegrations.map((integration) => (
              <IntegrationCard
                key={integration.id}
                integration={integration}
                onConnect={(id) => connectTool(id)}
                onDisconnect={disconnectTool}
              />
            ))}
          </div>
        </div>
      </main>
      <CommandPalette />
    </div>
  );
}
