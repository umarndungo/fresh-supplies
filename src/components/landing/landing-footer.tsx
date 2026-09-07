import Link from "next/link";
import { Logo } from "@/components/common/logo";
import { ROUTES } from "@/lib/constants";

export function LandingFooter() {
  return (
    <footer className="border-t border-border/60 bg-muted/20">
      <div className="mx-auto max-w-7xl px-4 py-12 sm:px-6 lg:px-8 lg:py-16">
        <div className="grid gap-8 lg:grid-cols-5">
          {/* Brand Column */}
          <div className="space-y-4 lg:col-span-2">
            <Link href="/" className="inline-block">
              <Logo />
            </Link>
            <p className="max-w-sm text-sm text-muted-foreground leading-relaxed">
              Reducing post-harvest perishable losses in Sub-Saharan Africa through data-driven spoilage prediction,
              risk segmentation, and route optimization.
            </p>
            <p className="text-xs text-muted-foreground">
              Built for regional road corridors, cooperatives, and high-temperature logistics.
            </p>
          </div>

          {/* Nav Columns */}
          <div className="space-y-3">
            <h4 className="text-xs font-semibold uppercase tracking-wider text-foreground">Platform</h4>
            <ul className="space-y-2 text-sm text-muted-foreground">
              <li>
                <a href="#features" className="hover:text-foreground transition-colors">
                  Spoilage Predictor
                </a>
              </li>
              <li>
                <a href="#how-it-works" className="hover:text-foreground transition-colors">
                  Smart Routing
                </a>
              </li>
              <li>
                <a href="#crops" className="hover:text-foreground transition-colors">
                  Supported Produce
                </a>
              </li>
              <li>
                <a href="#impact" className="hover:text-foreground transition-colors">
                  Supply Chain Impact
                </a>
              </li>
            </ul>
          </div>

          <div className="space-y-3">
            <h4 className="text-xs font-semibold uppercase tracking-wider text-foreground">Roles</h4>
            <ul className="space-y-2 text-sm text-muted-foreground">
              <li>
                <Link href={ROUTES.register} className="hover:text-foreground transition-colors">
                  Farmer Cooperatives
                </Link>
              </li>
              <li>
                <Link href={ROUTES.register} className="hover:text-foreground transition-colors">
                  Logistics Managers
                </Link>
              </li>
              <li>
                <Link href={ROUTES.register} className="hover:text-foreground transition-colors">
                  Market Analysts
                </Link>
              </li>
              <li>
                <Link href={ROUTES.register} className="hover:text-foreground transition-colors">
                  Administrators
                </Link>
              </li>
            </ul>
          </div>

          <div className="space-y-3">
            <h4 className="text-xs font-semibold uppercase tracking-wider text-foreground">Workspace</h4>
            <ul className="space-y-2 text-sm text-muted-foreground">
              <li>
                <Link href={ROUTES.login} className="hover:text-foreground transition-colors">
                  Sign In
                </Link>
              </li>
              <li>
                <Link href={ROUTES.register} className="hover:text-foreground transition-colors">
                  Create Account
                </Link>
              </li>
            </ul>
          </div>
        </div>

        {/* Bottom Bar */}
        <div className="mt-12 flex flex-col items-center justify-between gap-4 border-t border-border/60 pt-8 sm:flex-row text-xs text-muted-foreground">
          <p>© {new Date().getFullYear()} Fresh Supplies. All rights reserved.</p>
          <p className="flex items-center gap-1.5">
            <span>Powered by FastAPI · Next.js 16 · XGBoost ML Engine</span>
          </p>
        </div>
      </div>
    </footer>
  );
}

