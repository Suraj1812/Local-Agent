"use client";

import { Save } from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Select } from "@/components/ui/select";
import { Switch } from "@/components/ui/switch";
import { useAppStore } from "@/store/app-store";

export function SettingsView() {
  const settings = useAppStore((state) => state.settings);
  const loadInitial = useAppStore((state) => state.loadInitial);
  const saveSettings = useAppStore((state) => state.saveSettings);
  const [draft, setDraft] = useState(settings);

  useEffect(() => {
    loadInitial().catch(() => undefined);
  }, [loadInitial]);

  useEffect(() => {
    setDraft(settings);
  }, [settings]);

  const tools = useMemo(() => Object.entries(draft?.tools_enabled || {}), [draft]);
  const agents = useMemo(() => Object.entries(draft?.agent_config || {}), [draft]);

  if (!draft) {
    return <div className="p-6 text-sm text-muted-foreground">Loading settings...</div>;
  }

  return (
    <div className="h-screen overflow-auto p-4 md:p-6">
      <div className="mb-5 flex items-center justify-between gap-3">
        <div>
          <h1 className="text-xl font-semibold">Settings</h1>
          <p className="text-sm text-muted-foreground">Model, memory, tools, and agents</p>
        </div>
        <Button onClick={() => saveSettings(draft)}>
          <Save className="h-4 w-4" />
          Save
        </Button>
      </div>
      <div className="grid gap-4 xl:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Model</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <label className="grid gap-2 text-sm">
              <span className="text-muted-foreground">Ollama model</span>
              <Select value={draft.model} onChange={(event) => setDraft({ ...draft, model: event.target.value })}>
                {draft.supported_models.map((model) => (
                  <option key={model} value={model}>
                    {model}
                  </option>
                ))}
              </Select>
            </label>
            <label className="grid gap-2 text-sm">
              <span className="text-muted-foreground">Temperature</span>
              <Input
                type="number"
                min={0}
                max={1}
                step={0.05}
                value={draft.temperature}
                onChange={(event) => setDraft({ ...draft, temperature: Number(event.target.value) })}
              />
            </label>
            <label className="grid gap-2 text-sm">
              <span className="text-muted-foreground">Memory limit</span>
              <Input
                type="number"
                min={5}
                max={100}
                value={draft.memory_limit}
                onChange={(event) => setDraft({ ...draft, memory_limit: Number(event.target.value) })}
              />
            </label>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>Tools</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {tools.map(([name, enabled]) => (
              <div key={name} className="flex items-center justify-between rounded-md border bg-background p-3">
                <span className="text-sm capitalize">{name}</span>
                <Switch
                  label={`${name} tool`}
                  checked={enabled}
                  onCheckedChange={(checked) =>
                    setDraft({
                      ...draft,
                      tools_enabled: { ...draft.tools_enabled, [name]: checked }
                    })
                  }
                />
              </div>
            ))}
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>Agents</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {agents.map(([name, enabled]) => (
              <div key={name} className="flex items-center justify-between rounded-md border bg-background p-3">
                <span className="text-sm capitalize">{name}</span>
                <Switch
                  label={`${name} agent`}
                  checked={enabled}
                  onCheckedChange={(checked) =>
                    setDraft({
                      ...draft,
                      agent_config: { ...draft.agent_config, [name]: checked }
                    })
                  }
                />
              </div>
            ))}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
