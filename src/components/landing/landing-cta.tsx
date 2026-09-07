import Link from "next/link";
import { ArrowRight, Sparkles } from "lucide-react";
import { Button } from "@/components/ui/button";
import { ROUTES } from "@/lib/constants";

export function LandingCTA() {
  return (
    <section id="impact" className="relative overflow-hidden py-20 lg:py-24">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="relative overflow-hidden rounded-3xl bg-primary px-6 py-16 text-center text-primary-foreground shadow-2xl sm:px-12 md:py-20 lg:px-16">
          {/* Subtle background decorative circle */}
          <div
            className="pointer-events-none absolute inset-0 opacity-20"
            style={{
              backgroundImage:
                "radial-gradient(circle at 20% 20%, white 0, transparent 40%), radial-gradient(circle at 80% 70%, white 0, transparent 35%)",
            }}
          />

          <div className="relative z-10 mx-auto max-w-3xl space-y-6">
            <div className="inline-flex items-center gap-2 rounded-full border border-white/20 bg-white/10 px-3.5 py-1 text-xs font-medium text-white">
              <Sparkles className="size-3.5 text-accent" />
              <span>Built for Resilient AgTech Supply Chains</span>
            </div>

            <h2 className="font-display text-3xl font-bold tracking-tight sm:text-4xl lg:text-5xl text-white">
              Stop produce spoilage before it happens.
            </h2>

            <p className="mx-auto max-w-xl text-base text-white/85 sm:text-lg">
              Empower your cooperative, streamline transport fleets, and secure top-tier wholesale pricing with AI
              freshness prediction.
            </p>

            <div className="flex flex-col items-center justify-center gap-3 pt-4 sm:flex-row">
              <Button asChild size="lg" className="w-full sm:w-auto bg-white text-primary hover:bg-white/90 gap-2 shadow-lg">
                <Link href={ROUTES.register}>
                  Get Started Today
                  <ArrowRight className="size-4" />
                </Link>
              </Button>
              <Button
                asChild
                variant="outline"
                size="lg"
                className="w-full sm:w-auto border-white/40 text-white hover:bg-white/10 hover:text-white"
              >
                <Link href={ROUTES.login}>Sign in to Workspace</Link>
              </Button>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}

