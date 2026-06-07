"use client";

import ReactMarkdown from "react-markdown";
import rehypeHighlight from "rehype-highlight";
import remarkGfm from "remark-gfm";
import type { Message } from "@/lib/types";
import { cn } from "@/lib/utils";

export function ChatMessage({ message }: { message: Message }) {
  const isUser = message.role === "user";
  return (
    <article className={cn("flex", isUser ? "justify-end" : "justify-start")}>
      <div
        className={cn(
          "max-w-[min(760px,92%)] text-sm leading-6",
          isUser ? "rounded-lg bg-primary px-4 py-3 text-primary-foreground" : "px-1 py-2 text-foreground"
        )}
      >
        {isUser ? (
          <p className="whitespace-pre-wrap">{message.content}</p>
        ) : (
          <ReactMarkdown
            remarkPlugins={[remarkGfm]}
            rehypePlugins={[rehypeHighlight]}
            components={{
              a: ({ children, ...props }) => (
                <a className="text-primary underline" target="_blank" rel="noreferrer" {...props}>
                  {children}
                </a>
              ),
              code: ({ children, className, ...props }) => (
                <code className={cn("rounded bg-secondary px-1 py-0.5 font-mono text-xs", className)} {...props}>
                  {children}
                </code>
              ),
              pre: ({ children, ...props }) => (
                <pre className="my-3 overflow-x-auto rounded-lg border bg-card p-3 text-xs" {...props}>
                  {children}
                </pre>
              )
            }}
          >
            {message.content}
          </ReactMarkdown>
        )}
      </div>
    </article>
  );
}
