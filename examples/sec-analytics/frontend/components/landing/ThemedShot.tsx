import Image from "next/image";

type ThemedShotProps = {
  /** File name stem in public/landing/: `<stem>-dark.png` and `<stem>-light.png`. */
  stem: string;
  alt: string;
  width: number;
  height: number;
  sizes: string;
  /** Load both theme variants at once (above the fold), since either may be the visible one. */
  eager?: boolean;
  className?: string;
};

/**
 * A real screenshot of the app (captured by scripts/capture-landing-shots.ts) in the theme that matches the page.
 * Both images are in the HTML; CSS shows the one for <html data-theme>, so the swap needs no JavaScript.
 */
export function ThemedShot({ stem, alt, width, height, sizes, eager = false, className = "" }: ThemedShotProps) {
  const common = { width, height, sizes, className: `h-auto w-full ${className}` };
  return (
    <>
      <Image src={`/landing/${stem}-dark.png`} alt={alt} loading={eager ? "eager" : "lazy"} {...common} className={`${common.className} in-data-[theme=light]:hidden`} />
      <Image src={`/landing/${stem}-light.png`} alt={alt} loading={eager ? "eager" : "lazy"} {...common} className={`${common.className} hidden in-data-[theme=light]:block`} />
    </>
  );
}
