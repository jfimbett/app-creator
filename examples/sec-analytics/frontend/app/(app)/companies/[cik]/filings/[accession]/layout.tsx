import type { Metadata } from "next";

/** Gives this screen its own browser tab title ("Filing reader · SEC Analytics"). */
export const metadata: Metadata = { title: "Filing reader" };

export default function Layout({ children }: Readonly<{ children: React.ReactNode }>) {
  return children;
}
