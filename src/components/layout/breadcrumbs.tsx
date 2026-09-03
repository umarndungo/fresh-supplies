"use client";

import { Fragment } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { ChevronRight, Home } from "lucide-react";

function toLabel(segment: string): string {
  return segment.replace(/-/g, " ").replace(/\b\w/g, (char) => char.toUpperCase());
}

export function Breadcrumbs() {
  const pathname = usePathname();
  const segments = pathname.split("/").filter(Boolean);

  if (segments.length <= 1) {
    return (
      <div className="flex items-center gap-1.5 text-sm text-muted-foreground">
        <Home className="size-3.5" />
        <span className="font-medium text-foreground">Overview</span>
      </div>
    );
  }

  return (
    <nav aria-label="Breadcrumb" className="flex items-center gap-1.5 text-sm text-muted-foreground">
      <Link href="/dashboard" className="flex items-center hover:text-foreground">
        <Home className="size-3.5" />
      </Link>
      {segments.map((segment, index) => {
        const href = `/${segments.slice(0, index + 1).join("/")}`;
        const isLast = index === segments.length - 1;
        return (
          <Fragment key={href}>
            <ChevronRight className="size-3.5" />
            {isLast ? (
              <span className="font-medium text-foreground">{toLabel(segment)}</span>
            ) : (
              <Link href={href} className="hover:text-foreground">
                {toLabel(segment)}
              </Link>
            )}
          </Fragment>
        );
      })}
    </nav>
  );
}
