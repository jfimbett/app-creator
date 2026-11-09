import type { Metadata } from "next";

/** Gives this screen its own browser tab title ("Compare companies · SEC Analytics"). */
export const metadata: Metadata = { title: "Compare companies" };

export default function Layout({ children }: Readonly<{ children: React.ReactNode }>) {
  return children;
}
