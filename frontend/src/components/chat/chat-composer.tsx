"use client";

import { SendHorizontal } from "lucide-react";
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
    <form onSubmit={onSubmit} className="shrink-0 border-t bg-card/95 p-3 md:p-4">
      <div className="mx-auto flex max-w-4xl items-end gap-2">
        <Textarea
          value={goal}
          onChange={(event) => setGoal(event.target.value)}
          onKeyDown={(event) => {
            if (event.key === "Enter" && !event.shiftKey) {
              event.preventDefault();
              event.currentTarget.form?.requestSubmit();
            }
          }}
          placeholder="Message FirstAI"
          className="min-h-14 max-h-40 resize-none rounded-lg bg-background"
        />
        <Button type="submit" size="icon" disabled={isRunning || !goal.trim()} aria-label="Send goal">
          <SendHorizontal className="h-4 w-4" />
        </Button>
      </div>
    </form>
  );
}
