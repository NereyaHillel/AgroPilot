import Link from "next/link";

export default function NotFound() {
  return (
    <main className="mx-auto w-full max-w-5xl px-4 py-6 sm:px-6">
      <h1 className="font-heading text-5xl font-bold leading-none">Plot not found</h1>
      <p className="mt-4 max-w-prose">
        The registry has no plot with this address. It may have been removed.
      </p>
      <p className="mt-4">
        <Link href="/" className="font-bold text-field underline underline-offset-4">
          Back to all plots
        </Link>
      </p>
    </main>
  );
}
