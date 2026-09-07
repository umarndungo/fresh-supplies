import type { Metadata } from "next";
import { cookies } from "next/headers";
import { SESSION_FLAG_COOKIE } from "@/lib/constants";
import { LandingNavbar } from "@/components/landing/landing-navbar";
import { LandingHero } from "@/components/landing/landing-hero";
import { LandingFeatures } from "@/components/landing/landing-features";
import { LandingImpact } from "@/components/landing/landing-impact";
import { LandingCTA } from "@/components/landing/landing-cta";
import { LandingFooter } from "@/components/landing/landing-footer";

export const metadata: Metadata = {
  title: "Fresh Supplies · Reduce Post-Harvest Losses in Sub-Saharan Africa",
  description:
    "Data-driven spoilage prediction, risk segmentation, and spoilage-aware route and market optimization for fresh produce.",
};

export default async function RootPage() {
  const cookieStore = await cookies();
  const hasSession = cookieStore.has(SESSION_FLAG_COOKIE);

  return (
    <div className="flex min-h-screen flex-col bg-background text-foreground selection:bg-primary/20 selection:text-primary">
      <LandingNavbar isAuthenticated={hasSession} />
      <main className="flex-1">
        <LandingHero />
        <LandingFeatures />
        <LandingImpact />
        <LandingCTA />
      </main>
      <LandingFooter />
    </div>
  );
}

