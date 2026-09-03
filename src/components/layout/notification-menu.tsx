"use client";

import { Bell } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { EmptyState } from "@/components/common/empty-state";

export function NotificationMenu() {
  const hasUnread = false;

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="ghost" size="icon" className="relative" aria-label="Notifications">
          <Bell className="size-5" />
          {hasUnread ? <span className="absolute right-2 top-2 size-2 rounded-full bg-accent ring-2 ring-card" /> : null}
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end" className="w-80">
        <DropdownMenuLabel>Notifications</DropdownMenuLabel>
        <DropdownMenuSeparator />
        <div className="p-2">
          <EmptyState
            icon={Bell}
            title="You're all caught up"
            description="Spoilage alerts and route updates will appear here."
          />
        </div>
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
