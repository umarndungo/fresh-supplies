"use client";

import { useState } from "react";
import { Building2, Check, Pencil, Plus } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Dialog, DialogBody, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Skeleton } from "@/components/ui/skeleton";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { EmptyState } from "@/components/common/empty-state";
import { ErrorState } from "@/components/common/error-state";
import { PageHeader } from "@/components/common/page-header";
import { RoleGate } from "@/components/auth/role-gate";
import { useCreateTenant, useTenantUsage, useTenants, useUpdateTenant } from "@/hooks/use-tenants";

function CreateTenantDialog() {
  const [open, setOpen] = useState(false);
  const [name, setName] = useState("");
  const [adminFullName, setAdminFullName] = useState("");
  const [adminEmail, setAdminEmail] = useState("");
  const createTenant = useCreateTenant();

  const hasAdminName = adminFullName.trim().length >= 2;
  const hasAdminEmail = adminEmail.includes("@");
  const adminFieldsValid = (!adminFullName && !adminEmail) || (hasAdminName && hasAdminEmail);

  async function handleSubmit() {
    if (name.trim().length < 2 || !adminFieldsValid) return;
    await createTenant.mutateAsync({
      name: name.trim(),
      adminFullName: hasAdminName ? adminFullName.trim() : undefined,
      adminEmail: hasAdminEmail ? adminEmail.trim() : undefined,
    });
    setName("");
    setAdminFullName("");
    setAdminEmail("");
    setOpen(false);
  }

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button size="sm"><Plus className="size-4" />Create tenant</Button>
      </DialogTrigger>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Create tenant</DialogTitle>
          <DialogDescription>
            Optionally provision the cooperative&apos;s admin in the same step — they&apos;ll get an email to sign in.
          </DialogDescription>
        </DialogHeader>
        <DialogBody className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="tenant-name">Tenant name</Label>
            <Input id="tenant-name" value={name} onChange={(event) => setName(event.target.value)} placeholder="Nyeri Farmers Cooperative" />
          </div>
          <div className="space-y-2">
            <Label htmlFor="tenant-admin-name">Cooperative admin name (optional)</Label>
            <Input id="tenant-admin-name" value={adminFullName} onChange={(event) => setAdminFullName(event.target.value)} placeholder="Grace Gathoni" />
          </div>
          <div className="space-y-2">
            <Label htmlFor="tenant-admin-email">Cooperative admin email (optional)</Label>
            <Input id="tenant-admin-email" type="email" value={adminEmail} onChange={(event) => setAdminEmail(event.target.value)} placeholder="grace@coop.ke" />
          </div>
          {!adminFieldsValid ? (
            <p className="text-sm text-destructive">Provide both the admin&apos;s name and email, or leave both blank.</p>
          ) : null}
        </DialogBody>
        <DialogFooter>
          <Button onClick={() => void handleSubmit()} disabled={createTenant.isPending || name.trim().length < 2 || !adminFieldsValid}>Create tenant</Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}

function TenantNameCell({ id, name }: { id: string; name: string }) {
  const [editing, setEditing] = useState(false);
  const [value, setValue] = useState(name);
  const updateTenant = useUpdateTenant();

  async function save() {
    if (value.trim().length < 2 || value.trim() === name) {
      setEditing(false);
      return;
    }
    await updateTenant.mutateAsync({ id, name: value.trim() });
    setEditing(false);
  }

  if (!editing) {
    return (
      <div className="flex items-center gap-2">
        <span className="font-medium">{name}</span>
        <Button variant="ghost" size="icon" onClick={() => setEditing(true)} title="Rename tenant"><Pencil className="size-4" /></Button>
      </div>
    );
  }

  return (
    <div className="flex max-w-sm items-center gap-2">
      <Input value={value} onChange={(event) => setValue(event.target.value)} aria-label={`Rename ${name}`} />
      <Button variant="ghost" size="icon" onClick={() => void save()} disabled={updateTenant.isPending} title="Save tenant name"><Check className="size-4" /></Button>
    </div>
  );
}

export default function AdminTenantsPage() {
  const tenantsQuery = useTenants();
  const usageQuery = useTenantUsage();
  const isLoading = tenantsQuery.isLoading || usageQuery.isLoading;
  const isError = tenantsQuery.isError || usageQuery.isError;
  const usageByTenant = new Map((usageQuery.data ?? []).map((usage) => [usage.cooperativeId, usage]));

  return (
    <RoleGate allowed={["ADMINISTRATOR"]}>
      <div className="space-y-6">
        <PageHeader title="Tenants" description="Manage cooperative tenants and aggregate billing usage" actions={<CreateTenantDialog />} />
        <Card>
          <CardContent className="pt-6">
            {isLoading ? (
              <div className="space-y-3">{[1, 2, 3].map((item) => <Skeleton key={item} className="h-12 w-full" />)}</div>
            ) : isError ? (
              <ErrorState title="Couldn't load tenants" description="Tenant metadata and usage could not be fetched." onRetry={() => { void tenantsQuery.refetch(); void usageQuery.refetch(); }} />
            ) : !tenantsQuery.data || tenantsQuery.data.length === 0 ? (
              <EmptyState icon={Building2} title="No tenants yet" description="Create a tenant to begin managing cooperative access." action={<CreateTenantDialog />} />
            ) : (
              <Table>
                <TableHeader><TableRow><TableHead>Tenant</TableHead><TableHead>Members</TableHead><TableHead>Shipments</TableHead><TableHead>Produce</TableHead><TableHead className="text-right">Total kg</TableHead></TableRow></TableHeader>
                <TableBody>
                  {tenantsQuery.data.map((tenant) => {
                    const usage = usageByTenant.get(tenant.id);
                    return <TableRow key={tenant.id}><TableCell><TenantNameCell id={tenant.id} name={tenant.name} /></TableCell><TableCell>{usage?.memberCount ?? 0}</TableCell><TableCell>{usage?.shipmentCount ?? 0}</TableCell><TableCell>{usage?.produceItemCount ?? 0}</TableCell><TableCell className="text-right">{(usage?.totalQuantityKg ?? 0).toLocaleString()}</TableCell></TableRow>;
                  })}
                </TableBody>
              </Table>
            )}
          </CardContent>
        </Card>
      </div>
    </RoleGate>
  );
}
