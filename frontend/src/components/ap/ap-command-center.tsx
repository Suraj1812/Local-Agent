"use client";

import { ChangeEvent, ComponentType, FormEvent, useEffect, useMemo, useRef, useState } from "react";
import {
  Activity,
  AlertTriangle,
  BarChart3,
  Bot,
  CheckCircle2,
  Clock3,
  Database,
  FileCheck2,
  FileText,
  Link2,
  Loader2,
  ShieldCheck,
  UploadCloud
} from "lucide-react";
import { api } from "@/lib/api";
import type { APMatchingResult, APOverview } from "@/lib/types";
import { cn } from "@/lib/utils";
import { useAppStore } from "@/store/app-store";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";

const pipeline = [
  "Invoice intake",
  "OCR extraction",
  "2/3-way match",
  "Exception routing",
  "Approval policy",
  "ERP posting"
];

function money(value: number) {
  return new Intl.NumberFormat("en-US", { currency: "USD", maximumFractionDigits: 0, style: "currency" }).format(value);
}

function percent(value: number) {
  return `${value.toFixed(1)}%`;
}

function statusTone(status: string) {
  if (["matched", "ready_to_post", "online", "posted", "auto_approved"].includes(status)) {
    return "border-emerald-200 bg-emerald-50 text-emerald-700";
  }
  if (["exception", "reviewing", "draft"].includes(status)) {
    return "border-amber-200 bg-amber-50 text-amber-700";
  }
  return "border-slate-200 bg-slate-50 text-slate-600";
}

