import type { LucideIcon } from "lucide-react";
import type { UserRole } from "@/types/auth.types";

export interface NavItem {
  title: string;
  href: string;
  icon: LucideIcon;
  roles?: UserRole[];
  description?: string;
}

export interface NavSection {
  title: string;
  items: NavItem[];
}
