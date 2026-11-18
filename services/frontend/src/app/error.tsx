"use client";

import { useEffect } from "react";
import { Button } from "@/components/ui/button";

export default function ErrorPage({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    // The browser only gets a digest for server errors; the full error is in the server log.
    console.error(error);
  }, [error]);

  return (
    <main className="mx-auto w-full max-w-5xl px-4 py-6 sm:px-6">
      <h1 className="font-heading text-5xl font-bold leading-none">Something went wrong</h1>
      <p className="mt-4 max-w-prose">The page could not be shown. Trying again often fixes it.</p>
      {error.digest && (
        <p className="mt-2 text-sm text-muted-foreground">Reference for the logs: {error.digest}</p>
      )}
      <Button className="mt-4" onClick={reset}>
        Try again
      </Button>
    </main>
  );
}
