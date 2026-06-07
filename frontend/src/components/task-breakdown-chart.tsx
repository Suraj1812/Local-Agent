"use client";

import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

export function TaskBreakdownChart({ data }: { data: Array<{ status: string; count: number }> }) {
  return (
    <ResponsiveContainer width="100%" height="100%">
      <BarChart data={data}>
        <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
        <XAxis dataKey="status" stroke="var(--muted-foreground)" />
        <YAxis allowDecimals={false} stroke="var(--muted-foreground)" />
        <Tooltip />
        <Bar dataKey="count" fill="var(--primary)" radius={[4, 4, 0, 0]} />
      </BarChart>
    </ResponsiveContainer>
  );
}
