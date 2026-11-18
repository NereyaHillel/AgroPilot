export default function Loading() {
  return (
    <main className="mx-auto w-full max-w-5xl px-4 py-6 sm:px-6" aria-busy="true">
      <h1 className="font-heading text-5xl font-bold leading-none sm:text-6xl">Your plots</h1>
      <p className="mt-6 text-muted-foreground">Loading plots</p>
    </main>
  );
}
