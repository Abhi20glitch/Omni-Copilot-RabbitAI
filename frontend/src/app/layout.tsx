import "./globals.css";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Omni Copilot — Universal AI Workspace",
  description:
    "Chat-first universal AI workspace. Orchestrate Gmail, Calendar, GitHub, Notion, Slack, Drive and more from a single interface.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className="bg-[#111111] text-white antialiased">{children}</body>
    </html>
  );
}
