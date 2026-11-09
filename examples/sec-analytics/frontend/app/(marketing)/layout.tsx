import { ThemeToggle } from "@/components/ThemeToggle";

/** Layout of the landing page at /. Replaced by the full landing header and footer in slice 6.4. */
export default function MarketingLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <>
      <header className="mx-auto flex w-full max-w-[1440px] justify-end px-4 py-2">
        <ThemeToggle />
      </header>
      <main id="main" className="mx-auto w-full max-w-[1440px] px-4 py-4">
        {children}
      </main>
    </>
  );
}
