"use client";

import { useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { Menu } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Sheet, SheetContent, SheetHeader, SheetTitle, SheetTrigger } from "@/components/ui/sheet";
import { Logo } from "@/components/common/logo";
import { NAV_SECTIONS } from "@/config/navigation";
import { useAuthContext } from "@/context/auth-context";
import { cn } from "@/lib/utils";

export function MobileNav() {
  const [open, setOpen] = useState(false);
  const pathname = usePathname();
  const { user } = useAuthContext();

  return (
    <Sheet open={open} onOpenChange={setOpen}>
      <SheetTrigger asChild>
        <Button variant="ghost" size="icon" className="lg:hidden" aria-label="Open navigation">
          <Menu className="size-5" />
        </Button>
      </SheetTrigger>
      <SheetContent side="left" className="w-72 p-0">
        <SheetHeader className="border-b border-border px-5 py-4">
          <Logo />
          <SheetTitle className="sr-only">Main navigation</SheetTitle>
        </SheetHeader>
        <nav className="space-y-6 overflow-y-auto px-3 py-4">
          {NAV_SECTIONS.map((section) => {
            const items = section.items.filter((item) => !item.roles || (user && item.roles.includes(user.role)));
            if (items.length === 0) return null;
            return (
              <div key={section.title} className="space-y-1">
                <p className="px-3 text-xs font-medium uppercase tracking-wider text-muted-foreground">{section.title}</p>
                {items.map((item) => {
                  const isActive = pathname === item.href;
                  const Icon = item.icon;
                  return (
                    <Link
                      key={item.href}
                      href={item.href}
                      onClick={() => setOpen(false)}
                      className={cn(
                        "flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition-colors",
                        isActive
                          ? "bg-primary/10 text-primary"
                          : "text-muted-foreground hover:bg-secondary hover:text-foreground"
                      )}
                    >
                      <Icon className="size-4 shrink-0" />
                      <span className="flex-1 truncate">{item.title}</span>
                    </Link>
                  );
                })}
              </div>
            );
          })}
        </nav>
      </SheetContent>
    </Sheet>
  );
}
