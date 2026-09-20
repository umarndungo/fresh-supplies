import type { Metadata } from "next";
import Link from "next/link";
import { LoginForm } from "@/components/auth/login-form";
import { ROUTES } from "@/lib/constants";

export const metadata: Metadata = { title: "Sign in" };

export default function LoginPage() {
  return (
    <div className="space-y-6">
      <div className="space-y-2 text-center">
        <h2 className="font-display text-2xl font-semibold">Welcome back</h2>
        <p className="text-sm text-muted-foreground">Sign in to your Fresh Supplies workspace.</p>
      </div>
      <LoginForm />
      <p className="text-center text-sm text-muted-foreground">
        First time signing in?{" "}
        <Link href={ROUTES.otpLogin} className="font-medium text-primary hover:underline">
          Email me a sign-in code
        </Link>
      </p>
      <p className="text-center text-sm text-muted-foreground">
        Don&apos;t have an account? Contact your administrator to get added.
      </p>
    </div>
  );
}
