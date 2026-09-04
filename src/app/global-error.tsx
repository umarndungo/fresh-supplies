"use client";

import "./globals.css";

export default function GlobalError({ error, reset }: { error: Error & { digest?: string }; reset: () => void }) {
  return (
    <html lang="en">
      <body className="font-sans antialiased">
        <div className="flex min-h-screen flex-col items-center justify-center gap-6 bg-background px-6 text-center">
          <div className="space-y-2">
            <p className="font-display text-5xl font-semibold text-destructive">500</p>
            <h1 className="text-xl font-semibold text-foreground">Fresh Supplies hit a critical error</h1>
            <p className="max-w-sm text-sm text-muted-foreground">
              The application failed to render. Reloading usually resolves this.
            </p>
            {error.digest ? <p className="font-mono text-xs text-muted-foreground">Digest: {error.digest}</p> : null}
          </div>
          <button
            onClick={() => reset()}
            className="rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:opacity-90"
          >
            Try again
          </button>
        </div>
      </body>
    </html>
  );
}
