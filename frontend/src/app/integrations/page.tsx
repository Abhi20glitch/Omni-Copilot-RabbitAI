"use client";

import { useEffect, useState, Suspense } from "react";
import { useSearchParams } from "next/navigation";
import Sidebar from "@/components/Layout/Sidebar";
import CommandPalette from "@/components/Layout/CommandPalette";
import IntegrationCard from "@/components/Integrations/IntegrationCard";
import { useIntegrationStore } from "@/lib/store/integrationStore";

const FALLBACK_INTEGRATIONS = [
  { id: "gmail",    name: "Gmail",            icon: "📧", category: "google",       connected: false },
  { id: "gcal",     name: "Google Calendar",  icon: "📅", category: "google",       connected: false },
  { id: "gmeet",    name: "Google Meet",      icon: "📹", category: "google",       connected: false },
  { id: "gforms",   name: "Google Forms",     icon: "📋", category: "google",       connected: false },
  { id: "gsheets",  name: "Google Sheets",    icon: "📊", category: "google",       connected: false },
  { id: "drive",    name: "Google Drive",     icon: "💾", category: "google",       connected: false },
  { id: "discord",  name: "Discord",          icon: "🎮", category: "messaging",    connected: false },
  { id: "notion",   name: "Notion",           icon: "📝", category: "productivity", connected: false },
  { id: "github",   name: "GitHub",           icon: "🐙", category: "developer",    connected: false },
  { id: "whatsapp", name: "WhatsApp",         icon: "📱", category: "messaging",    connected: false },
];

function IntegrationsContent() {
  const { integrations, fetchIntegrations, connectTool, disconnectTool } = useIntegrationStore();
  const searchParams = useSearchParams();
  const [banner, setBanner] = useState<{ type: "success" | "error"; message: string } | null>(null);

  useEffect(() => {
    fetchIntegrations();
    const connected = searchParams.get("connected");
    const error = searchParams.get("error");
    if (connected) {
      setBanner({ type: "success", message: `${connected} connected successfully!` });
      setTimeout(() => setBanner(null), 4000);
      window.history.replaceState({}, "", "/integrations");
      // Re-fetch after a short delay to get updated status
      setTimeout(() => fetchIntegrations(), 500);
    } else if (error) {
      setBanner({ type: "error", message: `Connection error: ${decodeURIComponent(error)}` });
      setTimeout(() => setBanner(null), 6000);
      window.history.replaceState({}, "", "/integrations");
    }
  }, [fetchIntegrations, searchParams]);

  const displayIntegrations = integrations.length > 0 ? integrations : FALLBACK_INTEGRATIONS;

  // Merge: use backend connected state over fallback
  const mergedIntegrations = FALLBACK_INTEGRATIONS.map((fallback) => {
    const fromBackend = integrations.find((i) => i.id === fallback.id);
    return fromBackend ?? fallback;
  });
  return (
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

        {/* Banner */}
        {banner && (
          <div className={`mb-6 px-4 py-3 rounded-xl text-sm font-medium flex items-center gap-2 animate-fade-in ${
            banner.type === "success"
              ? "bg-emerald-500/10 border border-emerald-500/20 text-emerald-400"
              : "bg-red-500/10 border border-red-500/20 text-red-400"
          }`}>
            <span>{banner.type === "success" ? "✓" : "⚠"}</span>
            {banner.message}
          </div>
        )}

        {/* Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {mergedIntegrations.map((integration) => (
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
  );
}

export default function IntegrationsPage() {
  return (
    <div className="flex h-screen w-full bg-[#111111] overflow-hidden">
      <Sidebar />
      <Suspense fallback={<main className="flex-1" />}>
        <IntegrationsContent />
      </Suspense>
      <CommandPalette />
    </div>
  );
}
