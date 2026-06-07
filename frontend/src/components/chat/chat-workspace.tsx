"use client";

import { Loader2 } from "lucide-react";
import { ChatComposer } from "@/components/chat/chat-composer";
import { ChatMessage } from "@/components/chat/chat-message";
import { Progress } from "@/components/ui/progress";
import { useAppStore } from "@/store/app-store";

export function ChatWorkspace() {
  const conversation = useAppStore((state) => state.activeConversation);
  const optimisticMessages = useAppStore((state) => state.optimisticMessages);
  const isRunning = useAppStore((state) => state.isRunning);
  const activity = useAppStore((state) => state.activity);
  const plan = useAppStore((state) => state.plan);
  const messages = [...(conversation?.messages || []), ...optimisticMessages];
  const completed =
    activity?.completed_tasks.filter((task) => task.status === "completed" || task.status === "failed").length || 0;
  const progress = plan.length ? Math.max(12, Math.round((completed / plan.length) * 100)) : isRunning ? 16 : 0;
  const currentTask = activity?.current_task || (isRunning ? "Thinking" : null);

  return (
    <div className="flex h-dvh min-h-screen flex-col overflow-hidden bg-background text-foreground">
      <section className="min-h-0 flex-1 overflow-y-auto px-4 py-5 md:px-6">
        <div className="mx-auto flex min-h-full w-full max-w-3xl flex-col">
          {messages.length ? (
            <div className="flex flex-1 flex-col gap-5">
              {messages.map((message) => (
                <ChatMessage key={`${message.id}-${message.role}-${message.created_at}`} message={message} />
              ))}
            </div>
          ) : (
            <div className="grid flex-1 place-items-center text-center">
              <p className="text-sm text-muted-foreground">Ask anything.</p>
            </div>
          )}
        </div>
      </section>

      {isRunning && (
        <div className="shrink-0 border-t bg-background px-4 py-2 md:px-6">
          <div className="mx-auto flex max-w-3xl items-center gap-3 text-xs text-muted-foreground">
            <Loader2 className="h-3.5 w-3.5 shrink-0 animate-spin text-primary" />
            <Progress value={progress} className="h-1 w-20 shrink-0 md:w-28" />
            <span className="min-w-0 truncate">{currentTask}</span>
          </div>
        </div>
      )}

      <ChatComposer />
    </div>
  );
}
