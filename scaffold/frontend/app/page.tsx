import { HealthStatus } from "@/components/HealthStatus";
import { APP_NAME } from "@/lib/site";

export default function Home() {
  return (
    <main className="mx-auto flex min-h-screen max-w-2xl flex-col gap-6 px-6 py-12">
      <header>
        <h1 className="text-3xl font-bold tracking-tight">{APP_NAME}</h1>
        <p className="mt-2 text-[var(--muted)]">
          A working skeleton: this page (Next.js) talks to the backend (FastAPI) through <code>/api</code>.
        </p>
      </header>
      <HealthStatus />
    </main>
  );
}
