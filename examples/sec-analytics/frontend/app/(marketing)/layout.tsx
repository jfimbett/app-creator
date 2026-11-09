/** Layout of the landing page at /. Replaced by the full landing header and footer in slice 6.4. */
export default function MarketingLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <main id="main" className="mx-auto w-full max-w-[1440px] px-4 py-4">
      {children}
    </main>
  );
}
