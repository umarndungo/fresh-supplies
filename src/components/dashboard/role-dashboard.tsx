"use client";

import { useAuthContext } from "@/context/auth-context";
import type { UserRole } from "@/types/auth.types";
import { Truck, Warehouse, BarChart2, Route, Package, Users, MapPin, AlertTriangle, DollarSign, TrendingUp } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import Link from "next/link";

const ROLE_CONFIG: Record<UserRole, {
  title: string;
  description: string;
  primaryActions: { label: string; href: string; icon: React.ComponentType<{ className?: string }> }[];
  quickStats: { label: string; value: string | number; icon: React.ComponentType<{ className?: string }>; color: string }[];
  sections: { title: string; items: { label: string; href: string; description: string; icon: React.ComponentType<{ className?: string }> }[] }[];
}> = {
  ADMINISTRATOR: {
    title: "System Overview",
    description: "Full platform visibility and administration",
    primaryActions: [
      { label: "Manage Users", href: "/dashboard/admin/users", icon: Users },
      { label: "View All Shipments", href: "/dashboard/shipments", icon: Truck },
      { label: "System Analytics", href: "/dashboard/analytics", icon: BarChart2 },
    ],
    quickStats: [
      { label: "Total Users", value: "—", icon: Users, color: "text-blue-600" },
      { label: "Active Shipments", value: "—", icon: Truck, color: "text-green-600" },
      { label: "System Health", value: "OK", icon: TrendingUp, color: "text-emerald-600" },
    ],
    sections: [
      {
        title: "Administration",
        items: [
          { label: "Team & Access", href: "/dashboard/admin/users", description: "Manage users and roles", icon: Users },
        ],
      },
      {
        title: "Operations",
        items: [
          { label: "All Shipments", href: "/dashboard/shipments", description: "Track all shipments", icon: Truck },
          { label: "Produce Inventory", href: "/dashboard/produce", description: "System-wide inventory", icon: Warehouse },
          { label: "Route Optimization", href: "/dashboard/routes", description: "Manage routes", icon: Route },
        ],
      },
      {
        title: "Insights",
        items: [
          { label: "Analytics", href: "/dashboard/analytics", description: "Platform analytics", icon: BarChart2 },
          { label: "Reports", href: "/dashboard/reports", description: "Generate reports", icon: DollarSign },
        ],
      },
    ],
  },
  LOGISTICS_MANAGER: {
    title: "Logistics Dashboard",
    description: "Fleet-wide risk overview, all shipments, route management",
    primaryActions: [
      { label: "New Shipment", href: "/dashboard/shipments", icon: Truck },
      { label: "Optimize Route", href: "/dashboard/routes", icon: Route },
      { label: "View Analytics", href: "/dashboard/analytics", icon: BarChart2 },
    ],
    quickStats: [
      { label: "In Transit", value: "—", icon: Truck, color: "text-blue-600" },
      { label: "At Risk", value: "—", icon: AlertTriangle, color: "text-amber-600" },
      { label: "Avg Spoilage", value: "—%", icon: TrendingUp, color: "text-red-600" },
    ],
    sections: [
      {
        title: "Shipments",
        items: [
          { label: "All Shipments", href: "/dashboard/shipments", description: "Track and manage shipments", icon: Truck },
          { label: "Create Shipment", href: "/dashboard/shipments", description: "Schedule new shipment", icon: Package },
        ],
      },
      {
        title: "Inventory & Routes",
        items: [
          { label: "Produce Inventory", href: "/dashboard/produce", description: "Available stock", icon: Warehouse },
          { label: "Route Optimization", href: "/dashboard/routes", description: "Plan optimal routes", icon: Route },
          { label: "Market Insights", href: "/dashboard/market-insights", description: "Market prices & trends", icon: MapPin },
        ],
      },
      {
        title: "Analytics",
        items: [
          { label: "Spoilage Trends", href: "/dashboard/analytics", description: "Risk analytics", icon: BarChart2 },
          { label: "Reports", href: "/dashboard/reports", description: "Operational reports", icon: DollarSign },
        ],
      },
    ],
  },
  FARMER_COOPERATIVE: {
    title: "My Cooperative",
    description: "Your shipments, produce, and simplified recommendations",
    primaryActions: [
      { label: "Add Produce", href: "/dashboard/produce", icon: Package },
      { label: "New Shipment", href: "/dashboard/shipments", icon: Truck },
      { label: "My Recommendations", href: "/dashboard/analytics", icon: MapPin },
    ],
    quickStats: [
      { label: "My Produce", value: "—", icon: Package, color: "text-green-600" },
      { label: "Active Shipments", value: "—", icon: Truck, color: "text-blue-600" },
      { label: "Revenue This Month", value: "— KES", icon: DollarSign, color: "text-emerald-600" },
    ],
    sections: [
      {
        title: "My Produce",
        items: [
          { label: "Inventory", href: "/dashboard/produce", description: "Manage your produce stock", icon: Package },
          { label: "Add Harvest", href: "/dashboard/produce", description: "Record new harvest", icon: Package },
        ],
      },
      {
        title: "My Shipments",
        items: [
          { label: "Track Shipments", href: "/dashboard/shipments", description: "Your shipments only", icon: Truck },
          { label: "Schedule Delivery", href: "/dashboard/shipments", description: "Create new shipment", icon: Package },
        ],
      },
      {
        title: "Recommendations",
        items: [
          { label: "Best Markets", href: "/dashboard/analytics", description: "Where to sell for max revenue", icon: MapPin },
          { label: "Risk Alerts", href: "/dashboard/analytics", description: "Spoilage warnings", icon: AlertTriangle },
        ],
      },
    ],
  },
  MARKET_ANALYST: {
    title: "Market Intelligence",
    description: "Market prices, trends, and analytics",
    primaryActions: [
      { label: "Market Prices", href: "/dashboard/market-insights", icon: MapPin },
      { label: "Analytics", href: "/dashboard/analytics", icon: BarChart2 },
      { label: "Export Report", href: "/dashboard/reports", icon: DollarSign },
    ],
    quickStats: [
      { label: "Markets Tracked", value: "10", icon: MapPin, color: "text-blue-600" },
      { label: "Price Alerts", value: "—", icon: AlertTriangle, color: "text-amber-600" },
      { label: "Avg Margin", value: "—%", icon: TrendingUp, color: "text-emerald-600" },
    ],
    sections: [
      {
        title: "Market Analysis",
        items: [
          { label: "Market Insights", href: "/dashboard/market-insights", description: "Price trends by market", icon: MapPin },
          { label: "Price History", href: "/dashboard/market-insights", description: "Historical price data", icon: TrendingUp },
        ],
      },
      {
        title: "Revenue Optimization",
        items: [
          { label: "Analytics", href: "/dashboard/analytics", description: "Spoilage & revenue analytics", icon: BarChart2 },
          { label: "Route Efficiency", href: "/dashboard/routes", description: "Route cost analysis", icon: Route },
        ],
      },
      {
        title: "Reporting",
        items: [
          { label: "Market Reports", href: "/dashboard/reports", description: "Generate market reports", icon: DollarSign },
          { label: "Export Data", href: "/dashboard/reports", description: "Download CSV/Excel", icon: Package },
        ],
      },
    ],
  },
};

