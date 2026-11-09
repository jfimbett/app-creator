import { LandingFooter } from "@/components/landing/LandingFooter";
import { LandingHeader } from "@/components/landing/LandingHeader";

/**
 * Layout of the landing page at /: its own header and footer, sharing the theme and tokens with the app.
 * Static: it makes no backend call, so it renders even when the backend is down.
 */
export default function MarketingLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <>
      <LandingHeader />
      <main id="main">{children}</main>
      <LandingFooter />
    </>
  );
}
