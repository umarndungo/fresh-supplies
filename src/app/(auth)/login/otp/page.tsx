import type { Metadata } from "next";
import Link from "next/link";
import { OtpLoginForm } from "@/components/auth/otp-login-form";
import { ROUTES } from "@/lib/constants";

export const metadata: Metadata = { title: "Email sign-in code" };

export default function OtpLoginPage() {
  return (
    <div className="space-y-6">
      <div className="space-y-2 text-center">
        <h2 className="font-display text-2xl font-semibold">Sign in with a code</h2>
        <p className="text-sm text-muted-foreground">
          For your first sign-in, or if you&apos;ve forgotten your password.
        </p>
      </div>
      <OtpLoginForm />
      <p className="text-center text-sm text-muted-foreground">
        Have a password?{" "}
        <Link href={ROUTES.login} className="font-medium text-primary hover:underline">
          Sign in instead
        </Link>
      </p>
    </div>
  );
}
