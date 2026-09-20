"use client";

import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form";
import { otpCodeSchema, otpEmailSchema, type OtpCodeFormValues, type OtpEmailFormValues } from "@/lib/validators/auth.schema";
import { useAuth } from "@/hooks/use-auth";

export function OtpLoginForm() {
  const [email, setEmail] = useState<string | null>(null);
  const { requestOtp, isRequestingOtp, verifyOtp, isVerifyingOtp } = useAuth();

  const emailForm = useForm<OtpEmailFormValues>({
    resolver: zodResolver(otpEmailSchema),
    defaultValues: { email: "" },
  });
  const codeForm = useForm<OtpCodeFormValues>({
    resolver: zodResolver(otpCodeSchema),
    defaultValues: { code: "" },
  });

  async function onRequestOtp(values: OtpEmailFormValues) {
    try {
      await requestOtp(values.email);
      setEmail(values.email);
    } catch {
      // Surfaced via toast in useAuth's onError handler.
    }
  }

  async function onVerifyOtp(values: OtpCodeFormValues) {
    if (!email) return;
    try {
      await verifyOtp({ email, code: values.code });
    } catch {
      // Surfaced via toast in useAuth's onError handler.
    }
  }

  if (!email) {
    return (
      <Form {...emailForm}>
        <form onSubmit={emailForm.handleSubmit(onRequestOtp)} className="space-y-4" noValidate>
          <FormField
            control={emailForm.control}
            name="email"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Email</FormLabel>
                <FormControl>
                  <Input type="email" placeholder="you@cooperative.com" autoComplete="email" {...field} />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />
          <Button type="submit" className="w-full" disabled={isRequestingOtp}>
            {isRequestingOtp ? <Loader2 className="size-4 animate-spin" /> : null}
            Send sign-in code
          </Button>
        </form>
      </Form>
    );
  }

  return (
    <Form {...codeForm}>
      <form onSubmit={codeForm.handleSubmit(onVerifyOtp)} className="space-y-4" noValidate>
        <p className="text-sm text-muted-foreground">
          We sent a 6-digit code to <span className="font-medium text-foreground">{email}</span>.
        </p>
        <FormField
          control={codeForm.control}
          name="code"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Code</FormLabel>
              <FormControl>
                <Input inputMode="numeric" placeholder="123456" maxLength={6} autoComplete="one-time-code" {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />
        <Button type="submit" className="w-full" disabled={isVerifyingOtp}>
          {isVerifyingOtp ? <Loader2 className="size-4 animate-spin" /> : null}
          Verify code
        </Button>
        <Button
          type="button"
          variant="ghost"
          className="w-full"
          onClick={() => {
            setEmail(null);
            codeForm.reset();
          }}
        >
          Use a different email
        </Button>
      </form>
    </Form>
  );
}
