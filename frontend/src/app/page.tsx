import { AppShell } from "@/components/layout/app-shell";
import { APCommandCenter } from "@/components/ap/ap-command-center";

export default function Home() {
  return (
    <AppShell>
      <APCommandCenter />
    </AppShell>
  );
}
