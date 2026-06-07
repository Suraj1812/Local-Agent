"use client";

import ReactMarkdown from "react-markdown";
import rehypeHighlight from "rehype-highlight";
import remarkGfm from "remark-gfm";
import type { Message } from "@/lib/types";
import { cn } from "@/lib/utils";

const hiddenNoise = [
  "ollama is not reachable",
  "fallback path",
  "agent plan completed",
  "result for:",
  "completed '",
  "tool context:",
  "plan:"
];

function cleanAssistantContent(content: string) {
  const lines: string[] = [];
  let inFence = false;
  let previousBlank = false;

  for (const rawLine of content.split(/\r?\n/)) {
    const trimmed = rawLine.trim();
    if (trimmed.startsWith("```")) {
      inFence = !inFence;
      lines.push(rawLine);
      previousBlank = false;
      continue;
    }

    if (!inFence) {
      const normalized = trimmed.toLowerCase();
      if (hiddenNoise.some((item) => normalized.includes(item))) {
        continue;
      }

      const cleaned = rawLine
        .replace(/^\s{0,3}#{1,6}\s*/, "")
        .replace(/\*\*/g, "")
        .replace(/__/g, "")
        .trimEnd();

      if (!cleaned.trim()) {
        if (!previousBlank && lines.length) {
          lines.push("");
        }
        previousBlank = true;
        continue;
      }

      lines.push(cleaned);
      previousBlank = false;
      continue;
    }

    lines.push(rawLine);
    previousBlank = false;
  }

  return lines.join("\n").trim();
}

export function ChatMessage({ message }: { message: Message }) {
  const isUser = message.role === "user";
  const content = isUser ? message.content : cleanAssistantContent(message.content);

  return (
    <article className={cn("flex w-full min-w-0", isUser ? "justify-end" : "justify-start")}>
      <div
        className={cn(
          "min-w-0 max-w-full break-words text-[15px] leading-7 md:max-w-[86%]",
          isUser
            ? "rounded-md bg-secondary px-3 py-2 text-foreground"
            : "prose prose-slate max-w-none px-0 py-1 text-foreground"
        )}
      >
        {isUser ? (
          <p className="whitespace-pre-wrap">{content}</p>
        ) : (
          <ReactMarkdown
            remarkPlugins={[remarkGfm]}
            rehypePlugins={[rehypeHighlight]}
            components={{
              h1: ({ children }) => <p className="mb-2 font-medium">{children}</p>,
              h2: ({ children }) => <p className="mb-2 font-medium">{children}</p>,
              h3: ({ children }) => <p className="mb-2 font-medium">{children}</p>,
              p: ({ children }) => <p className="mb-3 last:mb-0">{children}</p>,
              ul: ({ children }) => <ul className="mb-3 list-disc space-y-1 pl-5 last:mb-0">{children}</ul>,
              ol: ({ children }) => <ol className="mb-3 list-decimal space-y-1 pl-5 last:mb-0">{children}</ol>,
              a: ({ children, ...props }) => (
                <a className="text-primary underline underline-offset-2" target="_blank" rel="noreferrer" {...props}>
                  {children}
                </a>
              ),
              code: ({ children, className, ...props }) => (
                <code
                  className={cn("rounded bg-secondary px-1 py-0.5 font-mono text-[13px]", className)}
                  {...props}
                >
                  {children}
                </code>
              ),
              pre: ({ children, ...props }) => (
                <pre className="my-3 max-w-full overflow-x-auto rounded-md border bg-white p-3 text-xs" {...props}>
                  {children}
                </pre>
              )
            }}
          >
            {content}
          </ReactMarkdown>
        )}
      </div>
    </article>
  );
}
