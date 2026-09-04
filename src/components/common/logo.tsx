import { cn } from "@/lib/utils";

interface LogoProps {
  variant?: "default" | "light";
  className?: string;
  showWordmark?: boolean;
}

export function Logo({ variant = "default", className, showWordmark = true }: LogoProps) {
  const isLight = variant === "light";
  return (
    <div className={cn("flex items-center gap-2.5", className)}>
      <svg width="28" height="28" viewBox="0 0 32 32" fill="none" aria-hidden="true">
        <path
          d="M16 2C9.4 8.2 6 14 6 19.2 6 25.2 10.5 30 16 30s10-4.8 10-10.8C26 14 22.6 8.2 16 2Z"
          className={isLight ? "fill-white/15" : "fill-primary/15"}
        />
        <path
          d="M16 6.4C11.4 11 9 15.3 9 19.2c0 4.4 3.2 7.8 7 7.8s7-3.4 7-7.8C23 15.3 20.6 11 16 6.4Z"
          className={isLight ? "fill-white" : "fill-primary"}
        />
        <circle cx="16" cy="19" r="2.4" className={isLight ? "fill-primary" : "fill-accent"} />
      </svg>
      {showWordmark ? (
        <span className={cn("font-display text-lg font-semibold tracking-tight", isLight ? "text-white" : "text-foreground")}>
          Fresh Supplies
        </span>
      ) : null}
    </div>
  );
}
