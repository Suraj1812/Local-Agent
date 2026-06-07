"use client";

import { ActivityPanel } from "@/components/chat/activity-panel";
import { ChatComposer } from "@/components/chat/chat-composer";
import { ChatMessage } from "@/components/chat/chat-message";
import { Badge } from "@/components/ui/badge";
import { useAppStore } from "@/store/app-store";

export function ChatWorkspace() {
  const conversation = useAppStore((state) => state.activeConversation);
  const optimisticMessages = useAppStore((state) => state.optimisticMessages);
  const isRunning = useAppStore((state) => state.isRunning);
  const messages = [...(conversation?.messages || []), ...optimisticMessages];

  return (
    <div className="grid h-screen grid-cols-1 xl:grid-cols-[minmax(0,1fr)_360px]">
      <section className="flex min-h-0 flex-col">
        <header className="flex h-16 shrink-0 items-center justify-between border-b px-4 md:px-6">
          <div>
            <div className="text-sm font-semibold">{conversation?.title || "New agent session"}</div>
            <div className="text-xs text-muted-foreground">Ollama + FastAPI + SQLite</div>
          </div>
          <Badge>{isRunning ? "Running" : "Ready"}</Badge>
        </header>
        <div className="min-h-0 flex-1 overflow-auto px-4 py-5 md:px-6">
          <div className="mx-auto flex max-w-4xl flex-col gap-4">
            {messages.length ? (
              messages.map((message) => <ChatMessage key={`${message.id}-${message.role}`} message={message} />)
            ) : (
              <div className="grid min-h-[55vh] place-items-center text-center">
                <div>
                  <div className="text-2xl font-semibold">FirstAI</div>
                  <div className="mt-2 text-sm text-muted-foreground">Local multi-agent workspace</div>
                </div>
              </div>
            )}
            {isRunning && (
              <div className="w-fit rounded-lg border bg-card px-3 py-2 text-sm text-muted-foreground">
                Agent is working...
              </div>
            )}
          </div>
        </div>
        <ChatComposer />
      </section>
      <ActivityPanel />
    </div>
  );
}
