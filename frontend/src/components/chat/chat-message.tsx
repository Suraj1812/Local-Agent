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
          "max-w-[min(760px,90%)] rounded-lg border px-4 py-3 text-sm leading-6",
          isUser ? "bg-primary text-primary-foreground" : "bg-card"
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
