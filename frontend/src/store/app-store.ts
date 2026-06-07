"use client";

import { create } from "zustand";
import { api } from "@/lib/api";
import type {
  AgentActivity,
  AgentTask,
  Conversation,
  Dashboard,
  DocumentItem,
  LogEntry,
  Message,
  Settings
} from "@/lib/types";

type AppState = {
  conversations: Conversation[];
  activeConversation: Conversation | null;
  optimisticMessages: Message[];
  activity: AgentActivity | null;
  plan: AgentTask[];
  settings: Settings | null;
  dashboard: Dashboard | null;
  logs: LogEntry[];
  documents: DocumentItem[];
  isRunning: boolean;
  loadInitial: () => Promise<void>;
  openConversation: (id: number) => Promise<void>;
  sendGoal: (goal: string) => Promise<void>;
  loadDashboard: () => Promise<void>;
  loadKnowledge: () => Promise<void>;
  uploadDocument: (file: File) => Promise<void>;
  loadLogs: () => Promise<void>;
  saveSettings: (settings: Partial<Settings>) => Promise<void>;
};

const emptyActivity = (goal: string): AgentActivity => ({
  current_goal: goal,
  current_task: "Queued",
  completed_tasks: [],
  active_tool: null,
  execution_progress: 2,
  reasoning_steps: ["Goal queued"],
  status: "queued"
});

export const useAppStore = create<AppState>((set, get) => ({
  conversations: [],
  activeConversation: null,
  optimisticMessages: [],
  activity: null,
  plan: [],
  settings: null,
  dashboard: null,
  logs: [],
  documents: [],
  isRunning: false,
  loadInitial: async () => {
    const [conversations, settings] = await Promise.all([api.conversations(), api.settings()]);
    set({ conversations, settings });
    if (conversations[0]) {
      await get().openConversation(conversations[0].id);
    }
  },
  openConversation: async (id: number) => {
    const conversation = await api.conversation(id);
    set({ activeConversation: conversation, optimisticMessages: [], activity: null, plan: [] });
  },
  sendGoal: async (goal: string) => {
    const current = get().activeConversation;
    const tempMessage: Message = {
      id: Date.now(),
      conversation_id: current?.id || 0,
      role: "user",
      content: goal,
      metadata: {},
      created_at: new Date().toISOString()
    };

    set({
      isRunning: true,
      optimisticMessages: [tempMessage],
      activity: emptyActivity(goal)
    });

    try {
      await api.streamAgent(goal, current?.id || null, (event) => {
        if (event.type === "activity") {
          set({ activity: event.payload as AgentActivity });
        }
        if (event.type === "plan") {
          set({ plan: event.payload as AgentTask[] });
        }
        if (event.type === "final") {
          const payload = event.payload as {
            conversation: Conversation;
            activity: AgentActivity;
            plan: AgentTask[];
          };
          set({
            activeConversation: payload.conversation,
            activity: payload.activity,
            plan: payload.plan,
            optimisticMessages: []
          });
        }
      });
      const conversations = await api.conversations();
      set({ conversations });
    } finally {
      set({ isRunning: false });
    }
  },
  loadDashboard: async () => {
    set({ dashboard: await api.dashboard() });
  },
  loadKnowledge: async () => {
    set({ documents: await api.documents() });
  },
  uploadDocument: async (file: File) => {
    await api.uploadDocument(file);
    await get().loadKnowledge();
  },
  loadLogs: async () => {
    set({ logs: await api.logs() });
  },
  saveSettings: async (settings: Partial<Settings>) => {
    set({ settings: await api.updateSettings(settings) });
  }
}));
