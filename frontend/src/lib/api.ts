import type { Conversation, Dashboard, DocumentItem, LogEntry, Settings } from "@/lib/types";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000/api";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers: {
      ...(init?.body instanceof FormData ? {} : { "Content-Type": "application/json" }),
      ...init?.headers
    }
  });
  if (!response.ok) {
    throw new Error(await response.text());
  }
  return response.json() as Promise<T>;
}

export const api = {
  conversations: () => request<Conversation[]>("/conversations"),
  conversation: (id: number) => request<Conversation>(`/conversations/${id}`),
  dashboard: () => request<Dashboard>("/dashboard"),
  settings: () => request<Settings>("/settings"),
  updateSettings: (settings: Partial<Settings>) =>
    request<Settings>("/settings", {
      method: "PUT",
      body: JSON.stringify(settings)
    }),
  logs: () => request<LogEntry[]>("/logs"),
  documents: () => request<DocumentItem[]>("/knowledge"),
  uploadDocument: (file: File) => {
    const form = new FormData();
    form.append("file", file);
    return request<DocumentItem>("/knowledge/upload", { method: "POST", body: form });
  },
  streamAgent: async (
    goal: string,
    conversationId: number | null,
    onEvent: (event: { type: string; payload: unknown }) => void
  ) => {
    const response = await fetch(`${API_BASE}/agent/stream`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ goal, conversation_id: conversationId })
    });

    if (!response.ok || !response.body) {
      throw new Error(await response.text());
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = "";

    while (true) {
      const { value, done } = await reader.read();
      if (done) break;
      buffer += decoder.decode(value, { stream: true });
      const events = buffer.split("\n\n");
      buffer = events.pop() || "";
      for (const rawEvent of events) {
        const line = rawEvent
          .split("\n")
          .find((item) => item.startsWith("data: "));
        if (!line) continue;
        onEvent(JSON.parse(line.slice(6)));
      }
    }
  }
};
