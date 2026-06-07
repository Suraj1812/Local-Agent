"use client";

import { ChangeEvent, FormEvent, useEffect, useRef, useState } from "react";
import {
  AlertTriangle,
  Bot,
  Check,
  ChevronRight,
  CircleAlert,
  FileUp,
  Loader2,
  Play,
  SendHorizontal
} from "lucide-react";
import { api } from "@/lib/api";
import type { APException, APInvoice, APMatchingResult, APOverview } from "@/lib/types";
import { cn } from "@/lib/utils";
import { useAppStore } from "@/store/app-store";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";

type View = "queue" | "exceptions" | "agents";
type AgentBrief = {
  title: string;
  summary: string;
  signals: string[];
  actions: string[];
};

function money(value: number) {
  return new Intl.NumberFormat("en-US", {
    currency: "USD",
    maximumFractionDigits: 0,
    style: "currency"
  }).format(value);
}

function statusTone(status: string) {
  if (["matched", "ready_to_post", "online", "posted", "auto_approved", "passed"].includes(status)) {
    return "text-emerald-700";
  }
  if (["exception", "reviewing", "draft", "failed"].includes(status)) {
    return "text-amber-700";
  }
  return "text-muted-foreground";
}

function cleanAgentLine(line: string) {
  return line
    .replace(/^#{1,6}\s*/, "")
    .replace(/^[-*]\s*/, "")
    .replace(/\*\*/g, "")
    .trim();
}

function isSystemNoise(line: string) {
  const normalized = line.toLowerCase();
  return (
    normalized.includes("ollama is not reachable") ||
    (normalized.includes("fallback") && normalized.includes("path")) ||
    normalized.startsWith("agent plan completed") ||
    normalized.startsWith("output") ||
    normalized.startsWith("result for:") ||
    normalized.startsWith("completed '")
  );
}

function relatedExceptions(overview: APOverview, invoice: APInvoice) {
  return overview.exceptions.filter((item) => item.invoice_id === invoice.id);
}

function buildAgentBrief({
  content,
  goal,
  matching,
  overview,
  selectedInvoice
}: {
  content: string;
  goal?: string;
  matching: APMatchingResult | null;
  overview: APOverview;
  selectedInvoice: APInvoice | null;
}): AgentBrief {
  const wantsRisk = /risk|highest|exception|summar/i.test(`${goal || ""} ${content}`);
  const exceptionInvoice = overview.invoices.find((invoice) => invoice.status === "exception") || overview.invoices[0];
  const targetInvoice = wantsRisk ? exceptionInvoice : selectedInvoice || exceptionInvoice;
  const exceptions = relatedExceptions(overview, targetInvoice);
  const visibleLines = content
    .split("\n")
    .map(cleanAgentLine)
    .filter((line) => line && !isSystemNoise(line));
  const selectedScore = selectedInvoice?.id === targetInvoice.id ? matching?.score : undefined;
  const score = selectedScore ?? (targetInvoice.status === "exception" ? 55 : targetInvoice.status === "matched" ? 100 : 90);
  const failedChecks =
    selectedInvoice?.id === targetInvoice.id
      ? (matching?.checks || []).filter((check) => check.status === "failed").map((check) => check.name)
      : targetInvoice.status === "exception"
        ? ["Amount within tolerance", "Goods receipt covers invoiced quantity"]
        : [];

  const title = wantsRisk
    ? `Highest risk: ${targetInvoice.vendor}`
    : targetInvoice.status === "exception"
      ? `Review needed: ${targetInvoice.vendor}`
      : `Ready: ${targetInvoice.vendor}`;
  const summary =
    visibleLines.find((line) => {
      const normalized = line.toLowerCase();
      return (
        !line.includes("(") &&
        !normalized.includes("define the research scope") &&
        !normalized.includes("search local knowledge") &&
        !normalized.includes("synthesize findings") &&
        !normalized.includes("return summary")
      );
    }) ||
    (targetInvoice.status === "exception"
      ? `${targetInvoice.invoice_number} should stay blocked until the PO variance and receiving gap are approved.`
      : `${targetInvoice.invoice_number} is policy-clean and can continue toward ERP posting.`);

  const signals = [
    `${targetInvoice.invoice_number} · ${money(targetInvoice.amount)} · ${targetInvoice.erp}`,
    `Policy score ${score}/100`,
    failedChecks.length ? `Failed checks: ${failedChecks.join(", ")}` : "All policy checks passed",
    ...exceptions.slice(0, 2).map((item) => item.summary)
  ];
  const actions = exceptions.length
    ? exceptions.slice(0, 2).map((item: APException) => item.next_action)
    : [matching?.recommendation || "Post to ERP", "Keep an audit trail for the final posting decision."];

  return { title, summary, signals, actions };
}

export function APCommandCenter() {
  const [overview, setOverview] = useState<APOverview | null>(null);
  const [matching, setMatching] = useState<APMatchingResult | null>(null);
  const [selectedInvoiceId, setSelectedInvoiceId] = useState<string | null>(null);
  const [view, setView] = useState<View>("queue");
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [prompt, setPrompt] = useState("");
  const [hasAsked, setHasAsked] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);
  const sendGoal = useAppStore((state) => state.sendGoal);
  const isRunning = useAppStore((state) => state.isRunning);
  const conversation = useAppStore((state) => state.activeConversation);
  const activity = useAppStore((state) => state.activity);

  useEffect(() => {
    let ignore = false;
    async function load() {
      try {
        const payload = await api.apOverview();
        const initial = payload.invoices.find((invoice) => invoice.status === "exception") || payload.invoices[0];
        const result = await runInvoiceMatch(initial);
        if (!ignore) {
          setOverview(payload);
          setSelectedInvoiceId(initial?.id || null);
          setMatching(result);
        }
      } finally {
        if (!ignore) {
          setLoading(false);
        }
      }
    }
    load().catch(() => setLoading(false));
    return () => {
      ignore = true;
    };
  }, []);

  const selectedInvoice =
    overview?.invoices.find((invoice) => invoice.id === selectedInvoiceId) || overview?.invoices[0] || null;
  const latestAnswer = [...(conversation?.messages || [])]
    .reverse()
    .find((message) => message.role === "assistant")?.content;
  const latestUserGoal = [...(conversation?.messages || [])]
    .reverse()
    .find((message) => message.role === "user")?.content;
  const agentBrief =
    overview && hasAsked && latestAnswer && !isRunning
      ? buildAgentBrief({ content: latestAnswer, goal: latestUserGoal, matching, overview, selectedInvoice })
      : null;

  async function runInvoiceMatch(invoice?: APInvoice) {
    if (!invoice) {
      return null;
    }
    return api.runAPMatching({
      invoice_number: `${invoice.invoice_number}-REVIEW`,
      po_number: invoice.po_number,
      amount: invoice.amount,
      vendor_id: invoice.vendor_id
    });
  }

  async function selectInvoice(invoice: APInvoice) {
    setSelectedInvoiceId(invoice.id);
    setMatching(null);
    setMatching(await runInvoiceMatch(invoice));
  }

  async function handleUpload(event: ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];
    if (!file) {
      return;
    }
    setUploading(true);
    try {
      await api.uploadDocument(file);
      window.alert("Invoice added to the extraction queue.");
    } catch (error) {
      window.alert(error instanceof Error ? error.message : "Upload failed");
    } finally {
      setUploading(false);
      event.target.value = "";
    }
  }

  async function handleRunMatch() {
    if (!selectedInvoice) {
      return;
    }
    setMatching(null);
    setMatching(await runInvoiceMatch(selectedInvoice));
  }

  async function askAgent(event: FormEvent) {
    event.preventDefault();
    const clean = prompt.trim();
    if (!clean || isRunning) {
      return;
    }
    setPrompt("");
    setHasAsked(true);
    await sendGoal(`Accounts payable finance agent task: ${clean}`);
  }

  if (loading || !overview) {
    return (
      <main className="grid min-h-screen place-items-center bg-background">
        <Loader2 className="h-5 w-5 animate-spin text-muted-foreground" aria-label="Loading" />
      </main>
    );
  }

  return (
    <main className="min-h-screen overflow-x-hidden bg-background text-foreground">
      <div className="sticky top-0 z-10 border-b bg-background/95 backdrop-blur">
        <form
          onSubmit={askAgent}
          className="mx-auto grid max-w-7xl grid-cols-[minmax(0,1fr)_auto] items-center gap-2 px-3 py-2 md:flex md:px-5 md:py-3"
        >
          <div className="flex h-10 min-w-0 items-center gap-2">
            <Bot className={cn("h-4 w-4 shrink-0", isRunning ? "text-primary" : "text-muted-foreground")} />
            <input
              value={prompt}
              onChange={(event) => setPrompt(event.target.value)}
              aria-label="Ask finance agent"
              autoComplete="off"
              placeholder="Ask about an invoice, exception, vendor, or posting"
              className="h-full min-w-0 flex-1 bg-transparent text-sm outline-none placeholder:text-muted-foreground"
            />
          </div>
          <div className="flex shrink-0 items-center gap-1">
            <span className="hidden shrink-0 text-xs text-muted-foreground lg:inline">
              {isRunning ? activity?.current_task || "Working" : `${overview.metrics.exceptions_open} needs review`}
            </span>
            <input ref={inputRef} type="file" className="hidden" onChange={handleUpload} />
            <Button
              type="button"
              variant="ghost"
              size="icon"
              aria-label="Upload invoice"
              title="Upload invoice"
              onClick={() => inputRef.current?.click()}
              disabled={uploading}
            >
              {uploading ? <Loader2 className="h-4 w-4 animate-spin" /> : <FileUp className="h-4 w-4" />}
            </Button>
            <Button
              type="button"
              variant="ghost"
              size="icon"
              aria-label="Run invoice match"
              title="Run invoice match"
              onClick={handleRunMatch}
              disabled={!selectedInvoice || !matching}
            >
              {matching ? <Play className="h-4 w-4" /> : <Loader2 className="h-4 w-4 animate-spin" />}
            </Button>
            <Button type="submit" size="icon" aria-label="Ask finance agent" title="Ask finance agent" disabled={isRunning || !prompt.trim()}>
              {isRunning ? <Loader2 className="h-4 w-4 animate-spin" /> : <SendHorizontal className="h-4 w-4" />}
            </Button>
          </div>
        </form>
        {isRunning && <Progress value={activity?.execution_progress || 5} className="h-0.5 rounded-none" />}
      </div>

      <div className="mx-auto max-w-7xl px-3 md:px-5">
        <div className="grid grid-cols-2 border-b py-3 sm:grid-cols-4">
          <Metric label="Exposure" value={money(overview.metrics.payable_exposure)} />
          <Metric label="No-touch" value={`${overview.metrics.straight_through_rate.toFixed(1)}%`} />
          <Metric label="Accuracy" value={`${overview.metrics.match_accuracy.toFixed(1)}%`} />
          <Metric label="Cycle" value={`${overview.metrics.avg_cycle_time_hours}h`} />
        </div>

        <div className="flex items-center justify-between border-b py-2">
          <div className="flex items-center gap-1">
            {(["queue", "exceptions", "agents"] as const).map((item) => (
              <button
                key={item}
                type="button"
                onClick={() => setView(item)}
                className={cn(
                  "rounded-md px-2.5 py-1.5 text-xs capitalize transition",
                  view === item ? "bg-secondary font-medium text-foreground" : "text-muted-foreground hover:text-foreground"
                )}
              >
                {item}
                {item === "exceptions" && <span className="ml-1 text-amber-700">{overview.exceptions.length}</span>}
              </button>
            ))}
          </div>
          <div className="hidden text-xs text-muted-foreground sm:block">
            {overview.systems.join(" · ")}
          </div>
        </div>

        <div className="grid min-w-0 lg:grid-cols-[minmax(0,1fr)_320px]">
          <section className="min-w-0 py-2 lg:pr-5">
            {view === "queue" && (
              <>
                <div className="space-y-1 md:hidden">
                  {overview.invoices.map((invoice) => (
                    <button
                      key={invoice.id}
                      type="button"
                      onClick={() => selectInvoice(invoice)}
                      className={cn(
                        "grid w-full min-w-0 grid-cols-[minmax(0,1fr)_auto] gap-3 border-b px-2 py-3 text-left outline-none transition hover:bg-secondary/50 focus-visible:bg-secondary focus-visible:ring-2 focus-visible:ring-inset focus-visible:ring-ring",
                        invoice.id === selectedInvoice?.id && "bg-secondary/70"
                      )}
                    >
                      <span className="min-w-0">
                        <span className="block truncate font-mono text-xs font-medium">{invoice.invoice_number}</span>
                        <span className="mt-1 block truncate text-sm">{invoice.vendor}</span>
                        <span className="mt-1 block truncate font-mono text-xs text-muted-foreground">{invoice.po_number}</span>
                      </span>
                      <span className="min-w-[92px] text-right">
                        <span className="block text-sm tabular-nums">{money(invoice.amount)}</span>
                        <span className={cn("mt-1 block text-xs capitalize", statusTone(invoice.status))}>
                          {invoice.status.replaceAll("_", " ")}
                        </span>
                        <span className="mt-1 block text-xs text-muted-foreground">{invoice.erp}</span>
                      </span>
                    </button>
                  ))}
                </div>

                <div className="hidden overflow-x-auto md:block">
                  <table className="w-full text-left text-sm">
                    <thead className="text-xs text-muted-foreground">
                      <tr>
                        <th className="px-2 py-2 font-medium">Invoice</th>
                        <th className="px-2 py-2 font-medium">Vendor</th>
                        <th className="px-2 py-2 font-medium">PO</th>
                        <th className="px-2 py-2 font-medium">Amount</th>
                        <th className="px-2 py-2 font-medium">ERP</th>
                        <th className="px-2 py-2 font-medium">State</th>
                        <th className="w-7" />
                      </tr>
                    </thead>
                    <tbody>
                      {overview.invoices.map((invoice) => (
                        <tr
                          key={invoice.id}
                          onClick={() => selectInvoice(invoice)}
                          onKeyDown={(event) => {
                            if (event.key === "Enter" || event.key === " ") {
                              event.preventDefault();
                              selectInvoice(invoice);
                            }
                          }}
                          role="button"
                          tabIndex={0}
                          className={cn(
                            "cursor-pointer border-t outline-none transition hover:bg-secondary/50 focus-visible:bg-secondary focus-visible:ring-2 focus-visible:ring-inset focus-visible:ring-ring",
                            invoice.id === selectedInvoice?.id && "bg-secondary/70"
                          )}
                        >
                          <td className="px-2 py-3 font-mono text-xs font-medium">{invoice.invoice_number}</td>
                          <td className="px-2 py-3">{invoice.vendor}</td>
                          <td className="px-2 py-3 font-mono text-xs text-muted-foreground">{invoice.po_number}</td>
                          <td className="px-2 py-3 tabular-nums">{money(invoice.amount)}</td>
                          <td className="px-2 py-3 text-muted-foreground">{invoice.erp}</td>
                          <td className={cn("px-2 py-3 text-xs capitalize", statusTone(invoice.status))}>
                            {invoice.status.replaceAll("_", " ")}
                          </td>
                          <td className="pr-1">
                            <ChevronRight className="h-4 w-4 text-muted-foreground" />
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </>
            )}

            {view === "exceptions" && (
              <div>
                {overview.exceptions.map((item) => (
                  <div key={item.id} className="grid gap-2 border-b px-2 py-4 sm:grid-cols-[100px_1fr_130px]">
                    <div className="flex items-start gap-2 text-xs font-medium text-amber-700">
                      <AlertTriangle className="h-4 w-4 shrink-0" />
                      {item.severity}
                    </div>
                    <div>
                      <div className="text-sm">{item.summary}</div>
                      <div className="mt-1 text-xs text-muted-foreground">{item.next_action}</div>
                    </div>
                    <div className="text-xs text-muted-foreground sm:text-right">{item.owner}</div>
                  </div>
                ))}
              </div>
            )}

            {view === "agents" && (
              <div>
                {overview.agents.map((agent) => (
                  <div key={agent.name} className="grid gap-2 border-b px-2 py-3 sm:grid-cols-[180px_1fr_80px]">
                    <div className="flex items-center gap-2 text-sm font-medium">
                      <span className={cn("h-1.5 w-1.5 rounded-full", agent.status === "online" ? "bg-emerald-500" : "bg-amber-500")} />
                      {agent.name}
                    </div>
                    <div className="text-xs leading-5 text-muted-foreground">{agent.focus}</div>
                    <div className="text-xs text-muted-foreground sm:text-right">{agent.last_run}</div>
                  </div>
                ))}
              </div>
            )}

            {agentBrief && (
              <div className="border-t px-2 py-4">
                <div className="mb-2 flex items-center gap-2 text-xs text-muted-foreground">
                  <Bot className="h-3.5 w-3.5" />
                  Finance brief
                </div>
                <div className="text-sm font-medium">{agentBrief.title}</div>
                <p className="mt-2 text-sm leading-6 text-muted-foreground">{agentBrief.summary}</p>
                <div className="mt-4 grid gap-4 sm:grid-cols-2">
                  <BriefList label="Signals" items={agentBrief.signals} />
                  <BriefList label="Next actions" items={agentBrief.actions} />
                </div>
              </div>
            )}
          </section>

          <aside className="border-t py-4 lg:border-l lg:border-t-0 lg:pl-5">
            {selectedInvoice && (
              <>
                <div className="flex items-start justify-between gap-3">
                  <div>
                    <div className="font-mono text-xs text-muted-foreground">{selectedInvoice.invoice_number}</div>
                    <div className="mt-1 text-base font-medium">{selectedInvoice.vendor}</div>
                  </div>
                  <div className={cn("text-xs capitalize", statusTone(selectedInvoice.status))}>
                    {selectedInvoice.status.replaceAll("_", " ")}
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-y-4 border-b py-5 text-sm">
                  <Data label="Amount" value={money(selectedInvoice.amount)} />
                  <Data label="Confidence" value={`${Math.round(selectedInvoice.confidence * 100)}%`} />
                  <Data label="Purchase order" value={selectedInvoice.po_number} mono />
                  <Data label="Match" value={selectedInvoice.match_type} />
                  <Data label="Due" value={selectedInvoice.due_date} />
                  <Data label="Target" value={selectedInvoice.erp} />
                </div>

                <div className="border-b py-5">
                  <div className="mb-3 flex items-center justify-between">
                    <span className="text-xs text-muted-foreground">Policy score</span>
                    <span className="font-mono text-sm font-medium">{matching?.score ?? "..."}</span>
                  </div>
                  <Progress value={matching?.score || 0} className="mb-4 h-1" />
                  <div className="space-y-2.5">
                    {(matching?.checks || []).map((check) => (
                      <div key={check.name} className="flex items-center justify-between gap-3 text-xs">
                        <span className="text-muted-foreground">{check.name}</span>
                        {check.status === "passed" ? (
                          <Check className="h-4 w-4 text-emerald-600" aria-label="Passed" />
                        ) : (
                          <CircleAlert className="h-4 w-4 text-amber-600" aria-label="Failed" />
                        )}
                      </div>
                    ))}
                  </div>
                </div>

                <div className="py-5">
                  <div className="text-sm font-medium">{matching?.recommendation || "Analyzing invoice"}</div>
                  {!!matching?.exceptions.length && (
                    <div className="mt-2 text-xs leading-5 text-amber-800">{matching.exceptions[0].message}</div>
                  )}
                  <div className="mt-4 text-xs leading-5 text-muted-foreground">
                    AI may recommend and draft. Exceptions require human approval before posting.
                  </div>
                </div>
              </>
            )}
          </aside>
        </div>
      </div>
    </main>
  );
}

function Metric({ label, value }: { label: string; value: string }) {
  return (
    <div className="border-l px-3 first:border-l-0 sm:px-4">
      <div className="text-xs text-muted-foreground">{label}</div>
      <div className="mt-1 font-mono text-lg font-medium tabular-nums">{value}</div>
    </div>
  );
}

function Data({ label, mono, value }: { label: string; mono?: boolean; value: string }) {
  return (
    <div className="min-w-0">
      <div className="text-xs text-muted-foreground">{label}</div>
      <div className={cn("mt-1 break-words text-sm", mono && "font-mono text-xs")}>{value}</div>
    </div>
  );
}

function BriefList({ items, label }: { items: string[]; label: string }) {
  return (
    <div className="min-w-0">
      <div className="mb-2 text-xs text-muted-foreground">{label}</div>
      <ul className="space-y-2 text-sm leading-5">
        {items.map((item) => (
          <li key={item} className="grid grid-cols-[14px_minmax(0,1fr)] gap-2">
            <span className="mt-2 h-1.5 w-1.5 rounded-full bg-primary/70" />
            <span className="min-w-0 break-words">{item}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}
