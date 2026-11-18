import type { Metadata } from "next";
import Link from "next/link";
import { Suspense } from "react";
import { Atkinson_Hyperlegible, Zilla_Slab } from "next/font/google";
import { StatusLine } from "@/components/status-line";
import "./globals.css";

// Atkinson Hyperlegible was designed for low vision, which also serves a phone in sunlight.
const body = Atkinson_Hyperlegible({
  variable: "--font-body",
  subsets: ["latin"],
  weight: ["400", "700"],
});

// A slab serif, the lettering of feed-store signs and seed catalogues.
const display = Zilla_Slab({
  variable: "--font-display",
  subsets: ["latin"],
  weight: ["500", "600", "700"],
});

export const metadata: Metadata = {
  title: "AgroPilot",
  description: "Today's irrigation for every plot.",
};

function Seedling() {
  return (
    <svg viewBox="0 0 24 24" className="size-7" aria-hidden fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M12 21v-9" />
      <path d="M12 12c0-4 2.5-6 7-6 0 4-2.5 6-7 6Z" />
      <path d="M12 15c0-3-2-5-6-5 0 3 2 5 6 5Z" />
    </svg>
  );
}

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    <html lang="en" className={`${body.variable} ${display.variable} h-full antialiased`}>
      {/* suppressHydrationWarning: browser extensions add attributes to <body> before React loads. */}
      <body className="flex min-h-full flex-col" suppressHydrationWarning>
        <header className="bg-field-dark text-primary-foreground">
          <div className="mx-auto flex w-full max-w-5xl items-center px-4 py-3 sm:px-6">
            <Link href="/" className="flex items-center gap-2 font-heading text-2xl font-bold tracking-wide">
              <Seedling />
              AgroPilot
            </Link>
          </div>
        </header>
        <div aria-hidden className="furrow-edge" />
        <div className="flex-1">{children}</div>
        <footer className="mx-auto w-full max-w-5xl border-t-2 border-dashed px-4 py-4 sm:px-6">
          <Suspense fallback={<p className="text-sm text-muted-foreground">Checking services</p>}>
            <StatusLine />
          </Suspense>
        </footer>
      </body>
    </html>
  );
}
