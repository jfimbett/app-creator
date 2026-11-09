import type { Metadata } from "next";

/** Gives this screen its own browser tab title ("Company overview · SEC Analytics"). */
export const metadata: Metadata = { title: "Company overview" };

export default function Layout({ children }: Readonly<{ children: React.ReactNode }>) {
  return children;
}
