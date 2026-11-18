import Link from "next/link";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";

/** What went wrong, in the user's words, and how to continue. Never a stack trace. */
export function ProblemNotice({
  title,
  detail,
  retryHref,
  setup = false,
}: {
  title: string;
  detail: string;
  retryHref: string;
  /** The app is not set up: waiting will not help, so offer no retry. */
  setup?: boolean;
}) {
  return (
    <Alert variant="destructive" className="border-2 border-barn bg-card py-3">
      <AlertTitle className="font-heading text-2xl font-semibold">{title}</AlertTitle>
      <AlertDescription>
        <p className="text-base text-foreground">{detail}</p>
        <p className="mt-2 text-base text-foreground">
          {setup ? (
            "Ask whoever set up AgroPilot to fix this in the app's settings."
          ) : (
            <>
              Services usually come back within seconds.{" "}
              <Link href={retryHref} prefetch={false} className="font-bold text-field underline underline-offset-4">
                Try again
              </Link>
            </>
          )}
        </p>
      </AlertDescription>
    </Alert>
  );
}
