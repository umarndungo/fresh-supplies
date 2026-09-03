"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuthContext } from "@/context/auth-context";
import { DashboardSkeleton } from "@/components/common/dashboard-skeleton";
import { ROUTES } from "@/lib/constants";
import { env } from "@/lib/env";

export function AuthGuard({ children }: { children: React.ReactNode }) {
  const { status } = useAuthContext();
  const router = useRouter();

  useEffect(() => {
    if (env.NEXT_PUBLIC_DEV_AUTH_BYPASS) return;
    if (status === "unauthenticated") {
      router.replace(ROUTES.login);
    }
  }, [status, router]);

  if (env.NEXT_PUBLIC_DEV_AUTH_BYPASS) {
    return <>{children}</>;
  }

  if (status === "loading" || status === "unauthenticated") {
    return (
      <div className="flex min-h-screen items-center justify-center bg-background p-6">
        <div className="w-full max-w-5xl">
          <DashboardSkeleton />
        </div>
      </div>
    );
  }

  return <>{children}</>;
}
