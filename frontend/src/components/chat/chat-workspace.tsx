"use client";

import { ChangeEvent, useRef, useState } from "react";
import { BrainCircuit, Loader2, Paperclip } from "lucide-react";
import { ChatComposer } from "@/components/chat/chat-composer";
import { ChatMessage } from "@/components/chat/chat-message";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { cn } from "@/lib/utils";
import { useAppStore } from "@/store/app-store";

export function ChatWorkspace() {
  const conversation = useAppStore((state) => state.activeConversation);
  const conversations = useAppStore((state) => state.conversations);
  const optimisticMessages = useAppStore((state) => state.optimisticMessages);
  const isRunning = useAppStore((state) => state.isRunning);
  const settings = useAppStore((state) => state.settings);
  const activity = useAppStore((state) => state.activity);
  const plan = useAppStore((state) => state.plan);
  const openConversation = useAppStore((state) => state.openConversation);
  const saveSettings = useAppStore((state) => state.saveSettings);
  const uploadDocument = useAppStore((state) => state.uploadDocument);
  const inputRef = useRef<HTMLInputElement>(null);
  const [uploading, setUploading] = useState(false);
  const messages = [...(conversation?.messages || []), ...optimisticMessages];
  const completedTasks =
    activity?.completed_tasks.filter((task) => task.status === "completed" || task.status === "failed").length || 0;
  const progress = plan.length ? Math.min(100, Math.round((completedTasks / plan.length) * 100)) : isRunning ? 18 : 100;
  const currentTask =
    activity?.current_task ||
    (isRunning ? plan.find((task) => task.status !== "completed")?.title : undefined);

  async function handleModelChange(event: ChangeEvent<HTMLSelectElement>) {
    await saveSettings({ model: event.target.value, theme: "light" });
  }

  async function handleFileChange(event: ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];
    if (!file) {
      return;
    }
    setUploading(true);
    try {
      await uploadDocument(file);
    } catch (error) {
      window.alert(error instanceof Error ? error.message : "Upload failed");
    } finally {
      setUploading(false);
      event.target.value = "";
    }
  }

  return (
    <div className="flex h-screen flex-col bg-background">
      <header className="shrink-0 border-b bg-card/95">
        <div className="mx-auto flex max-w-5xl items-center justify-between gap-3 px-4 py-3 md:px-6">
          <div className="flex min-w-0 items-center gap-3">
            <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-md bg-primary text-primary-foreground">
              <BrainCircuit className="h-5 w-5" />
            </div>
            <div className="min-w-0">
              <div className="text-sm font-semibold">FirstAI</div>
              <div className="truncate text-xs text-muted-foreground">{conversation?.title || "New chat"}</div>
            </div>
          </div>

          <div className="flex shrink-0 items-center gap-2">
            <span
              className={cn(
                "hidden items-center gap-1.5 rounded-full border px-2.5 py-1 text-xs font-medium sm:inline-flex",
                isRunning ? "border-primary/25 text-primary" : "border-border text-muted-foreground"
              )}
            >
              {isRunning && <Loader2 className="h-3 w-3 animate-spin" />}
              {isRunning ? "Working" : "Ready"}
            </span>
            <select
              aria-label="Model"
              value={settings?.model || "llama3"}
              onChange={handleModelChange}
              className="h-9 rounded-md border bg-background px-2 text-sm outline-none transition focus:border-primary focus:ring-2 focus:ring-primary/15"
            >
              {(settings?.supported_models || ["llama3", "qwen2.5", "deepseek-r1"]).map((model) => (
                <option key={model} value={model}>
                  {model}
                </option>
              ))}
            </select>
            <input ref={inputRef} type="file" className="hidden" onChange={handleFileChange} />
            <Button
              type="button"
              variant="outline"
              size="icon"
              aria-label="Upload file"
              onClick={() => inputRef.current?.click()}
              disabled={uploading}
            >
              {uploading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Paperclip className="h-4 w-4" />}
            </Button>
          </div>
        </div>

        {!!conversations.length && (
          <div className="mx-auto flex max-w-5xl gap-2 overflow-x-auto px-4 pb-3 md:px-6">
            {conversations.slice(0, 8).map((item) => (
              <button
                key={item.id}
                type="button"
                onClick={() => openConversation(item.id)}
                className={cn(
                  "max-w-48 shrink-0 truncate rounded-full border px-3 py-1.5 text-xs transition",
                  item.id === conversation?.id
                    ? "border-primary bg-primary text-primary-foreground"
                    : "border-border bg-background text-muted-foreground hover:border-primary/40 hover:text-foreground"
                )}
              >
                {item.title}
              </button>
            ))}
          </div>
        )}
      </header>

      {(isRunning || currentTask) && (
        <div className="shrink-0 border-b bg-background">
          <div className="mx-auto flex max-w-5xl items-center gap-3 px-4 py-2 text-xs text-muted-foreground md:px-6">
            <Progress value={progress} className="h-1.5 w-28 shrink-0 md:w-40" />
            <span className="truncate">{currentTask || "Finishing"}</span>
          </div>
        </div>
      )}

      <section className="min-h-0 flex-1 overflow-auto px-4 py-5 md:px-6">
        <div className="mx-auto flex max-w-4xl flex-col gap-5">
          {messages.length ? (
            messages.map((message) => <ChatMessage key={`${message.id}-${message.role}`} message={message} />)
          ) : (
            <div className="grid min-h-[56vh] place-items-center text-center">
              <div>
                <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-md bg-primary text-primary-foreground">
                  <BrainCircuit className="h-6 w-6" />
                </div>
                <div className="text-2xl font-semibold">FirstAI</div>
              </div>
            </div>
          )}
        </div>
      </section>

      <ChatComposer />
    </div>
  );
}
