import type { Metadata } from "next";

/** Gives this screen its own browser tab title ("Home · SEC Analytics"). */
export const metadata: Metadata = { title: "Home" };

export default function Layout({ children }: Readonly<{ children: React.ReactNode }>) {
  return children;
}
