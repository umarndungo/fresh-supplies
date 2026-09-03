import type { ReactNode } from "react";
import Link from "next/link";
import { Logo } from "@/components/common/logo";
import { ThemeToggle } from "@/components/layout/theme-toggle";

export default function AuthLayout({ children }: { children: ReactNode }) {
  return (
    <div className="grid min-h-screen lg:grid-cols-2">
      <div className="relative hidden flex-col justify-between overflow-hidden bg-primary p-10 text-primary-foreground lg:flex">
        <div
          className="pointer-events-none absolute inset-0 opacity-20"
          style={{
            backgroundImage:
              "radial-gradient(circle at 20% 20%, white 0, transparent 40%), radial-gradient(circle at 80% 70%, white 0, transparent 35%)",
          }}
        />
        <Link href="/" className="relative z-10">
          <Logo variant="light" />
        </Link>
        <div className="relative z-10 space-y-4">
          <p className="text-sm uppercase tracking-[0.2em] text-primary-foreground/70">Enterprise AgTech</p>
          <h1 className="max-w-md font-display text-3xl font-semibold leading-tight">
            Move fresh produce from farm to market before the freshness window closes.
          </h1>
          <p className="max-w-sm text-sm text-primary-foreground/80">
            FreshRoute AI gives cooperatives, logistics teams, and market analysts one shared view of harvest,
            transport, and demand.
          </p>
        </div>
        <p className="relative z-10 text-xs text-primary-foreground/60">
          © {new Date().getFullYear()} FreshRoute AI. All rights reserved.
        </p>
      </div>
      <div className="flex flex-col">
        <div className="flex items-center justify-between p-6 lg:justify-end">
          <Link href="/" className="lg:hidden">
            <Logo />
          </Link>
          <ThemeToggle />
        </div>
        <div className="flex flex-1 items-center justify-center p-6">
          <div className="w-full max-w-sm">{children}</div>
        </div>
      </div>
    </div>
  );
}
