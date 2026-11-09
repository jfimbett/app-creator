import { AppShell } from "@/components/AppShell";

/** Layout of the app screens (/app, /companies/..., /compare): the app header and main area. */
export default function AppLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <AppShell>{children}</AppShell>;
}
