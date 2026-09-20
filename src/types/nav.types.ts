import type { LucideIcon } from "lucide-react";
import type { UserRole } from "@/types/auth.types";

export interface NavItem {
  title: string;
  href: string;
  icon: LucideIcon;
  roles?: UserRole[];
  /** Only show to a FARMER_COOPERATIVE user whose cooperativeRole is ADMIN. */
  requiresCooperativeAdmin?: boolean;
  description?: string;
}

export interface NavSection {
  title: string;
  items: NavItem[];
}
