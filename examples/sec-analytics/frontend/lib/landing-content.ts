// Landing page content (M6, brief §4.3). Typed constants so lib/landing-content.test.ts can check the honesty
// rules of brief §6: fictional content labelled where it appears, no invented statistics, no real people or firms,
// pricing that never charges anyone, example.com addresses only. Feature claims match what the app does at m5.

export const REPO_URL = "https://github.com/jfimbett/app-creator";

export const HEADLINE = "Understand public companies from their SEC filings";
export const SUBHEADLINE =
  "Search a company, read ten years of figures with the filing each number came from, open the 10-K itself, and compare up to four companies side by side.";

export const DISCLAIMER =
  "SEC Analytics is not affiliated with or endorsed by the U.S. Securities and Exchange Commission. It uses public SEC EDGAR data and is not investment advice.";

export const REVIEWS_LABEL = "Fictional testimonials written for this teaching demo.";
export const PRICING_NOTE = "Prices are illustrative. This teaching app has no accounts and takes no payments.";
export const ABOUT_LABEL = "SEC Analytics and its team are fictional, created for a programming course.";

export const LANDING_NAV = [
  { href: "#features", label: "Features" },
  { href: "#reviews", label: "Reviews" },
  { href: "#pricing", label: "Pricing" },
  { href: "#about", label: "About" },
  { href: "#faq", label: "FAQ" },
] as const;

export type FeatureIcon = "search" | "table" | "document" | "compare" | "spark" | "offline";

export const FEATURES: { icon: FeatureIcon; title: string; body: string }[] = [
  {
    icon: "search",
    title: "Find any SEC filer",
    body: "Search by company name, ticker or CIK, with keyboard shortcuts (/ or Ctrl K) and a list you can move through with the arrow keys.",
  },
  {
    icon: "table",
    title: "Ten years of figures, with sources",
    body: "Income statement, balance sheet, cash flow and ratios by fiscal year. Each number shows its SEC concept, period, form and accession, and derived values show their formula.",
  },
  {
    icon: "document",
    title: "Read the filing itself",
    body: "Open a 10-K or 10-Q as clean text with a section list and search inside the document, plus a link to the original on sec.gov.",
  },
  {
    icon: "compare",
    title: "Compare up to four companies",
    body: "Put companies side by side on their own fiscal years, index money metrics to 100 at the first common year, and export exactly what you see as CSV.",
  },
  {
    icon: "spark",
    title: "An optional AI analyst",
    body: "Ask questions about the loaded figures and filing passages with your own OpenRouter key. Every answer lists checked source chips that link back to the data.",
  },
  {
    icon: "offline",
    title: "Demo mode works offline",
    body: "A recorded snapshot of SEC data for three companies ships with the app, so a classroom can use it with no network and no keys.",
  },
];

export const HOW_IT_WORKS = [
  { title: "Search a company", body: "Type a name, ticker or CIK, or start with one of the demo companies." },
  { title: "Read the figures and filings", body: "Check the key figures and charts, hover a value for its source, and open the 10-K behind it." },
  { title: "Compare and ask", body: "Line companies up on the same metrics, export the table, and ask the analyst with your own key." },
] as const;

export type Testimonial = { name: string; initials: string; role: string; organisation?: string; quote: string; stars?: number };

export const TESTIMONIALS: Testimonial[] = [
  {
    name: "Maya Okafor",
    initials: "MO",
    role: "Finance student",
    organisation: "Riverbend College (fictional)",
    quote: "I stopped copying numbers out of 10-Ks by hand. Hovering a value and seeing the exact filing it came from changed how I write my case studies.",
    stars: 5,
  },
  {
    name: "Tomás Lindqvist",
    initials: "TL",
    role: "Teaching assistant, corporate finance",
    quote: "Demo mode is the reason I use it in tutorials: forty laptops, one weak Wi-Fi network, and every student still sees the same figures.",
    stars: 5,
  },
  {
    name: "Priya Raman",
    initials: "PR",
    role: "Equity research intern",
    organisation: "Northgate Partners (fictional)",
    quote: "The comparison view keeps each company on its own fiscal year and says so. That small honesty saves me from a lot of wrong charts.",
    stars: 4,
  },
  {
    name: "Daniel Achterberg",
    initials: "DA",
    role: "Accounting student",
    quote: "When a line is missing it says why instead of showing a zero. I learned more about XBRL concepts from those notes than from the textbook.",
    stars: 5,
  },
  {
    name: "Lena Moreau",
    initials: "LM",
    role: "Instructor, financial statement analysis",
    organisation: "Harbor School of Business (fictional)",
    quote: "The analyst's source chips are a good teaching tool: students check the cited figure before they trust the sentence.",
    stars: 4,
  },
  {
    name: "Kwame Asante",
    initials: "KA",
    role: "MBA student",
    quote: "Exporting the comparison as CSV gave me exactly the rows on screen, with empty cells where data was missing. My spreadsheet finally matched the source.",
  },
];

