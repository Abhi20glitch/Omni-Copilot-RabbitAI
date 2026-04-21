"use client";

import { useEffect, useState } from "react";
import Sidebar from "@/components/Layout/Sidebar";
import CommandPalette from "@/components/Layout/CommandPalette";
import { useMemoryStore } from "@/lib/store/memoryStore";

export default function MemoryPage() {
  const { memories, loading, fetchMemories, addMemory, deleteMemory } = useMemoryStore();
  const [newKey, setNewKey] = useState("");
  const [newValue, setNewValue] = useState("");
  const [editingId, setEditingId] = useState<string | null>(null);
  const [editValue, setEditValue] = useState("");

  useEffect(() => {
    fetchMemories();
  }, [fetchMemories]);

  const handleAdd = async () => {
    if (!newKey.trim() || !newValue.trim()) return;
    await addMemory(newKey.trim(), newValue.trim());
    setNewKey("");
    setNewValue("");
  };

  return (
    <div className="flex h-screen w-full bg-[#111111] overflow-hidden">
      <Sidebar />
      <main className="flex-1 overflow-y-auto">
        <div className="max-w-3xl mx-auto px-8 py-10">
          {/* Header */}
          <div className="mb-8">
            <h1 className="text-2xl font-bold mb-2">
              <span className="text-gradient">Memory Viewer</span>
            </h1>
            <p className="text-sm text-white/40">
              View, edit, and manage what the AI remembers about you and your preferences.
            </p>
          </div>

          {/* Add New Memory */}
          <div className="p-5 rounded-xl bg-white/[0.03] border border-white/[0.06] mb-6">
            <h3 className="text-sm font-semibold mb-3">Add New Memory</h3>
            <div className="flex flex-col sm:flex-row gap-3">
              <input
                id="memory-key-input"
                value={newKey}
                onChange={(e) => setNewKey(e.target.value)}
                placeholder="Key (e.g., preferred_language)"
                className="flex-1 px-3 py-2.5 rounded-lg bg-white/[0.05] border border-white/[0.08] text-sm placeholder:text-white/25 outline-none focus:border-accent/50 transition-colors"
              />
              <input
                id="memory-value-input"
                value={newValue}
                onChange={(e) => setNewValue(e.target.value)}
                placeholder="Value (e.g., TypeScript)"
                className="flex-1 px-3 py-2.5 rounded-lg bg-white/[0.05] border border-white/[0.08] text-sm placeholder:text-white/25 outline-none focus:border-accent/50 transition-colors"
                onKeyDown={(e) => e.key === "Enter" && handleAdd()}
              />
              <button
                id="add-memory-btn"
                onClick={handleAdd}
                className="px-5 py-2.5 rounded-lg bg-accent hover:bg-accent-hover text-white text-sm font-medium transition-all active:scale-95"
              >
                Add
              </button>
            </div>
          </div>

          {/* Memory List */}
          {loading ? (
            <div className="flex items-center justify-center py-20 text-white/30">
              <span className="animate-pulse-soft mr-2">●</span> Loading memories...
            </div>
          ) : memories.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-20 text-white/20">
              <span className="text-4xl mb-3">🧠</span>
              <p className="text-sm">No memories stored yet</p>
              <p className="text-xs mt-1">Add entries above or chat with the AI to build memory</p>
            </div>
          ) : (
            <div className="space-y-2">
              {memories.map((mem) => (
                <div
                  key={mem.id}
                  className="group p-4 rounded-xl bg-white/[0.03] border border-white/[0.06] hover:border-white/[0.1] transition-all"
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1 min-w-0">
                      <span className="text-xs font-mono text-accent/70">{mem.key}</span>
                      {editingId === mem.id ? (
                        <div className="flex gap-2 mt-1">
                          <input
                            value={editValue}
                            onChange={(e) => setEditValue(e.target.value)}
                            className="flex-1 px-2 py-1 rounded bg-white/[0.05] border border-white/[0.08] text-sm outline-none focus:border-accent/50"
                            onBlur={async () => {
                              if (editValue.trim()) await addMemory(mem.key, editValue);
                              setEditingId(null);
                            }}
                            onKeyDown={async (e) => {
                              if (e.key === "Enter") {
                                await addMemory(mem.key, editValue);
                                setEditingId(null);
                              }
                              if (e.key === "Escape") setEditingId(null);
                            }}
                            autoFocus
                          />
                        </div>
                      ) : (
                        <p className="text-sm text-white/70 mt-0.5 truncate">{mem.value}</p>
                      )}
                      <p className="text-[10px] text-white/20 mt-1">
                        Updated {new Date(mem.updatedAt).toLocaleString()}
                      </p>
                    </div>
                    <div className="flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity ml-3">
                      <button
                        onClick={() => {
                          setEditingId(mem.id);
                          setEditValue(mem.value);
                        }}
                        className="px-2 py-1 rounded text-[11px] text-white/40 hover:text-accent hover:bg-accent/10 transition-all"
                      >
                        Edit
                      </button>
                      <button
                        onClick={() => deleteMemory(mem.id)}
                        className="px-2 py-1 rounded text-[11px] text-white/40 hover:text-red-400 hover:bg-red-500/10 transition-all"
                      >
                        Delete
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </main>
      <CommandPalette />
    </div>
  );
}