export function RoleDashboard() {
  const { user } = useAuthContext();
  const role = user?.role ?? "ADMINISTRATOR";
  const config = ROLE_CONFIG[role];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">{config.title}</h1>
        <p className="text-muted-foreground">{config.description}</p>
      </div>

      <div className="flex flex-wrap gap-3">
        {config.primaryActions.map((action) => (
          <Link key={action.href} href={action.href as any}>
            <Button>
              <action.icon className="size-4 mr-2" />
              {action.label}
            </Button>
          </Link>
        ))}
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        {config.quickStats.map((stat, i) => (
          <Card key={i}>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">{stat.label}</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex items-center justify-between">
                <span className={`text-2xl font-bold ${stat.color}`}>{stat.value}</span>
                <stat.icon className="size-6 text-muted-foreground" />
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      <div className="space-y-6">
        {config.sections.map((section) => (
          <Card key={section.title}>
            <CardHeader>
              <CardTitle>{section.title}</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
                {section.items.map((item) => (
                  <Link key={item.href} href={item.href as any} className="p-4 rounded-lg border hover:bg-secondary transition-colors">
                    <div className="flex items-center gap-3 mb-2">
                      <item.icon className="size-5 text-primary" />
                      <span className="font-medium">{item.label}</span>
                    </div>
                    <p className="text-sm text-muted-foreground">{item.description}</p>
                  </Link>
                ))}
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}

export function RoleSpecificContent() {
  const { user } = useAuthContext();
  const role = user?.role ?? "ADMINISTRATOR";

  switch (role) {
    case "LOGISTICS_MANAGER":
      return <LogisticsManagerDashboard />;
    case "FARMER_COOPERATIVE":
      return <FarmerCooperativeDashboard />;
    case "MARKET_ANALYST":
      return <MarketAnalystDashboard />;
    default:
      return <AdministratorDashboard />;
  }
}

function AdministratorDashboard() {
  return (
    <div className="space-y-6">
      <h2 className="text-xl font-bold">Administrator Dashboard</h2>
      <p className="text-muted-foreground">Full platform administration coming soon...</p>
    </div>
  );
}

function LogisticsManagerDashboard() {
  return (
    <div className="space-y-6">
      <h2 className="text-xl font-bold">Logistics Manager Dashboard</h2>
      <p className="text-muted-foreground">Fleet-wide risk overview, all shipments, map view coming soon...</p>
    </div>
  );
}

function FarmerCooperativeDashboard() {
  return (
    <div className="space-y-6">
      <h2 className="text-xl font-bold">Farmer Cooperative Dashboard</h2>
      <p className="text-muted-foreground">Your shipments only, simplified recommendation view coming soon...</p>
    </div>
  );
}

function MarketAnalystDashboard() {
  return (
    <div className="space-y-6">
      <h2 className="text-xl font-bold">Market Analyst Dashboard</h2>
      <p className="text-muted-foreground">Full ranked market tables, price trends, analytics-heavy coming soon...</p>
    </div>
  );
}