export type PricingTier = {
  name: string;
  price: string;
  period: string;
  summary: string;
  features: string[];
  cta: { label: string; href: string };
  highlighted?: boolean;
};

export const PRICING_TIERS: PricingTier[] = [
  {
    name: "Student",
    price: "$0",
    period: "forever",
    summary: "Everything the app does today.",
    features: ["Demo and Live SEC data", "Statements, ratios and the filings reader", "Compare up to four companies, CSV export", "AI analyst with your own key"],
    cta: { label: "Start with the demo", href: "/app" },
  },
  {
    name: "Team",
    price: "$12",
    period: "per member per month",
    summary: "For study groups and project teams.",
    features: ["Everything in Student", "Shared workspaces (illustrative)", "Saved comparisons for the group (illustrative)"],
    cta: { label: "Open the app", href: "/app" },
    highlighted: true,
  },
  {
    name: "Classroom",
    price: "$299",
    period: "per term",
    summary: "For a course with an instructor.",
    features: ["Everything in Team", "Instructor features (illustrative)", "Recorded demo snapshot for offline lessons"],
    cta: { label: "Read the FAQ", href: "#faq" },
  },
];

export const ABOUT = {
  story: [
    "SEC Analytics started as a small tool for a corporate finance course: students kept asking where a number in a spreadsheet really came from. The answer was always the same — a filing on SEC EDGAR — so the team built an app that keeps every number next to its source.",
    "Public companies in the United States file their annual and quarterly reports with the SEC, and those filings are free for anyone to read. The data is rich but hard to use. SEC Analytics turns it into clear tables, charts and comparisons without hiding where it came from.",
  ],
  values: [
    { title: "Numbers with their sources", body: "Every figure links to its concept, period and filing." },
    { title: "Missing means missing", body: "A gap is explained, never filled with a zero or a guess." },
    { title: "Works in a classroom", body: "Offline demo data, keyboard friendly, readable in both themes." },
  ],
  team: [
    { name: "Ines Carvalho", initials: "IC", role: "Product and data" },
    { name: "Samuel Brandt", initials: "SB", role: "Frontend and design" },
    { name: "Aiko Nakamura", initials: "AN", role: "Backend and SEC data" },
    { name: "Rafael Quint", initials: "RQ", role: "Teaching and support" },
  ],
  city: "Lakeport (a fictional city)",
  contact: "hello@example.com",
};

export const FAQ = [
  {
    question: "Where does the data come from?",
    answer:
      "From public SEC EDGAR: Company Facts (XBRL), company submissions and the filing documents. In Demo mode the app uses a recorded snapshot of that data for three companies, so it works offline; in Live mode the backend fetches from SEC directly, within SEC's fair-access limits.",
  },
  {
    question: "Is this investment advice?",
    answer: "No. SEC Analytics shows what companies reported to the SEC. It does not show market prices or valuations and it does not recommend anything.",
  },
  {
    question: "Does the AI analyst need a key?",
    answer:
      "Yes, your own OpenRouter key, and it is optional: everything else works without it. The key stays in the page's memory unless you choose to keep it for the current tab, and it is sent only with your own questions, through this app's backend, to OpenRouter.",
  },
  {
    question: "Is SEC Analytics affiliated with the SEC?",
    answer: "No. It is not affiliated with or endorsed by the U.S. Securities and Exchange Commission. It only reads data the SEC publishes for everyone.",
  },
  {
    question: "Does it store my data?",
    answer:
      "There are no accounts. The app remembers only your colour theme in this browser. The AI key stays in memory unless you opt in to keep it for the tab, and it is never written to disk by the app.",
  },
] as const;
