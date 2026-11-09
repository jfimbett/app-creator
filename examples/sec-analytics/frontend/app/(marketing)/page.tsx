import Link from "next/link";

/** Landing page placeholder (slice 6.1); the full page arrives in slice 6.4. */
export default function Landing() {
  return (
    <section aria-labelledby="landing-title" className="flex flex-col gap-2">
      <h1 id="landing-title" className="text-heading font-semibold">
        SEC Analytics
      </h1>
      <p>
        <Link href="/app">Open the app</Link>
      </p>
    </section>
  );
}
