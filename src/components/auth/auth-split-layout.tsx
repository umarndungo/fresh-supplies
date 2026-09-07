"use client";

import type { ReactNode } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { Logo } from "@/components/common/logo";
import { ThemeToggle } from "@/components/layout/theme-toggle";

interface AuthSplitLayoutProps {
  children: ReactNode;
}

export function AuthSplitLayout({ children }: AuthSplitLayoutProps) {
  const pathname = usePathname();
  const isRegister = pathname?.includes("/register") ?? false;

  return (
    <div className="relative min-h-screen w-full overflow-x-hidden bg-background">
      {/* ============================================================ */}
      {/* MOBILE LAYOUT (< lg): Responsive stacked layout              */}
      {/* ============================================================ */}
      <div className="flex min-h-screen flex-col lg:hidden">
        <header className="flex items-center justify-between p-6">
          <Link href="/">
            <Logo />
          </Link>
          <ThemeToggle />
        </header>
        <main className="flex flex-1 items-center justify-center p-6">
          <div className="w-full max-w-sm">{children}</div>
        </main>
        <footer className="p-6 text-center text-xs text-muted-foreground">
          © {new Date().getFullYear()} Fresh Supplies. All rights reserved.
        </footer>
      </div>

      {/* ============================================================ */}
      {/* DESKTOP LAYOUT (>= lg): Forward-Slash (/) Split Layout       */}
      {/* ============================================================ */}
      <div className="relative hidden min-h-screen w-full lg:block">
        {/* --- BRAND PANEL WITH FORWARD-SLASH (/) DIAGONAL CLIP --- */}
        <div
          className="absolute inset-0 z-0 bg-primary text-primary-foreground transition-all duration-700 ease-in-out"
          style={{
            clipPath: isRegister
              ? "polygon(56% 0, 100% 0, 100% 100%, 44% 100%)"
              : "polygon(0 0, 56% 0, 44% 100%, 0 100%)",
          }}
        >
          {/* Subtle radial texture */}
          <div
            className="pointer-events-none absolute inset-0 opacity-20"
            style={{
              backgroundImage:
                "radial-gradient(circle at 20% 20%, white 0, transparent 40%), radial-gradient(circle at 80% 70%, white 0, transparent 35%)",
            }}
          />

          {/* Brand hero content */}
          <div
            className={`absolute top-0 bottom-0 flex w-[44%] flex-col justify-between p-10 xl:p-14 transition-all duration-700 ease-in-out ${
              isRegister
                ? "right-0 items-start pl-16 pr-10 xl:pr-14"
                : "left-0 items-start pl-10 pr-16 xl:pl-14"
            }`}
          >
            <Link href="/" className="relative z-10 transition-transform hover:opacity-90">
              <Logo variant="light" />
            </Link>

            <div className="relative z-10 max-w-md space-y-4">
              <p className="text-xs font-semibold uppercase tracking-[0.25em] text-primary-foreground/75">
                Enterprise AgTech
              </p>
              <h1 className="font-display text-3xl font-bold leading-tight tracking-tight xl:text-4xl">
                Move fresh produce from farm to market before the freshness window closes.
              </h1>
              <p className="text-sm leading-relaxed text-primary-foreground/80 xl:text-base">
                Fresh Supplies gives cooperatives, logistics teams, and market analysts one shared view of harvest,
                transport, and demand.
              </p>
            </div>

            <p className="relative z-10 text-xs text-primary-foreground/60">
              © {new Date().getFullYear()} Fresh Supplies. All rights reserved.
            </p>
          </div>
        </div>

        {/* --- FORWARD-SLASH (/) ACCENT DIVIDER LINE --- */}
        <svg
          className="pointer-events-none absolute inset-0 z-10 h-full w-full"
          preserveAspectRatio="none"
          viewBox="0 0 100 100"
        >
          <line
            x1="44"
            y1="100"
            x2="56"
            y2="0"
            stroke="currentColor"
            strokeWidth="0.2"
            className="text-white/20 dark:text-white/10"
          />
        </svg>

        {/* --- AUTH FORM PANEL --- */}
        {/* On Login (/login): positioned on the RIGHT side (w-1/2 ml-auto)    */}
        {/* On Register (/register): positioned on the LEFT side (w-1/2 mr-auto) */}
        <div
          className={`relative z-20 flex min-h-screen w-1/2 flex-col transition-all duration-700 ease-in-out ${
            isRegister ? "mr-auto" : "ml-auto"
          }`}
        >
          {/* Header containing ThemeToggle */}
          <header
            className={`flex items-center p-6 lg:p-8 ${
              isRegister ? "justify-start pl-10 xl:pl-14" : "justify-end pr-10 xl:pr-14"
            }`}
          >
            <ThemeToggle />
          </header>

          {/* Form Content */}
          <main className="flex flex-1 items-center justify-center px-8 py-6 lg:px-12 xl:px-16 overflow-y-auto">
            <div className="w-full max-w-sm my-auto">{children}</div>
          </main>

          {/* Bottom spacer matching header height */}
          <div className="h-10" />
        </div>
      </div>
    </div>
  );
}

