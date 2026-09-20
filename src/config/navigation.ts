import { LayoutDashboard, Truck, Warehouse, BarChart2, Route, FileBarChart, Users, LineChart, MapPin } from "lucide-react";
import type { AuthUser } from "@/types/auth.types";
import type { NavItem, NavSection } from "@/types/nav.types";

export function isNavItemVisible(item: NavItem, user: AuthUser | null): boolean {
  if (item.roles && (!user || !item.roles.includes(user.role))) return false;
  if (item.requiresCooperativeAdmin) {
    if (!user || user.role !== "FARMER_COOPERATIVE" || user.cooperativeRole !== "ADMIN") return false;
  }
  return true;
}

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
        roles: ["LOGISTICS_MANAGER"],
      },
      {
        title: "Produce Inventory",
        href: "/dashboard/produce",
        icon: Warehouse,
        roles: ["LOGISTICS_MANAGER", "FARMER_COOPERATIVE"],
      },
      {
        title: "Analytics",
        href: "/dashboard/analytics",
        icon: BarChart2,
        roles: ["LOGISTICS_MANAGER", "MARKET_ANALYST"],
        description: "Spoilage trends, revenue, risk distribution",
      },
      {
        title: "Market Insights",
        href: "/dashboard/market-insights",
        icon: LineChart,
        roles: ["MARKET_ANALYST"],
      },
      {
        title: "Route Optimization",
        href: "/dashboard/routes",
        icon: Route,
        roles: ["LOGISTICS_MANAGER"],
      },
      {
        title: "Reports",
        href: "/dashboard/reports",
        icon: FileBarChart,
        roles: ["LOGISTICS_MANAGER", "MARKET_ANALYST"],
      },
    ],
  },
  {
    title: "Administration",
    items: [
      { title: "Team & Access", href: "/dashboard/admin/users", icon: Users, roles: ["ADMINISTRATOR"] },
      { title: "Tenants", href: "/dashboard/admin/tenants", icon: Warehouse, roles: ["ADMINISTRATOR"] },
      { title: "Access Grants", href: "/dashboard/admin/grants", icon: Users, roles: ["ADMINISTRATOR"] },
    ],
  },
  {
    title: "My Cooperative",
    items: [
      {
        title: "Team",
        href: "/dashboard/cooperative/members",
        icon: Users,
        roles: ["FARMER_COOPERATIVE"],
        requiresCooperativeAdmin: true,
      },
    ],
  },
];
