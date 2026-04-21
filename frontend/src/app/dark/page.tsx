"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useThemeStore } from "@/lib/store/themeStore";

export default function DarkLanding() {
  const { setTheme } = useThemeStore();
  const router = useRouter();

  useEffect(() => {
    setTheme("dark");
  }, [setTheme]);

  return (
    <main className="min-h-screen bg-[#0a0a0a] flex flex-col items-center justify-center px-6 relative overflow-hidden">
      <div className="absolute top-1/3 left-1/4 w-[500px] h-[500px] bg-[#6C63FF]/8 rounded-full blur-[150px]" />
      <div className="absolute bottom-1/3 right-1/4 w-[400px] h-[400px] bg-indigo-600/8 rounded-full blur-[130px]" />

      <div className="relative z-10 text-center max-w-xl animate-fade-in">
        <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-[#6C63FF] to-[#8B5CF6] flex items-center justify-center text-2xl mx-auto mb-6 shadow-2xl shadow-purple-500/20">
          🌙
        </div>
        <h1 className="text-4xl font-bold mb-3 text-white tracking-tight">
          Dark Mode <span className="text-gradient">Activated</span>
        </h1>
        <p className="text-white/40 mb-8">
          Immerse yourself in the premium dark experience. Easy on the eyes, powerful in execution.
        </p>
        <button
          onClick={() => router.push("/chat")}
          className="px-8 py-3.5 rounded-xl bg-accent hover:bg-accent-hover text-white text-sm font-semibold transition-all shadow-lg shadow-accent/25 active:scale-95"
        >
          Enter Workspace →
        </button>
      </div>
    </main>
  );
}
