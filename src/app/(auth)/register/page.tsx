import type { Metadata } from "next";
import Link from "next/link";
import { RegisterForm } from "@/components/auth/register-form";
import { ROUTES } from "@/lib/constants";

export const metadata: Metadata = { title: "Create account" };

export default function RegisterPage() {
  return (
    <div className="space-y-6">
      <div className="space-y-2 text-center">
        <h2 className="font-display text-2xl font-semibold">Create your workspace account</h2>
        <p className="text-sm text-muted-foreground">Join your organization on FreshRoute AI.</p>
      </div>
      <RegisterForm />
      <p className="text-center text-sm text-muted-foreground">
        Already have an account?{" "}
        <Link href={ROUTES.login} className="font-medium text-primary hover:underline">
          Sign in
        </Link>
      </p>
    </div>
  );
}
