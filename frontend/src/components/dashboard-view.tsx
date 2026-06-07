"use client";

import dynamic from "next/dynamic";
import { CheckCircle2, Database, Files, MessageSquare, ScrollText } from "lucide-react";
import { useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useAppStore } from "@/store/app-store";

const TaskBreakdownChart = dynamic(
  () => import("@/components/task-breakdown-chart").then((module) => module.TaskBreakdownChart),
  {
    ssr: false,
    loading: () => <div className="grid h-full place-items-center text-sm text-muted-foreground">Loading chart...</div>
  }
);

const statIcons = {
  conversations: MessageSquare,
  tasks: ScrollText,
  completed_tasks: CheckCircle2,
  memories: Database,
  documents: Files
};

export function DashboardView() {
  const dashboard = useAppStore((state) => state.dashboard);
  const loadDashboard = useAppStore((state) => state.loadDashboard);

  useEffect(() => {
    loadDashboard().catch(() => undefined);
  }, [loadDashboard]);

  return (
    <div className="h-screen overflow-auto p-4 md:p-6">
      <div className="mb-5">
        <h1 className="text-xl font-semibold">Dashboard</h1>
        <p className="text-sm text-muted-foreground">Agent usage and local storage</p>
      </div>
      <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-5">
        {dashboard &&
          Object.entries(dashboard.totals).map(([key, value]) => {
            const Icon = statIcons[key as keyof typeof statIcons];
            return (
              <Card key={key}>
                <CardContent className="flex items-center justify-between p-4">
                  <div>
                    <div className="text-xs uppercase text-muted-foreground">{key.replace("_", " ")}</div>
                    <div className="mt-1 text-2xl font-semibold">{value}</div>
                  </div>
                  <Icon className="h-5 w-5 text-primary" />
                </CardContent>
              </Card>
            );
          })}
      </div>
      <div className="mt-4 grid gap-4 xl:grid-cols-[minmax(0,1fr)_380px]">
        <Card>
          <CardHeader>
            <CardTitle>Tasks</CardTitle>
          </CardHeader>
          <CardContent className="h-80">
            <TaskBreakdownChart data={dashboard?.task_breakdown || []} />
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>Recent Activity</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            {(dashboard?.recent_activity || []).map((item) => (
              <div key={item.id} className="rounded-md border bg-background p-2">
                <div className="text-sm">{item.action}</div>
                <div className="line-clamp-2 text-xs text-muted-foreground">{item.detail}</div>
              </div>
            ))}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
