"use client";

import { PageHeader } from "@/components/common/page-header";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { useAuthContext } from "@/context/auth-context";
import { ROLE_LABELS } from "@/lib/constants";
import { formatDate } from "@/lib/utils";

export default function DashboardOverviewPage() {
  const { user } = useAuthContext();

  if (!user) return null;

  return (
    <div className="space-y-6">
      <PageHeader
        title={`Welcome back, ${user.fullName.split(" ")[0]}`}
        description="Here's a snapshot of your Fresh Supplies account."
      />
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        <Card>
          <CardHeader>
            <CardDescription>Role</CardDescription>
            <CardTitle>{ROLE_LABELS[user.role]}</CardTitle>
          </CardHeader>
          <CardContent>
            <Badge variant="secondary">{user.email}</Badge>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardDescription>Organization</CardDescription>
            <CardTitle>{user.organizationName ?? "Not linked yet"}</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground">
              Cooperative and fleet details will appear here once your organization profile is connected.
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardDescription>Member since</CardDescription>
            <CardTitle>{formatDate(user.createdAt)}</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground">
              Spoilage forecasts, market recommendations, and route plans will populate this workspace next.
            </p>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
