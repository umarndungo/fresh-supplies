import { LayoutDashboard, Truck, Warehouse, BarChart2, Route, FileBarChart, Users, LineChart, MapPin } from "lucide-react";
import type { NavSection } from "@/types/nav.types";

/**
 * Full intended information architecture for Fresh Supplies. Shipments is
 * implemented; the remaining routes are scaffolded so the shell is
 * realistic, and resolve to the branded 404 page until built.
 */
export const NAV_SECTIONS: NavSection[] = [
  {
    title: "Workspace",
    items: [
      { title: "Overview", href: "/dashboard", icon: LayoutDashboard, description: "Your account summary" },
      {
        title: "Shipments",
        href: "/dashboard/shipments",
        icon: Truck,
        roles: ["ADMINISTRATOR", "LOGISTICS_MANAGER"],
      },
      {
        title: "Produce Inventory",
        href: "/dashboard/produce",
        icon: Warehouse,
        roles: ["ADMINISTRATOR", "LOGISTICS_MANAGER", "FARMER_COOPERATIVE"],
      },
      {
        title: "Analytics",
        href: "/dashboard/analytics",
        icon: BarChart2,
        roles: ["ADMINISTRATOR", "LOGISTICS_MANAGER", "MARKET_ANALYST"],
        description: "Spoilage trends, revenue, risk distribution",
      },
      {
        title: "Market Insights",
        href: "/dashboard/market-insights",
        icon: LineChart,
        roles: ["ADMINISTRATOR", "MARKET_ANALYST"],
      },
      {
        title: "Route Optimization",
        href: "/dashboard/routes",
        icon: Route,
        roles: ["ADMINISTRATOR", "LOGISTICS_MANAGER"],
      },
      { title: "Reports", href: "/dashboard/reports", icon: FileBarChart },
    ],
  },
  {
    title: "Administration",
    items: [{ title: "Team & Access", href: "/dashboard/admin/users", icon: Users, roles: ["ADMINISTRATOR"] }],
  },
];
