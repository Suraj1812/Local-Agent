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

export type APInvoice = {
  id: string;
  invoice_number: string;
  vendor_id: string;
  vendor: string;
  po_number: string;
  currency: string;
  amount: number;
  status: "matched" | "exception" | "ready_to_post" | string;
  match_type: string;
  risk: string;
  confidence: number;
  due_date: string;
  erp: string;
};

export type APException = {
  id: string;
  invoice_id: string;
  type: string;
  severity: string;
  owner: string;
  summary: string;
  next_action: string;
};

export type APJournalEntry = {
  id: string;
  invoice_id: string;
  status: string;
  erp: string;
  lines: Array<{ account: string; debit: number; credit: number }>;
};

export type FinanceAgent = {
  name: string;
  status: string;
  focus: string;
  last_run: string;
};

export type APOverview = {
  metrics: {
    invoice_volume: number;
    payable_exposure: number;
    straight_through_rate: number;
    match_accuracy: number;
    exceptions_open: number;
    avg_cycle_time_hours: number;
    erp_sync_ready: number;
  };
  systems: string[];
  modules: string[];
  invoices: APInvoice[];
  exceptions: APException[];
  journal_entries: APJournalEntry[];
  agents: FinanceAgent[];
};

export type APMatchingResult = {
  status: string;
  score: number;
  match_type: string;
  checks: Array<{ name: string; status: string; delta?: number }>;
  exceptions: Array<{ type: string; severity: string; message: string }>;
  recommendation: string;
};
