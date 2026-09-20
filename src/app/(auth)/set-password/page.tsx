import type { Metadata } from "next";
import { SetPasswordForm } from "@/components/auth/set-password-form";

export const metadata: Metadata = { title: "Set your password" };

export default function SetPasswordPage() {
  return (
    <div className="space-y-6">
      <div className="space-y-2 text-center">
        <h2 className="font-display text-2xl font-semibold">Set your password</h2>
        <p className="text-sm text-muted-foreground">
          You&apos;re signed in — choose a password so you can sign in directly next time.
        </p>
      </div>
      <SetPasswordForm />
    </div>
  );
}
