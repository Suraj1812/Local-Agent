"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { BarChart3, BrainCircuit, Files, MessageSquare, ScrollText, Settings } from "lucide-react";
import { useEffect } from "react";
import { useAppStore } from "@/store/app-store";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

const navItems = [
  { href: "/", label: "Chat", icon: MessageSquare },
  { href: "/dashboard", label: "Dashboard", icon: BarChart3 },
  { href: "/knowledge", label: "Knowledge", icon: Files },
  { href: "/logs", label: "Logs", icon: ScrollText },
  { href: "/settings", label: "Settings", icon: Settings }
];

export function AppShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const loadInitial = useAppStore((state) => state.loadInitial);

  useEffect(() => {
    loadInitial().catch(() => undefined);
  }, [loadInitial]);

  return (
    <main className="flex min-h-screen bg-background text-foreground">
      <aside className="hidden w-64 shrink-0 border-r bg-card/80 p-3 lg:block">
        <div className="mb-4 flex h-12 items-center gap-2 px-2">
          <div className="flex h-9 w-9 items-center justify-center rounded-md bg-primary text-primary-foreground">
            <BrainCircuit className="h-5 w-5" />
          </div>
          <div>
            <div className="text-sm font-semibold">FirstAI</div>
            <div className="text-xs text-muted-foreground">Local Agent</div>
          </div>
        </div>
        <nav className="space-y-1">
          {navItems.map((item) => {
            const Icon = item.icon;
            const active = pathname === item.href;
            return (
              <Button
                key={item.href}
                asChild
                variant={active ? "secondary" : "ghost"}
                className={cn("w-full justify-start", active && "text-primary")}
              >
                <Link href={item.href}>
                  <Icon className="h-4 w-4" />
                  {item.label}
                </Link>
              </Button>
            );
          })}
        </nav>
        <ConversationRail />
      </aside>
      <section className="min-w-0 flex-1">{children}</section>
    </main>
  );
}

function ConversationRail() {
  const conversations = useAppStore((state) => state.conversations);
  const active = useAppStore((state) => state.activeConversation);
  const openConversation = useAppStore((state) => state.openConversation);

  return (
    <div className="mt-5 border-t pt-4">
      <div className="mb-2 px-2 text-xs font-medium uppercase text-muted-foreground">Conversations</div>
      <div className="max-h-[calc(100vh-260px)] space-y-1 overflow-auto pr-1">
        {conversations.map((conversation) => (
          <button
            key={conversation.id}
            onClick={() => openConversation(conversation.id)}
            className={cn(
              "w-full rounded-md px-2 py-2 text-left text-xs transition-colors hover:bg-secondary",
              active?.id === conversation.id && "bg-secondary text-primary"
            )}
          >
            <span className="line-clamp-2">{conversation.title}</span>
          </button>
        ))}
        {!conversations.length && (
          <div className="rounded-md border border-dashed p-3 text-xs text-muted-foreground">No conversations yet</div>
        )}
      </div>
    </div>
  );
}
