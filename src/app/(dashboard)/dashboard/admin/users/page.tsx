"use client";

import { useState } from "react";
import { Loader2, Plus, Shield, UserCog, UserRoundPlus, Trash2, Users } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Skeleton } from "@/components/ui/skeleton";
import { EmptyState } from "@/components/common/empty-state";
import { ErrorState } from "@/components/common/error-state";
import { PageHeader } from "@/components/common/page-header";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogBody,
  DialogTrigger,
} from "@/components/ui/dialog";
import { useCreateAdminUser, useDeleteAdminUser, useAdminUsers, useUpdateAdminUser } from "@/hooks/use-admin";
import { useTenants } from "@/hooks/use-tenants";
import { useAuthContext } from "@/context/auth-context";
import { formatDate, getInitials } from "@/lib/utils";
import type { AdminUser, UserRole } from "@/types/admin.types";
import { USER_ROLE_LABELS, USER_ROLE_OPTIONS } from "@/types/admin.types";

const ROLE_VARIANTS: Record<UserRole, "default" | "secondary" | "warning" | "destructive"> = {
  ADMINISTRATOR: "destructive",
  LOGISTICS_MANAGER: "warning",
  FARMER_COOPERATIVE: "secondary",
  MARKET_ANALYST: "default",
  DRIVER: "secondary",
};

