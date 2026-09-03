"use client";

import { LogOut, Settings, User as UserIcon } from "lucide-react";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Badge } from "@/components/ui/badge";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { useAuthContext } from "@/context/auth-context";
import { useAuth } from "@/hooks/use-auth";
import { ROLE_LABELS } from "@/lib/constants";
import { getInitials } from "@/lib/utils";

export function ProfileDropdown() {
  const { user } = useAuthContext();
  const { logout, isLoggingOut } = useAuth();

  if (!user) return null;

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <button
          className="flex items-center gap-2 rounded-full outline-none ring-offset-2 focus-visible:ring-2 focus-visible:ring-ring"
          aria-label="Account menu"
        >
          <Avatar className="size-8">
            <AvatarFallback className="bg-primary/10 text-xs font-medium text-primary">
              {getInitials(user.fullName)}
            </AvatarFallback>
          </Avatar>
        </button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end" className="w-64">
        <DropdownMenuLabel className="space-y-1">
          <p className="text-sm font-medium leading-none">{user.fullName}</p>
          <p className="text-xs font-normal text-muted-foreground">{user.email}</p>
          <Badge variant="secondary" className="mt-1">
            {ROLE_LABELS[user.role]}
          </Badge>
        </DropdownMenuLabel>
        <DropdownMenuSeparator />
        <DropdownMenuItem disabled>
          <UserIcon className="size-4" /> Profile
          <span className="ml-auto text-xs text-muted-foreground">Soon</span>
        </DropdownMenuItem>
        <DropdownMenuItem disabled>
          <Settings className="size-4" /> Account settings
          <span className="ml-auto text-xs text-muted-foreground">Soon</span>
        </DropdownMenuItem>
        <DropdownMenuSeparator />
        <DropdownMenuItem variant="destructive" onSelect={() => void logout()} disabled={isLoggingOut}>
          <LogOut className="size-4" /> Log out
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
