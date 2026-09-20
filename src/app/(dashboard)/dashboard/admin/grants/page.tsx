"use client";

import { useMemo, useState } from "react";
import { KeyRound, Trash2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Skeleton } from "@/components/ui/skeleton";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { EmptyState } from "@/components/common/empty-state";
import { ErrorState } from "@/components/common/error-state";
import { PageHeader } from "@/components/common/page-header";
import { RoleGate } from "@/components/auth/role-gate";
import { useAdminUsers } from "@/hooks/use-admin";
import { useCreateGrant, useRevokeGrant, useTenantGrants } from "@/hooks/use-grants";
import { useTenants } from "@/hooks/use-tenants";
import type { UserRole } from "@/types/auth.types";

const GRANT_ROLES: UserRole[] = ["LOGISTICS_MANAGER", "MARKET_ANALYST"];

export default function AdminGrantsPage() {
  const usersQuery = useAdminUsers();
  const tenantsQuery = useTenants();
  const [tenantId, setTenantId] = useState<string>("");
  const [userId, setUserId] = useState<string>("");
  const [search, setSearch] = useState("");
  const createGrant = useCreateGrant();
  const revokeGrant = useRevokeGrant();
  const grantsQuery = useTenantGrants(tenantId || undefined);

  const eligibleUsers = useMemo(() => {
    const normalized = search.trim().toLowerCase();
    return (usersQuery.data ?? []).filter((user) => {
      if (!GRANT_ROLES.includes(user.role)) return false;
      return !normalized || `${user.fullName} ${user.email}`.toLowerCase().includes(normalized);
    });
  }, [search, usersQuery.data]);

  async function submitGrant() {
    if (!userId || !tenantId) return;
    await createGrant.mutateAsync({ userId, cooperativeId: tenantId });
    setUserId("");
  }

  const isLoading = usersQuery.isLoading || tenantsQuery.isLoading;
  const isError = usersQuery.isError || tenantsQuery.isError;
  const selectedTenant = tenantsQuery.data?.find((tenant) => tenant.id === tenantId);

  return (
    <RoleGate allowed={["ADMINISTRATOR"]}>
      <div className="space-y-6">
        <PageHeader title="Access Grants" description="Give logistics and market staff access to specific cooperative tenants" />
        <Card>
          <CardHeader><CardTitle>Create access grant</CardTitle></CardHeader>
          <CardContent className="grid gap-4 md:grid-cols-3">
            <div className="space-y-2">
              <Label htmlFor="grant-user-search">Staff user</Label>
              <Input id="grant-user-search" value={search} onChange={(event) => setSearch(event.target.value)} placeholder="Search name or email" />
              <Select value={userId} onValueChange={setUserId}>
                <SelectTrigger><SelectValue placeholder="Select staff user" /></SelectTrigger>
                <SelectContent>{eligibleUsers.map((user) => <SelectItem key={user.id} value={user.id}>{user.fullName} ({user.role === "LOGISTICS_MANAGER" ? "Logistics" : "Market Analyst"})</SelectItem>)}</SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <Label>Tenant</Label>
              <Select value={tenantId} onValueChange={setTenantId}>
                <SelectTrigger><SelectValue placeholder="Select tenant" /></SelectTrigger>
                <SelectContent>{(tenantsQuery.data ?? []).map((tenant) => <SelectItem key={tenant.id} value={tenant.id}>{tenant.name}</SelectItem>)}</SelectContent>
              </Select>
            </div>
            <div className="flex items-end"><Button onClick={() => void submitGrant()} disabled={!userId || !tenantId || createGrant.isPending}>Grant access</Button></div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader><CardTitle>{selectedTenant ? `Grants for ${selectedTenant.name}` : "Existing grants"}</CardTitle></CardHeader>
          <CardContent>
            {isLoading ? <div className="space-y-3">{[1, 2].map((item) => <Skeleton key={item} className="h-12 w-full" />)}</div> : isError ? <ErrorState title="Couldn't load access data" description="Users and tenants could not be fetched." onRetry={() => { void usersQuery.refetch(); void tenantsQuery.refetch(); }} /> : !tenantId ? <EmptyState icon={KeyRound} title="Select a tenant" description="Choose a tenant to review and revoke its grants." /> : grantsQuery.isLoading ? <Skeleton className="h-12 w-full" /> : grantsQuery.isError ? <ErrorState title="Couldn't load grants" onRetry={() => void grantsQuery.refetch()} /> : !grantsQuery.data || grantsQuery.data.length === 0 ? <EmptyState icon={KeyRound} title="No grants for this tenant" description="Use the form above to grant staff access." /> : (
              <Table>
                <TableHeader><TableRow><TableHead>User</TableHead><TableHead>Granted</TableHead><TableHead className="text-right">Actions</TableHead></TableRow></TableHeader>
                <TableBody>{grantsQuery.data.map((grant) => { const user = usersQuery.data?.find((item) => item.id === grant.userId); return <TableRow key={grant.id}><TableCell>{user ? `${user.fullName} (${user.email})` : grant.userId}</TableCell><TableCell>{new Date(grant.createdAt).toLocaleDateString()}</TableCell><TableCell className="text-right"><Button variant="ghost" size="icon" title="Revoke access" disabled={revokeGrant.isPending} onClick={() => void revokeGrant.mutateAsync({ id: grant.id, cooperativeId: grant.cooperativeId })}><Trash2 className="size-4 text-destructive" /></Button></TableCell></TableRow>; })}</TableBody>
              </Table>
            )}
          </CardContent>
        </Card>
      </div>
    </RoleGate>
  );
}