export function APCommandCenter() {
  const [overview, setOverview] = useState<APOverview | null>(null);
  const [matching, setMatching] = useState<APMatchingResult | null>(null);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [prompt, setPrompt] = useState("");
  const inputRef = useRef<HTMLInputElement>(null);
  const sendGoal = useAppStore((state) => state.sendGoal);
  const isRunning = useAppStore((state) => state.isRunning);
  const conversation = useAppStore((state) => state.activeConversation);

  useEffect(() => {
    let ignore = false;
    async function load() {
      try {
        const [overviewPayload, matchingPayload] = await Promise.all([
          api.apOverview(),
          api.runAPMatching({ invoice_number: "AP-DEMO-NEW", po_number: "PO-88022", amount: 41720, vendor_id: "ven-1017" })
        ]);
        if (!ignore) {
          setOverview(overviewPayload);
          setMatching(matchingPayload);
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

  const latestAnswer = useMemo(
    () => [...(conversation?.messages || [])].reverse().find((message) => message.role === "assistant")?.content,
    [conversation]
  );

  async function handleUpload(event: ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];
    if (!file) {
      return;
    }
    setUploading(true);
    try {
      await api.uploadDocument(file);
      window.alert("Invoice document captured for extraction.");
    } catch (error) {
      window.alert(error instanceof Error ? error.message : "Upload failed");
    } finally {
      setUploading(false);
      event.target.value = "";
    }
  }

  async function runMatchingDemo() {
    setMatching(null);
    setMatching(await api.runAPMatching({ invoice_number: "AP-DEMO-NEW", po_number: "PO-88022", amount: 41720, vendor_id: "ven-1017" }));
  }

  async function askAgent(event: FormEvent) {
    event.preventDefault();
    const clean = prompt.trim();
    if (!clean || isRunning) {
      return;
    }
    setPrompt("");
    await sendGoal(`Accounts payable finance agent task: ${clean}`);
  }

  if (loading || !overview) {
    return (
      <div className="grid min-h-screen place-items-center bg-background text-sm text-muted-foreground">
        <div className="flex items-center gap-2">
          <Loader2 className="h-4 w-4 animate-spin" />
          Loading AP control plane
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen overflow-x-hidden bg-background text-foreground">
      <header className="sticky top-0 z-10 border-b bg-card/95 backdrop-blur">
        <div className="mx-auto flex max-w-7xl flex-wrap items-center justify-between gap-3 px-4 py-3 md:px-6">
          <div className="flex items-center gap-3">
            <div className="flex h-9 w-9 items-center justify-center rounded-md bg-primary text-primary-foreground">
              <FileCheck2 className="h-5 w-5" />
            </div>
            <div>
              <div className="text-sm font-semibold">FirstAI AP</div>
              <div className="text-xs text-muted-foreground">Autonomous finance execution</div>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <input ref={inputRef} type="file" className="hidden" onChange={handleUpload} />
            <Button variant="outline" onClick={() => inputRef.current?.click()} disabled={uploading}>
              {uploading ? <Loader2 className="h-4 w-4 animate-spin" /> : <UploadCloud className="h-4 w-4" />}
              Upload invoice
            </Button>
            <Button onClick={runMatchingDemo}>
              <ShieldCheck className="h-4 w-4" />
              Run match
            </Button>
          </div>
        </div>
      </header>

      <main className="mx-auto grid min-w-0 max-w-7xl gap-4 px-4 py-4 md:px-6 lg:grid-cols-[minmax(0,1fr)_360px]">
        <section className="min-w-0 space-y-4">
          <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
            <Metric label="Invoice volume" value={overview.metrics.invoice_volume.toString()} detail="active AP queue" icon={FileText} />
            <Metric label="Payable exposure" value={money(overview.metrics.payable_exposure)} detail="pending liability" icon={Database} />
            <Metric label="Straight-through" value={percent(overview.metrics.straight_through_rate)} detail="no-touch rate" icon={Activity} />
            <Metric label="Match accuracy" value={percent(overview.metrics.match_accuracy)} detail="policy checked" icon={BarChart3} />
          </div>

          <div className="rounded-lg border bg-card p-4">
            <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
              <div>
                <h1 className="text-lg font-semibold">Invoice-to-ERP execution pipeline</h1>
                <p className="text-sm text-muted-foreground">Document intelligence, matching, exceptions, approvals, journals, and ERP sync.</p>
              </div>
              <div className="rounded-full border bg-background px-3 py-1 text-xs text-muted-foreground">
                SAP · NetSuite · Dynamics · QuickBooks
              </div>
            </div>
            <div className="grid gap-2 md:grid-cols-6">
              {pipeline.map((step, index) => (
                <div key={step} className="rounded-md border bg-background p-3">
                  <div className="mb-3 flex items-center justify-between text-xs text-muted-foreground">
                    <span>0{index + 1}</span>
                    {index < 3 ? <CheckCircle2 className="h-4 w-4 text-primary" /> : <Clock3 className="h-4 w-4 text-amber-600" />}
                  </div>
                  <div className="text-sm font-medium">{step}</div>
                </div>
              ))}
            </div>
          </div>

          <div className="grid gap-4 xl:grid-cols-[minmax(0,1.35fr)_minmax(320px,0.65fr)]">
            <div className="min-w-0 rounded-lg border bg-card">
              <div className="flex items-center justify-between border-b px-4 py-3">
                <div>
                  <h2 className="text-sm font-semibold">Invoice work queue</h2>
                  <p className="text-xs text-muted-foreground">Prioritized by due date, policy risk, and ERP readiness.</p>
                </div>
                <span className="text-xs text-muted-foreground">{overview.metrics.exceptions_open} exceptions</span>
              </div>
              <div className="overflow-x-auto">
                <table className="w-full min-w-[720px] text-left text-sm">
                  <thead className="border-b bg-secondary/60 text-xs text-muted-foreground">
                    <tr>
                      <th className="px-4 py-2 font-medium">Invoice</th>
                      <th className="px-4 py-2 font-medium">Vendor</th>
                      <th className="px-4 py-2 font-medium">Match</th>
                      <th className="px-4 py-2 font-medium">Amount</th>
                      <th className="px-4 py-2 font-medium">ERP</th>
                      <th className="px-4 py-2 font-medium">Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    {overview.invoices.map((invoice) => (
                      <tr key={invoice.id} className="border-b last:border-0">
                        <td className="px-4 py-3 font-medium">{invoice.invoice_number}</td>
                        <td className="px-4 py-3 text-muted-foreground">{invoice.vendor}</td>
                        <td className="px-4 py-3">{invoice.match_type}</td>
                        <td className="px-4 py-3">{money(invoice.amount)}</td>
                        <td className="px-4 py-3">{invoice.erp}</td>
                        <td className="px-4 py-3">
                          <span className={cn("rounded-full border px-2 py-1 text-xs", statusTone(invoice.status))}>
                            {invoice.status.replaceAll("_", " ")}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

            <div className="rounded-lg border bg-card p-4">
              <div className="mb-3 flex items-center gap-2">
                <AlertTriangle className="h-4 w-4 text-amber-600" />
                <h2 className="text-sm font-semibold">Exception center</h2>
              </div>
              <div className="space-y-3">
                {overview.exceptions.map((item) => (
                  <div key={item.id} className="rounded-md border bg-background p-3">
                    <div className="mb-2 flex items-center justify-between gap-2">
                      <span className={cn("rounded-full border px-2 py-1 text-xs", statusTone("exception"))}>
                        {item.severity}
                      </span>
                      <span className="text-xs text-muted-foreground">{item.owner}</span>
                    </div>
                    <div className="text-sm font-medium">{item.summary}</div>
                    <p className="mt-2 text-xs leading-5 text-muted-foreground">{item.next_action}</p>
                  </div>
                ))}
              </div>
            </div>
          </div>

          <div className="rounded-lg border bg-card p-4">
            <div className="mb-4 flex items-center justify-between">
              <div>
                <h2 className="text-sm font-semibold">Finance AI workforce</h2>
                <p className="text-xs text-muted-foreground">Specialized agents with deterministic policy constraints and audit traces.</p>
              </div>
              <Bot className="h-4 w-4 text-primary" />
            </div>
            <div className="grid gap-3 md:grid-cols-3">
              {overview.agents.map((agent) => (
                <div key={agent.name} className="rounded-md border bg-background p-3">
                  <div className="mb-2 flex items-center justify-between gap-2">
                    <div className="text-sm font-medium">{agent.name}</div>
                    <span className={cn("rounded-full border px-2 py-0.5 text-xs", statusTone(agent.status))}>
                      {agent.status}
                    </span>
                  </div>
                  <p className="min-h-12 text-xs leading-5 text-muted-foreground">{agent.focus}</p>
                  <div className="mt-3 text-xs text-muted-foreground">{agent.last_run}</div>
                </div>
              ))}
            </div>
          </div>
        </section>

        <aside className="min-w-0 space-y-4">
          <div className="rounded-lg border bg-card p-4">
            <div className="mb-3 flex items-center justify-between">
              <h2 className="text-sm font-semibold">3-way matching result</h2>
              <span className={cn("rounded-full border px-2 py-1 text-xs", statusTone(matching?.status || ""))}>
                {matching?.status?.replaceAll("_", " ") || "running"}
              </span>
            </div>
            <Progress value={matching?.score || 0} className="mb-3 h-1.5" />
            <div className="mb-3 text-3xl font-semibold">{matching?.score || 0}</div>
            <div className="space-y-2">
              {(matching?.checks || []).map((check) => (
                <div key={check.name} className="flex items-center justify-between gap-2 text-sm">
                  <span className="text-muted-foreground">{check.name}</span>
                  <span className={check.status === "passed" ? "text-primary" : "text-amber-700"}>{check.status}</span>
                </div>
              ))}
            </div>
            {!!matching?.exceptions.length && (
              <div className="mt-3 rounded-md border border-amber-200 bg-amber-50 p-3 text-xs leading-5 text-amber-800">
                {matching.exceptions[0].message}
              </div>
            )}
            {matching?.recommendation && (
              <div className="mt-3 rounded-md border bg-background p-3 text-sm">
                <span className="text-muted-foreground">Recommendation: </span>
                <span className="font-medium">{matching.recommendation}</span>
              </div>
            )}
          </div>

          <div className="rounded-lg border bg-card p-4">
            <div className="mb-3 flex items-center gap-2">
              <Link2 className="h-4 w-4 text-primary" />
              <h2 className="text-sm font-semibold">ERP sync</h2>
            </div>
            <div className="space-y-3">
              {overview.systems.map((system) => (
                <div key={system} className="flex items-center justify-between rounded-md border bg-background px-3 py-2 text-sm">
                  <span>{system}</span>
                  <span className="text-xs text-muted-foreground">connector ready</span>
                </div>
              ))}
            </div>
          </div>

          <div className="rounded-lg border bg-card p-4">
            <div className="mb-3 flex items-center gap-2">
              <Database className="h-4 w-4 text-primary" />
              <h2 className="text-sm font-semibold">Journal preview</h2>
            </div>
            {overview.journal_entries.map((entry) => (
              <div key={entry.id} className="mb-3 rounded-md border bg-background p-3 last:mb-0">
                <div className="mb-2 flex items-center justify-between text-xs">
                  <span className="font-medium">{entry.erp}</span>
                  <span className={cn("rounded-full border px-2 py-0.5", statusTone(entry.status))}>{entry.status}</span>
                </div>
                {entry.lines.map((line) => (
                  <div key={`${entry.id}-${line.account}`} className="flex justify-between text-xs text-muted-foreground">
                    <span>GL {line.account}</span>
                    <span>{money(line.debit || line.credit)}</span>
                  </div>
                ))}
              </div>
            ))}
          </div>

          <div className="rounded-lg border bg-card p-4">
            <div className="mb-3 flex items-center gap-2">
              <Bot className="h-4 w-4 text-primary" />
              <h2 className="text-sm font-semibold">Finance agent</h2>
            </div>
            <form onSubmit={askAgent} className="flex gap-2">
              <input
                value={prompt}
                onChange={(event) => setPrompt(event.target.value)}
                placeholder="Ask about AP risk"
                className="min-w-0 flex-1 rounded-md border bg-background px-3 py-2 text-sm outline-none focus:border-primary focus:ring-2 focus:ring-primary/15"
              />
              <Button type="submit" size="icon" disabled={isRunning || !prompt.trim()} aria-label="Ask finance agent">
                {isRunning ? <Loader2 className="h-4 w-4 animate-spin" /> : <Bot className="h-4 w-4" />}
              </Button>
            </form>
            {latestAnswer && (
              <div className="mt-3 max-h-40 overflow-auto rounded-md border bg-background p-3 text-xs leading-5 text-muted-foreground">
                {latestAnswer}
              </div>
            )}
          </div>
        </aside>
      </main>
    </div>
  );
}

function Metric({
  detail,
  icon: Icon,
  label,
  value
}: {
  detail: string;
  icon: ComponentType<{ className?: string }>;
  label: string;
  value: string;
}) {
  return (
    <div className="rounded-lg border bg-card p-4">
      <div className="mb-3 flex items-center justify-between">
        <span className="text-xs font-medium text-muted-foreground">{label}</span>
        <Icon className="h-4 w-4 text-primary" />
      </div>
      <div className="text-2xl font-semibold">{value}</div>
      <div className="mt-1 text-xs text-muted-foreground">{detail}</div>
    </div>
  );
}
