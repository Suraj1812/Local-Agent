"use client";

import { Loader2, SendHorizontal } from "lucide-react";
import { FormEvent, useState } from "react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { useAppStore } from "@/store/app-store";

export function ChatComposer() {
  const [goal, setGoal] = useState("");
  const sendGoal = useAppStore((state) => state.sendGoal);
  const isRunning = useAppStore((state) => state.isRunning);

  async function onSubmit(event: FormEvent) {
    event.preventDefault();
    const clean = goal.trim();
    if (!clean || isRunning) return;
    setGoal("");
    await sendGoal(clean);
  }

  return (
    <form onSubmit={onSubmit} className="shrink-0 border-t bg-background px-3 py-3 md:px-6 md:py-4">
      <div className="mx-auto flex max-w-3xl items-end gap-2">
        <Textarea
          value={goal}
          onChange={(event) => setGoal(event.target.value)}
          onKeyDown={(event) => {
            if (event.key === "Enter" && !event.shiftKey) {
              event.preventDefault();
              event.currentTarget.form?.requestSubmit();
            }
          }}
          placeholder="Ask anything..."
          className="max-h-40 min-h-12 resize-none rounded-md border-input bg-white px-3 py-3 text-[15px] leading-6 shadow-none"
        />
        <Button type="submit" size="icon" disabled={isRunning || !goal.trim()} aria-label="Send">
          {isRunning ? <Loader2 className="h-4 w-4 animate-spin" /> : <SendHorizontal className="h-4 w-4" />}
        </Button>
      </div>
    </form>
  );
}
