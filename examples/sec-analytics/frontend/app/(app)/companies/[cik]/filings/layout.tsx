import type { Metadata } from "next";

/** Gives this screen its own browser tab title ("Filings · SEC Analytics"). */
export const metadata: Metadata = { title: "Filings" };

export default function Layout({ children }: Readonly<{ children: React.ReactNode }>) {
  return children;
}
