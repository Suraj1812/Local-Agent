"use client";

import { CheckCircle2, Cpu, ListChecks } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { useAppStore } from "@/store/app-store";

export function ActivityPanel() {
  const activity = useAppStore((state) => state.activity);
  const plan = useAppStore((state) => state.plan);

  return (
    <aside className="hidden min-h-0 border-l bg-card/60 p-4 xl:block">
      <div className="flex h-full flex-col gap-4">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Cpu className="h-4 w-4 text-primary" />
              Agent Activity
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="text-xs text-muted-foreground">Status</div>
            <div className="flex items-center justify-between gap-2">
              <Badge>{activity?.status || "idle"}</Badge>
              <span className="font-mono text-xs text-muted-foreground">{activity?.execution_progress || 0}%</span>
            </div>
            <Progress value={activity?.execution_progress || 0} />
            <div>
              <div className="mb-1 text-xs text-muted-foreground">Current Task</div>
              <div className="min-h-10 rounded-md border bg-background p-2 text-sm">
                {activity?.current_task || "Waiting"}
              </div>
            </div>
            <div>
              <div className="mb-1 text-xs text-muted-foreground">Active Tool</div>
              <Badge>{activity?.active_tool || "none"}</Badge>
            </div>
          </CardContent>
        </Card>

        <Card className="min-h-0 flex-1">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <ListChecks className="h-4 w-4 text-accent" />
              Plan
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-2 overflow-auto">
            {plan.map((task) => (
              <div key={`${task.id}-${task.title}`} className="rounded-md border bg-background p-2">
                <div className="flex items-start gap-2">
                  <CheckCircle2 className="mt-0.5 h-4 w-4 shrink-0 text-primary" />
                  <div>
                    <div className="text-sm">{task.title}</div>
                    <div className="mt-1 text-xs text-muted-foreground">{task.priority}</div>
                  </div>
                </div>
              </div>
            ))}
            {!plan.length && <div className="text-sm text-muted-foreground">No active plan</div>}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Reasoning Steps</CardTitle>
          </CardHeader>
          <CardContent className="max-h-44 space-y-2 overflow-auto">
            {(activity?.reasoning_steps || []).map((step, index) => (
              <div key={`${step}-${index}`} className="text-xs text-muted-foreground">
                {index + 1}. {step}
              </div>
            ))}
            {!activity?.reasoning_steps?.length && <div className="text-sm text-muted-foreground">Idle</div>}
          </CardContent>
        </Card>
      </div>
    </aside>
  );
}
