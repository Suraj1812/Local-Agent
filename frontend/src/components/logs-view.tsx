"use client";

import { useEffect } from "react";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useAppStore } from "@/store/app-store";

export function LogsView() {
  const logs = useAppStore((state) => state.logs);
  const loadLogs = useAppStore((state) => state.loadLogs);

  useEffect(() => {
    loadLogs().catch(() => undefined);
  }, [loadLogs]);

  return (
    <div className="h-screen overflow-auto p-4 md:p-6">
      <div className="mb-5">
        <h1 className="text-xl font-semibold">Logs</h1>
        <p className="text-sm text-muted-foreground">Agent actions, tools, and task execution</p>
      </div>
      <Card>
        <CardHeader>
          <CardTitle>Agent Log</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="divide-y rounded-md border">
            {logs.map((log) => (
              <div key={log.id} className="grid gap-2 p-3 text-sm lg:grid-cols-[120px_160px_minmax(0,1fr)_180px]">
                <Badge>{log.level}</Badge>
                <div className="font-medium">{log.action}</div>
                <div className="line-clamp-2 text-muted-foreground">{log.detail}</div>
                <div className="font-mono text-xs text-muted-foreground">{new Date(log.created_at).toLocaleString()}</div>
              </div>
            ))}
            {!logs.length && <div className="p-4 text-sm text-muted-foreground">No logs yet</div>}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
