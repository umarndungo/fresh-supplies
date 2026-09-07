import Link from "next/link";
import { ArrowRight, ShieldCheck, Sparkles, TrendingDown, Clock, MapPin, Truck } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { ROUTES } from "@/lib/constants";

export function LandingHero() {
  return (
    <section className="relative overflow-hidden pt-12 pb-20 md:pt-20 md:pb-28">
      {/* Background Gradients */}
      <div className="pointer-events-none absolute -top-40 left-1/2 -z-10 h-[550px] w-[1000px] -translate-x-1/2 opacity-30 blur-3xl [background:radial-gradient(circle_at_center,var(--primary)_0%,transparent_70%)]" />

      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="grid items-center gap-12 lg:grid-cols-12 lg:gap-8">
          {/* Left Column: Headlines & CTA */}
          <div className="space-y-6 text-center lg:col-span-7 lg:text-left">
            <div className="inline-flex items-center gap-2 rounded-full border border-primary/20 bg-primary/10 px-3.5 py-1.5 text-xs font-medium text-primary">
              <Sparkles className="size-3.5 text-accent" />
              <span>AI-Powered Cold Chain & Loss Prevention</span>
            </div>

            <h1 className="font-display text-4xl font-bold tracking-tight sm:text-5xl lg:text-6xl">
              Move fresh produce from farm to market before the{" "}
              <span className="text-primary">
                freshness window closes
              </span>
              .
            </h1>

            <p className="mx-auto max-w-2xl text-base leading-relaxed text-muted-foreground sm:text-lg lg:mx-0">
              Fresh Supplies equips agricultural cooperatives, logistics fleets, and market buyers across Sub-Saharan Africa
              with real-time spoilage forecasting, dynamic route reallocation, and wholesale price intelligence.
            </p>

            {/* CTA Buttons */}
            <div className="flex flex-col items-center justify-center gap-3 pt-2 sm:flex-row lg:justify-start">
              <Button asChild size="lg" className="w-full sm:w-auto gap-2 shadow-md hover:shadow-lg">
                <Link href={ROUTES.register}>
                  Create Free Account
                  <ArrowRight className="size-4" />
                </Link>
              </Button>
              <Button asChild variant="outline" size="lg" className="w-full sm:w-auto">
                <Link href={ROUTES.login}>Sign in to Workspace</Link>
              </Button>
            </div>

            {/* Quick Guarantees */}
            <div className="flex flex-wrap items-center justify-center gap-6 pt-3 text-xs text-muted-foreground lg:justify-start">
              <div className="flex items-center gap-1.5">
                <ShieldCheck className="size-4 text-primary" />
                <span>Offline-first field sync</span>
              </div>
              <div className="flex items-center gap-1.5">
                <Clock className="size-4 text-primary" />
                <span>Real-time shelf-life alerts</span>
              </div>
              <div className="flex items-center gap-1.5">
                <MapPin className="size-4 text-primary" />
                <span>Cross-corridor route tracking</span>
              </div>
            </div>
          </div>

          {/* Right Column: Live Spoilage Intelligence Mock Card */}
          <div className="lg:col-span-5">
            <div className="relative mx-auto max-w-md rounded-2xl border border-border/80 bg-card p-6 shadow-2xl transition-all hover:border-primary/40">
              {/* Header Badge */}
              <div className="flex items-center justify-between border-b border-border/60 pb-4">
                <div className="flex items-center gap-2.5">
                  <div className="flex size-9 items-center justify-center rounded-lg bg-primary/10 text-primary">
                    <Truck className="size-5" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-sm">Batch #FS-8842</h3>
                    <p className="text-xs text-muted-foreground">Eldoret Hub → Nairobi Wholesale</p>
                  </div>
                </div>
                <Badge variant="outline" className="border-emerald-500/40 bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 font-medium">
                  Optimal Quality
                </Badge>
              </div>

              {/* Produce Information */}
              <div className="grid grid-cols-2 gap-3 py-4 text-xs">
                <div className="rounded-lg bg-muted/60 p-3">
                  <span className="text-muted-foreground">Commodity</span>
                  <p className="mt-1 font-semibold text-sm text-foreground">Roma Tomatoes</p>
                  <p className="text-[11px] text-muted-foreground">Class A · 4,200 kg</p>
                </div>
                <div className="rounded-lg bg-muted/60 p-3">
                  <span className="text-muted-foreground">Est. Shelf Life</span>
                  <p className="mt-1 font-semibold text-sm text-primary">5.2 Days Left</p>
                  <p className="text-[11px] text-emerald-600 dark:text-emerald-400">94% Viability Window</p>
                </div>
              </div>

              {/* Spoilage Risk Gauge Indicator */}
              <div className="space-y-2 rounded-lg border border-border/60 bg-muted/30 p-3">
                <div className="flex items-center justify-between text-xs">
                  <span className="font-medium text-foreground">Spoilage Probability</span>
                  <span className="font-bold text-primary">8.4% (Low Risk)</span>
                </div>
                <div className="h-2 w-full overflow-hidden rounded-full bg-muted">
                  <div className="h-full w-[8.4%] rounded-full bg-primary" />
                </div>
                <p className="text-[11px] text-muted-foreground">
                  Transit conditions nominal (14.2°C ambient, 78% humidity).
                </p>
              </div>

              {/* Route Suggestion Card */}
              <div className="mt-4 flex items-center justify-between rounded-lg border border-accent/30 bg-accent/10 p-3 text-xs">
                <div className="space-y-0.5">
                  <span className="font-semibold text-accent-foreground dark:text-accent">Recommended Destination</span>
                  <p className="text-muted-foreground">Wakulima Market · Highest Demand Margin</p>
                </div>
                <span className="font-bold text-sm text-foreground">KES 110/kg</span>
              </div>
            </div>
          </div>
        </div>

        {/* Value Stats Banner */}
        <div className="mt-16 grid grid-cols-2 gap-4 rounded-2xl border border-border/70 bg-card/60 p-6 backdrop-blur-sm sm:grid-cols-4 sm:gap-8 sm:p-8">
          <div className="text-center">
            <p className="font-display text-3xl font-bold tracking-tight text-primary sm:text-4xl">38%</p>
            <p className="mt-1 text-xs text-muted-foreground sm:text-sm font-medium">Post-Harvest Loss Cut</p>
          </div>
          <div className="text-center">
            <p className="font-display text-3xl font-bold tracking-tight text-primary sm:text-4xl">14+</p>
            <p className="mt-1 text-xs text-muted-foreground sm:text-sm font-medium">Perishable Crop Types</p>
          </div>
          <div className="text-center">
            <p className="font-display text-3xl font-bold tracking-tight text-primary sm:text-4xl">2.4x</p>
            <p className="mt-1 text-xs text-muted-foreground sm:text-sm font-medium">Faster Route Reallocation</p>
          </div>
          <div className="text-center">
            <p className="font-display text-3xl font-bold tracking-tight text-primary sm:text-4xl">100%</p>
            <p className="mt-1 text-xs text-muted-foreground sm:text-sm font-medium">Offline Sync for Drivers</p>
          </div>
        </div>
      </div>
    </section>
  );
}

