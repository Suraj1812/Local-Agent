"use client";

import { useEffect } from "react";
import { useAppStore } from "@/store/app-store";

export function AppShell({ children }: { children: React.ReactNode }) {
  const loadInitial = useAppStore((state) => state.loadInitial);

  useEffect(() => {
    loadInitial().catch(() => undefined);
  }, [loadInitial]);

  return <main className="min-h-screen bg-background text-foreground">{children}</main>;
}
