import { AppShell } from "@/components/layout/app-shell";
import { ChatWorkspace } from "@/components/chat/chat-workspace";

export default function Home() {
  return (
    <AppShell>
      <ChatWorkspace />
    </AppShell>
  );
}
