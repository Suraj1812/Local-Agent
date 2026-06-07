"use client";

import { Upload } from "lucide-react";
import { ChangeEvent, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useAppStore } from "@/store/app-store";

export function KnowledgeView() {
  const documents = useAppStore((state) => state.documents);
  const loadKnowledge = useAppStore((state) => state.loadKnowledge);
  const uploadDocument = useAppStore((state) => state.uploadDocument);

  useEffect(() => {
    loadKnowledge().catch(() => undefined);
  }, [loadKnowledge]);

  async function onFile(event: ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];
    if (!file) return;
    await uploadDocument(file);
    event.target.value = "";
  }

  return (
    <div className="h-screen overflow-auto p-4 md:p-6">
      <div className="mb-5 flex items-center justify-between gap-3">
        <div>
          <h1 className="text-xl font-semibold">Knowledge</h1>
          <p className="text-sm text-muted-foreground">Local documents and retrieval chunks</p>
        </div>
        <Button asChild>
          <label>
            <Upload className="h-4 w-4" />
            Upload
            <input
              type="file"
              accept=".pdf,.txt,.md,.docx"
              className="hidden"
              onChange={onFile}
            />
          </label>
        </Button>
      </div>
      <Card>
        <CardHeader>
          <CardTitle>Documents</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="divide-y rounded-md border">
            {documents.map((document) => (
              <div key={document.id} className="grid gap-2 p-3 text-sm md:grid-cols-[minmax(0,1fr)_120px_100px]">
                <div className="min-w-0 truncate">{document.filename}</div>
                <div className="text-muted-foreground">{document.mime_type}</div>
                <div className="font-mono text-muted-foreground">{document.chunks} chunks</div>
              </div>
            ))}
            {!documents.length && <div className="p-4 text-sm text-muted-foreground">No documents uploaded</div>}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
