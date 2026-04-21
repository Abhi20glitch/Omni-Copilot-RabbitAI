"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useThemeStore } from "@/lib/store/themeStore";

export default function LightLanding() {
  const { setTheme } = useThemeStore();
  const router = useRouter();

  useEffect(() => {
    setTheme("light");
  }, [setTheme]);

  return (
    <main className="min-h-screen bg-[#fafafa] flex flex-col items-center justify-center px-6 relative overflow-hidden">
      <div className="absolute top-1/3 left-1/4 w-[500px] h-[500px] bg-indigo-200/40 rounded-full blur-[150px]" />
      <div className="absolute bottom-1/3 right-1/4 w-[400px] h-[400px] bg-violet-200/30 rounded-full blur-[130px]" />

      <div className="relative z-10 text-center max-w-xl animate-fade-in">
        <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-[#6C63FF] to-[#a78bfa] flex items-center justify-center text-2xl mx-auto mb-6 shadow-xl shadow-indigo-300/30">
          ☀️
        </div>
        <h1 className="text-4xl font-bold mb-3 text-gray-900 tracking-tight">
          Light Mode <span className="bg-gradient-to-r from-[#6C63FF] to-[#a78bfa] bg-clip-text text-transparent">Activated</span>
        </h1>
        <p className="text-gray-500 mb-8">
          Clean, bright, and crisp. Perfect for daytime productivity and focus.
        </p>
        <button
          onClick={() => router.push("/chat")}
          className="px-8 py-3.5 rounded-xl bg-[#6C63FF] hover:bg-[#7B73FF] text-white text-sm font-semibold transition-all shadow-lg shadow-indigo-400/25 active:scale-95"
        >
          Enter Workspace →
        </button>
      </div>
    </main>
  );
}
