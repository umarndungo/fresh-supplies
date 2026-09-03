"use client";

import { useEffect } from "react";
import Link from "next/link";
import { TriangleAlert } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Logo } from "@/components/common/logo";

export default function Error({ error, reset }: { error: Error & { digest?: string }; reset: () => void }) {
  useEffect(() => {
    console.error("Unhandled application error:", error);
  }, [error]);

  return (
    <div className="flex min-h-screen flex-col items-center justify-center gap-6 bg-background px-6 text-center">
      <Logo />
      <div className="flex size-16 items-center justify-center rounded-full bg-destructive/10">
        <TriangleAlert className="size-8 text-destructive" strokeWidth={1.5} />
      </div>
      <div className="space-y-2">
        <p className="font-display text-5xl font-semibold text-destructive">500</p>
        <h1 className="text-xl font-semibold text-foreground">Something broke on our end</h1>
        <p className="max-w-sm text-sm text-muted-foreground">
          Our team has been notified. Try again, or head back to your dashboard.
        </p>
        {process.env.NODE_ENV === "development" && error.digest ? (
          <p className="font-mono text-xs text-muted-foreground">Digest: {error.digest}</p>
        ) : null}
      </div>
      <div className="flex gap-3">
        <Button variant="outline" onClick={() => reset()}>
          Try again
        </Button>
        <Button asChild>
          <Link href="/dashboard">Back to dashboard</Link>
        </Button>
      </div>
    </div>
  );
}