function InviteUserDialog() {
  const [open, setOpen] = useState(false);
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [role, setRole] = useState<UserRole>("FARMER_COOPERATIVE");
  const [organizationName, setOrganizationName] = useState("");
  const [cooperativeId, setCooperativeId] = useState("none");
  const [cooperativeRole, setCooperativeRole] = useState<"MEMBER" | "ADMIN">("MEMBER");
  const [error, setError] = useState<string | null>(null);
  const createUser = useCreateAdminUser();
  const tenantsQuery = useTenants();

  const supportsCooperative = role === "FARMER_COOPERATIVE" || role === "DRIVER";

  async function handleSubmit() {
    setError(null);
    if (fullName.trim().length < 2) {
      setError("Full name is required.");
      return;
    }
    if (!email.includes("@")) {
      setError("A valid email is required.");
      return;
    }
    try {
      await createUser.mutateAsync({
        fullName: fullName.trim(),
        email: email.trim(),
        role,
        organizationName: organizationName.trim() || null,
        cooperativeId: supportsCooperative && cooperativeId !== "none" ? cooperativeId : null,
        cooperativeRole: supportsCooperative && cooperativeId !== "none" && role === "FARMER_COOPERATIVE" ? cooperativeRole : null,
      });
      setOpen(false);
      setFullName("");
      setEmail("");
      setRole("FARMER_COOPERATIVE");
      setOrganizationName("");
      setCooperativeId("none");
      setCooperativeRole("MEMBER");
    } catch {
      // Surfaced via toast in useCreateAdminUser's onError handler.
    }
  }

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button size="sm">
          <UserRoundPlus className="size-4" />
          Invite user
        </Button>
      </DialogTrigger>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Invite a team member</DialogTitle>
          <DialogDescription>
            Creates the account and emails them a sign-in code — they set their own password on first login.
          </DialogDescription>
        </DialogHeader>
        <DialogBody className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="invite-name">Full name</Label>
            <Input id="invite-name" value={fullName} onChange={(e) => setFullName(e.target.value)} placeholder="Grace Gathoni" />
          </div>
          <div className="space-y-2">
            <Label htmlFor="invite-email">Email</Label>
            <Input id="invite-email" type="email" value={email} onChange={(e) => setEmail(e.target.value)} placeholder="grace@coop.ke" />
          </div>
          <div className="space-y-2">
            <Label>Role</Label>
            <Select value={role} onValueChange={(value) => setRole(value as UserRole)}>
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {USER_ROLE_OPTIONS.map((option) => (
                  <SelectItem key={option} value={option}>
                    {USER_ROLE_LABELS[option]}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          <div className="space-y-2">
            <Label htmlFor="invite-org">Organization (optional)</Label>
            <Input id="invite-org" value={organizationName} onChange={(e) => setOrganizationName(e.target.value)} placeholder="Nyeri Farmers Coop" />
          </div>
          {supportsCooperative ? (
            <div className="space-y-2">
              <Label>Cooperative (optional)</Label>
              <Select value={cooperativeId} onValueChange={setCooperativeId}>
                <SelectTrigger><SelectValue placeholder="No cooperative" /></SelectTrigger>
                <SelectContent>
                  <SelectItem value="none">None — solo tenant</SelectItem>
                  {(tenantsQuery.data ?? []).map((tenant) => (
                    <SelectItem key={tenant.id} value={tenant.id}>{tenant.name}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          ) : null}
          {supportsCooperative && cooperativeId !== "none" && role === "FARMER_COOPERATIVE" ? (
            <div className="space-y-2">
              <Label>Cooperative role</Label>
              <Select value={cooperativeRole} onValueChange={(value) => setCooperativeRole(value as "MEMBER" | "ADMIN")}>
                <SelectTrigger><SelectValue /></SelectTrigger>
                <SelectContent>
                  <SelectItem value="MEMBER">Member</SelectItem>
                  <SelectItem value="ADMIN">Admin</SelectItem>
                </SelectContent>
              </Select>
            </div>
          ) : null}
          {error ? <p className="text-sm text-destructive">{error}</p> : null}
        </DialogBody>
        <DialogFooter>
          <Button onClick={handleSubmit} disabled={createUser.isPending}>
            {createUser.isPending ? <Loader2 className="size-4 animate-spin mr-2" /> : <Plus className="size-4 mr-2" />}
            Invite user
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}

interface EditUserDialogProps {
  user: AdminUser;
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

function EditUserDialog({ user, open, onOpenChange }: EditUserDialogProps) {
  const [fullName, setFullName] = useState(user.fullName);
  const [organizationName, setOrganizationName] = useState(user.organizationName ?? "");
  const [role, setRole] = useState<UserRole>(user.role);
  const [cooperativeId, setCooperativeId] = useState(user.cooperativeId ?? "none");
  const [cooperativeRole, setCooperativeRole] = useState<"MEMBER" | "ADMIN">(user.cooperativeRole ?? "MEMBER");
  const [isActive, setIsActive] = useState(user.isActive);
  const [resetPassword, setResetPassword] = useState("");
  const { user: currentUser } = useAuthContext();
  const updateUser = useUpdateAdminUser();
  const tenantsQuery = useTenants();

  const isSelf = currentUser?.id === user.id;
  const supportsCooperative = role === "FARMER_COOPERATIVE" || role === "DRIVER";

  async function handleSubmit() {
    try {
      await updateUser.mutateAsync({
        id: user.id,
        payload: {
          fullName: fullName.trim() || undefined,
          organizationName: organizationName.trim() || undefined,
          role,
          cooperativeId: supportsCooperative && cooperativeId !== "none" ? cooperativeId : null,
          cooperativeRole:
            supportsCooperative && cooperativeId !== "none" && role === "FARMER_COOPERATIVE" ? cooperativeRole : null,
          isActive,
          resetPassword: resetPassword.trim() || undefined,
        },
      });
      onOpenChange(false);
    } catch {
      // Surfaced via toast.
    }
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Edit {user.fullName}</DialogTitle>
          <DialogDescription>{user.email}</DialogDescription>
        </DialogHeader>
        <DialogBody className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="edit-name">Full name</Label>
            <Input id="edit-name" value={fullName} onChange={(e) => setFullName(e.target.value)} />
          </div>
          <div className="space-y-2">
            <Label htmlFor="edit-org">Organization</Label>
            <Input id="edit-org" value={organizationName} onChange={(e) => setOrganizationName(e.target.value)} />
          </div>
          <div className="space-y-2">
            <Label>Role</Label>
            <Select value={role} onValueChange={(value) => setRole(value as UserRole)}>
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {USER_ROLE_OPTIONS.map((option) => (
                  <SelectItem key={option} value={option}>
                    {USER_ROLE_LABELS[option]}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          {supportsCooperative ? (
            <>
              <div className="space-y-2">
                <Label>Cooperative</Label>
                <Select value={cooperativeId} onValueChange={(value) => setCooperativeId(value)}>
                  <SelectTrigger><SelectValue placeholder="No cooperative" /></SelectTrigger>
                  <SelectContent>
                    <SelectItem value="none">None</SelectItem>
                    {(tenantsQuery.data ?? []).map((tenant) => <SelectItem key={tenant.id} value={tenant.id}>{tenant.name}</SelectItem>)}
                  </SelectContent>
                </Select>
              </div>
              {role === "FARMER_COOPERATIVE" ? (
                <div className="space-y-2">
                  <Label>Cooperative role</Label>
                  <Select value={cooperativeRole} onValueChange={(value) => setCooperativeRole(value as "MEMBER" | "ADMIN")} disabled={cooperativeId === "none"}>
                    <SelectTrigger><SelectValue /></SelectTrigger>
                    <SelectContent>
                      <SelectItem value="MEMBER">Member</SelectItem>
                      <SelectItem value="ADMIN">Admin</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              ) : null}
            </>
          ) : (role === "LOGISTICS_MANAGER" || role === "MARKET_ANALYST") ? (
            <p className="text-xs text-muted-foreground rounded-md border p-3">
              {USER_ROLE_LABELS[role]} accounts see data by cooperative access grant, not by
              cooperative assignment here. Use{" "}
              <a href="/dashboard/admin/grants" className="underline underline-offset-2">
                Access Grants
              </a>{" "}
              to give this user visibility into a cooperative.
            </p>
          ) : null}
          <div className="flex items-center justify-between rounded-lg border p-3">
            <div>
              <Label htmlFor="edit-active">Account status</Label>
              <p className="text-xs text-muted-foreground">
                {isActive ? "Active — user can sign in." : "Deactivated — sign-in is blocked."}
              </p>
            </div>
            <Button
              id="edit-active"
              type="button"
              variant={isActive ? "destructive" : "default"}
              size="sm"
              disabled={isSelf}
              onClick={() => setIsActive(!isActive)}
            >
              {isActive ? "Deactivate" : "Reactivate"}
            </Button>
          </div>
          <div className="space-y-2">
            <Label htmlFor="edit-password">Reset password (optional)</Label>
            <Input id="edit-password" type="password" value={resetPassword} onChange={(e) => setResetPassword(e.target.value)} placeholder="New temporary password" />
          </div>
        </DialogBody>
        <DialogFooter>
          <Button variant="outline" onClick={() => onOpenChange(false)}>
            Cancel
          </Button>
          <Button onClick={handleSubmit} disabled={updateUser.isPending}>
            {updateUser.isPending ? <Loader2 className="size-4 animate-spin mr-2" /> : null}
            Save changes
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}

export default function AdminUsersPage() {
  const { data: users, isLoading, isError, refetch } = useAdminUsers();
  const { user: currentUser } = useAuthContext();
  const updateUser = useUpdateAdminUser();
  const deleteUser = useDeleteAdminUser();
  const [editing, setEditing] = useState<AdminUser | null>(null);

  async function handleToggleActive(target: AdminUser) {
    try {
      await updateUser.mutateAsync({ id: target.id, payload: { isActive: !target.isActive } });
    } catch {
      // Surfaced via toast.
    }
  }

  async function handleDelete(target: AdminUser) {
    if (!confirm(`Remove ${target.fullName} (${target.email})? This permanently deletes the account.`)) return;
    try {
      await deleteUser.mutateAsync(target.id);
    } catch {
      // Surfaced via toast.
    }
  }

  const activeCount = users?.filter((u) => u.isActive).length ?? 0;

  return (
    <div className="space-y-6">
      <PageHeader
        title="Team & Access"
        description="Invite team members and manage roles and account access"
        actions={<InviteUserDialog />}
      />

      <div className="grid gap-4 sm:grid-cols-3">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Total members</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2 text-2xl font-semibold">
              <Users className="size-5 text-muted-foreground" />
              {isLoading ? <Skeleton className="h-8 w-12" /> : users?.length ?? "—"}
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Active</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2 text-2xl font-semibold">
              <Shield className="size-5 text-green-600" />
              {isLoading ? <Skeleton className="h-8 w-12" /> : activeCount}
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Deactivated</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2 text-2xl font-semibold">
              <UserCog className="size-5 text-muted-foreground" />
              {isLoading ? <Skeleton className="h-8 w-12" /> : (users?.length ?? 0) - activeCount}
            </div>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Members</CardTitle>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="space-y-3">
              {[1, 2, 3].map((i) => (
                <Skeleton key={i} className="h-12 w-full" />
              ))}
            </div>
          ) : isError ? (
            <ErrorState
              title="Couldn't load users"
              description="The user directory could not be fetched. You need the Administrator role to manage team members."
              onRetry={() => void refetch()}
            />
          ) : !users || users.length === 0 ? (
            <EmptyState
              icon={Users}
              title="No team members yet"
              description="Invite your first team member to get started."
              action={<InviteUserDialog />}
            />
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Member</TableHead>
                  <TableHead>Role</TableHead>
                  <TableHead>Organization</TableHead>
                  <TableHead>Joined</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead className="text-right">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {users.map((target) => {
                  const isSelf = currentUser?.id === target.id;
                  return (
                    <TableRow key={target.id}>
                      <TableCell>
                        <div className="flex items-center gap-3">
                          <Avatar className="size-9">
                            <AvatarFallback>{getInitials(target.fullName)}</AvatarFallback>
                          </Avatar>
                          <div>
                            <div className="font-medium">
                              {target.fullName}
                              {isSelf ? <span className="ml-1 text-xs text-muted-foreground">(you)</span> : null}
                            </div>
                            <div className="text-xs text-muted-foreground">{target.email}</div>
                          </div>
                        </div>
                      </TableCell>
                      <TableCell>
                        <Badge variant={ROLE_VARIANTS[target.role]}>{USER_ROLE_LABELS[target.role]}</Badge>
                      </TableCell>
                      <TableCell className="text-muted-foreground">{target.organizationName ?? "—"}</TableCell>
                      <TableCell className="text-muted-foreground">{formatDate(target.createdAt)}</TableCell>
                      <TableCell>
                        <Badge variant={target.isActive ? "success" : "secondary"}>
                          {target.isActive ? "Active" : "Deactivated"}
                        </Badge>
                      </TableCell>
                      <TableCell className="text-right">
                        <div className="flex justify-end gap-2">
                          <Button variant="outline" size="sm" onClick={() => setEditing(target)}>
                            Edit
                          </Button>
                          <Button
                            variant={target.isActive ? "outline" : "default"}
                            size="sm"
                            disabled={isSelf}
                            onClick={() => void handleToggleActive(target)}
                          >
                            {target.isActive ? "Deactivate" : "Reactivate"}
                          </Button>
                          <Button variant="ghost" size="sm" disabled={isSelf} onClick={() => void handleDelete(target)}>
                            <Trash2 className="size-4 text-destructive" />
                            <span className="sr-only">Delete</span>
                          </Button>
                        </div>
                      </TableCell>
                    </TableRow>
                  );
                })}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>

      {editing ? (
        <EditUserDialog
          user={editing}
          open={true}
          onOpenChange={(open) => {
            if (!open) setEditing(null);
          }}
        />
      ) : null}
    </div>
  );
}