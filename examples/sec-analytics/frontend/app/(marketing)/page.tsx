import type { Metadata } from "next";

import { About } from "@/components/landing/About";
import { Faq } from "@/components/landing/Faq";
import { Features } from "@/components/landing/Features";
import { Hero } from "@/components/landing/Hero";
import { FinalCta } from "@/components/landing/LandingFooter";
import { HowItWorks } from "@/components/landing/HowItWorks";
import { Pricing } from "@/components/landing/Pricing";
import { Testimonials } from "@/components/landing/Testimonials";

const TITLE = "SEC Analytics: understand public companies from their SEC filings";
const DESCRIPTION =
  "Ten years of figures with their sources, the filings themselves, comparisons of up to four companies and an optional AI analyst. Uses public SEC EDGAR data; a teaching app.";

export const metadata: Metadata = {
  title: TITLE,
  description: DESCRIPTION,
  openGraph: { title: TITLE, description: DESCRIPTION, type: "website" },
};

/** The landing page (owner decision O2). Fictional and illustrative content is labelled where it appears. */
export default function Landing() {
  return (
    <>
      <Hero />
      <Features />
      <HowItWorks />
      <Testimonials />
      <Pricing />
      <About />
      <Faq />
      <FinalCta />
    </>
  );
}
