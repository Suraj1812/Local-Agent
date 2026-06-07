export type Message = {
  id: number;
  conversation_id: number;
  role: "user" | "assistant" | "system" | "tool";
  content: string;
  metadata: Record<string, unknown>;
  created_at: string;
};

export type Conversation = {
  id: number;
  title: string;
  created_at: string;
  updated_at: string;
  messages?: Message[];
};

export type AgentTask = {
  id: number;
  title: string;
  priority: string;
  status?: string;
  tool?: string;
};

export type AgentActivity = {
  current_goal: string;
  current_task: string | null;
  completed_tasks: AgentTask[];
  active_tool: string | null;
  execution_progress: number;
  reasoning_steps: string[];
  status: string;
};

export type Settings = {
  model: string;
  temperature: number;
  memory_limit: number;
  theme: "light";
  tools_enabled: Record<string, boolean>;
  agent_config: Record<string, boolean>;
  supported_models: string[];
  require_ollama?: boolean;
  tools?: Array<{ name: string; description: string; enabled: boolean }>;
};

export type Dashboard = {
  totals: {
    conversations: number;
    tasks: number;
    completed_tasks: number;
    memories: number;
    documents: number;
  };
  task_breakdown: Array<{ status: string; count: number }>;
  recent_activity: LogEntry[];
};

export type LogEntry = {
  id: number;
  conversation_id?: number | null;
  level: string;
  action: string;
  detail: string;
  metadata: Record<string, unknown>;
  created_at: string;
};

export type DocumentItem = {
  id: number;
  filename: string;
  mime_type: string;
  chunks: number;
  created_at?: string;
};
