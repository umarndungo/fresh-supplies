import { CheckCircle2, ArrowRight, Sprout, MapPin, Truck, Store } from "lucide-react";
import { Badge } from "@/components/ui/badge";

export function LandingImpact() {
  const steps = [
    {
      step: "01",
      icon: Sprout,
      title: "Harvest & Field Aggregation",
      description:
        "Farmer cooperatives weigh, grade, and record harvested produce at regional collection centers using mobile and desktop forms.",
    },
    {
      step: "02",
      icon: MapPin,
      title: "AI Spoilage & Risk Scoring",
      description:
        "Our engine models ambient transit temperatures, crop respiration, and humidity to estimate shelf life and choose optimal delivery windows.",
    },
    {
      step: "03",
      icon: Truck,
      title: "Intelligent In-Transit Routing",
      description:
        "Drivers receive offline-capable turn-by-turn assignments. If road delays occur, alternative wholesale markets are automatically recommended.",
    },
    {
      step: "04",
      icon: Store,
      title: "Wholesale Delivery & Payout",
      description:
        "Produce arrives fresh at maximum market value. Digital proof-of-delivery is confirmed, and fair payouts are unlocked for cooperatives.",
    },
  ];

  const crops = [
    { name: "Roma & Round Tomatoes", category: "High Respiration", shelf: "4 - 7 Days" },
    { name: "Hass & Fuerte Avocados", category: "Export Grade", shelf: "10 - 14 Days" },
    { name: "French Beans & Peas", category: "Cold Sensitive", shelf: "5 - 8 Days" },
    { name: "Mangoes & Tropicals", category: "Climacteric", shelf: "7 - 12 Days" },
    { name: "Kales & Leafy Greens", category: "Rapid Spoilage", shelf: "2 - 4 Days" },
    { name: "Sweet Peppers & Chillies", category: "Market Staple", shelf: "8 - 12 Days" },
  ];

  return (
    <section id="how-it-works" className="py-20">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        {/* Step-by-Step Supply Chain */}
        <div className="mx-auto max-w-3xl text-center">
          <p className="text-xs font-semibold uppercase tracking-widest text-primary">Workflow</p>
          <h2 className="mt-2 font-display text-3xl font-bold tracking-tight sm:text-4xl">
            How Produce Moves with Fresh Supplies
          </h2>
          <p className="mt-4 text-base text-muted-foreground sm:text-lg">
            From the rural aggregation depot to the urban wholesale terminal, every step is safeguarded by predictive
            analytics.
          </p>
        </div>

        <div className="mt-14 grid gap-8 md:grid-cols-2 lg:grid-cols-4">
          {steps.map((item, idx) => {
            const Icon = item.icon;
            return (
              <div
                key={idx}
                className="relative rounded-2xl border border-border/70 bg-card p-6 shadow-sm transition-all hover:border-primary/40 hover:shadow-md"
              >
                <div className="flex items-center justify-between">
                  <span className="font-display text-2xl font-bold text-primary/40">{item.step}</span>
                  <div className="flex size-10 items-center justify-center rounded-lg bg-primary/10 text-primary">
                    <Icon className="size-5" />
                  </div>
                </div>
                <h3 className="mt-4 text-lg font-semibold text-foreground">{item.title}</h3>
                <p className="mt-2 text-sm leading-relaxed text-muted-foreground">{item.description}</p>
              </div>
            );
          })}
        </div>

        {/* Supported Perishable Crops Showcase */}
        <div id="crops" className="mt-24 rounded-3xl border border-border/80 bg-muted/40 p-8 lg:p-12">
          <div className="grid items-center gap-8 lg:grid-cols-12">
            <div className="space-y-4 lg:col-span-5">
              <Badge variant="outline" className="border-primary/40 bg-primary/10 text-primary font-medium">
                Produce Coverage
              </Badge>
              <h3 className="font-display text-2xl font-bold tracking-tight sm:text-3xl">
                Trained on the East & Sub-Saharan Africa Produce Basket
              </h3>
              <p className="text-sm leading-relaxed text-muted-foreground">
                Our machine learning models are calibrated against specific local cultivars, packaging habits (crate,
                sack, loose), and ambient temperature baselines across regional agricultural corridors.
              </p>
              <div className="space-y-2 pt-2 text-xs text-muted-foreground">
                <div className="flex items-center gap-2">
                  <CheckCircle2 className="size-4 text-primary" />
                  <span>Ambient and refrigerated transport profiling</span>
                </div>
                <div className="flex items-center gap-2">
                  <CheckCircle2 className="size-4 text-primary" />
                  <span>Dynamic price discovery across regional hubs</span>
                </div>
              </div>
            </div>

            <div className="grid gap-3 sm:grid-cols-2 lg:col-span-7">
              {crops.map((crop, idx) => (
                <div
                  key={idx}
                  className="flex items-center justify-between rounded-xl border border-border/60 bg-card p-4 shadow-sm"
                >
                  <div>
                    <h4 className="font-semibold text-sm text-foreground">{crop.name}</h4>
                    <p className="text-xs text-muted-foreground">{crop.category}</p>
                  </div>
                  <Badge variant="secondary" className="text-xs font-normal">
                    {crop.shelf}
                  </Badge>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}

