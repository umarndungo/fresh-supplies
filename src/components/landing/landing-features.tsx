import {
  BrainCircuit,
  Navigation,
  Users,
  Smartphone,
  BarChart3,
  ShieldCheck,
} from "lucide-react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

export function LandingFeatures() {
  const features = [
    {
      icon: BrainCircuit,
      title: "Machine Learning Spoilage Engine",
      description:
        "Trained on real agricultural degradation curves, ambient temperature, humidity, and transit durations to forecast exact freshness expiration.",
    },
    {
      icon: Navigation,
      title: "Dynamic Market Re-allocation",
      description:
        "When traffic delays or heat waves jeopardize shelf-life, our routing engine re-routes shipments to nearer premium buyers before produce spoils.",
    },
    {
      icon: Smartphone,
      title: "Offline-First Mobile Dispatch",
      description:
        "Drivers and field workers operate seamlessly in remote farming corridors without cellular network. Records sync automatically once reconnected.",
    },
    {
      icon: Users,
      title: "Farmer Cooperative Empowerment",
      description:
        "Transparent aggregation tracking gives smallholder farmers and cooperative leaders fair grading, accurate weights, and reliable payout records.",
    },
    {
      icon: BarChart3,
      title: "Wholesale Market Price Intelligence",
      description:
        "Continuously compares prevailing commodity rates across regional urban markets to maximize gross margins for every dispatch.",
    },
    {
      icon: ShieldCheck,
      title: "Quality Verification & Audit Trail",
      description:
        "Capture multi-angle photo evidence and digital inspection sign-offs at farmgate pickup, intermediate depots, and final receiving docks.",
    },
  ];

  return (
    <section id="features" className="py-20 bg-muted/30">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="mx-auto max-w-3xl text-center">
          <p className="text-xs font-semibold uppercase tracking-widest text-primary">Core Capabilities</p>
          <h2 className="mt-2 font-display text-3xl font-bold tracking-tight sm:text-4xl">
            Engineered for Sub-Saharan African AgTech Logistics
          </h2>
          <p className="mt-4 text-base text-muted-foreground sm:text-lg">
            Every layer of Fresh Supplies is optimized to conquer infrastructure bottlenecks, hot transit corridors,
            and volatile food markets.
          </p>
        </div>

        <div className="mt-14 grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {features.map((feature, idx) => {
            const Icon = feature.icon;
            return (
              <Card
                key={idx}
                className="border-border/70 bg-card transition-all duration-200 hover:-translate-y-1 hover:border-primary/50 hover:shadow-lg"
              >
                <CardHeader className="space-y-3">
                  <div className="inline-flex size-11 items-center justify-center rounded-xl bg-primary/10 text-primary">
                    <Icon className="size-5" />
                  </div>
                  <CardTitle className="text-lg font-semibold">{feature.title}</CardTitle>
                </CardHeader>
                <CardContent>
                  <CardDescription className="text-sm leading-relaxed normal-case text-muted-foreground">
                    {feature.description}
                  </CardDescription>
                </CardContent>
              </Card>
            );
          })}
        </div>
      </div>
    </section>
  );
}

