"use client";

import { useState } from "react";
import { Loader2, Plus, UserRoundPlus, Users } from "lucide-react";
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
  DialogBody,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { useAuthContext } from "@/context/auth-context";
import { useCooperativeMembers, useCreateCooperativeMember } from "@/hooks/use-cooperative-members";
import { formatDate, getInitials } from "@/lib/utils";

type MemberRole = "FARMER_COOPERATIVE" | "DRIVER";

const ROLE_LABELS: Record<MemberRole, string> = {
  FARMER_COOPERATIVE: "Member",
  DRIVER: "Driver",
};

function AddMemberDialog() {
  const [open, setOpen] = useState(false);
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [role, setRole] = useState<MemberRole>("FARMER_COOPERATIVE");
  const [error, setError] = useState<string | null>(null);
  const createMember = useCreateCooperativeMember();

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
      await createMember.mutateAsync({ fullName: fullName.trim(), email: email.trim(), role });
      setOpen(false);
      setFullName("");
      setEmail("");
      setRole("FARMER_COOPERATIVE");
    } catch {
      // Surfaced via toast in useCreateCooperativeMember's onError handler.
    }
  }

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button size="sm">
          <UserRoundPlus className="size-4" />
          Add member
        </Button>
      </DialogTrigger>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Add to your cooperative</DialogTitle>
          <DialogDescription>
            They&apos;ll get an email with a sign-in code and set their own password on first login.
          </DialogDescription>
        </DialogHeader>
        <DialogBody className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="member-name">Full name</Label>
            <Input id="member-name" value={fullName} onChange={(e) => setFullName(e.target.value)} placeholder="Grace Gathoni" />
          </div>
          <div className="space-y-2">
            <Label htmlFor="member-email">Email</Label>
            <Input id="member-email" type="email" value={email} onChange={(e) => setEmail(e.target.value)} placeholder="grace@coop.ke" />
          </div>
          <div className="space-y-2">
            <Label>Role</Label>
            <Select value={role} onValueChange={(value) => setRole(value as MemberRole)}>
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="FARMER_COOPERATIVE">Member</SelectItem>
                <SelectItem value="DRIVER">Driver</SelectItem>
              </SelectContent>
            </Select>
          </div>
          {error ? <p className="text-sm text-destructive">{error}</p> : null}
        </DialogBody>
        <DialogFooter>
          <Button onClick={handleSubmit} disabled={createMember.isPending}>
            {createMember.isPending ? <Loader2 className="size-4 animate-spin mr-2" /> : <Plus className="size-4 mr-2" />}
            Add member
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}

export default function CooperativeMembersPage() {
  const { user } = useAuthContext();
  const isCooperativeAdmin = user?.role === "FARMER_COOPERATIVE" && user?.cooperativeRole === "ADMIN";
  const { data: members, isLoading, isError, refetch } = useCooperativeMembers();

  if (!isCooperativeAdmin) {
    return (
      <ErrorState
        title="Cooperative admins only"
        description="You need to be your cooperative's admin to manage its members."
      />
    );
  }

  return (
    <div className="space-y-6">
      <PageHeader
        title="Cooperative Team"
        description="Add members and drivers to your cooperative"
        actions={<AddMemberDialog />}
      />

      <Card>
        <CardHeader>
          <CardTitle>Members &amp; drivers</CardTitle>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="space-y-3">
              {[1, 2, 3].map((i) => (
                <Skeleton key={i} className="h-12 w-full" />
              ))}
            </div>
          ) : isError ? (
            <ErrorState title="Couldn't load your team" description="The member list could not be fetched." onRetry={() => void refetch()} />
          ) : !members || members.length === 0 ? (
            <EmptyState
              icon={Users}
              title="No members yet"
              description="Add your first member or driver to get started."
              action={<AddMemberDialog />}
            />
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Name</TableHead>
                  <TableHead>Role</TableHead>
                  <TableHead>Joined</TableHead>
                  <TableHead>Status</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {members.map((member) => (
                  <TableRow key={member.id}>
                    <TableCell>
                      <div className="flex items-center gap-3">
                        <Avatar className="size-9">
                          <AvatarFallback>{getInitials(member.fullName)}</AvatarFallback>
                        </Avatar>
                        <div>
                          <div className="font-medium">{member.fullName}</div>
                          <div className="text-xs text-muted-foreground">{member.email}</div>
                        </div>
                      </div>
                    </TableCell>
                    <TableCell>
                      <Badge variant={member.role === "DRIVER" ? "secondary" : "default"}>
                        {member.role === "DRIVER" ? ROLE_LABELS.DRIVER : member.cooperativeRole === "ADMIN" ? "Admin" : ROLE_LABELS.FARMER_COOPERATIVE}
                      </Badge>
                    </TableCell>
                    <TableCell className="text-muted-foreground">{formatDate(member.createdAt)}</TableCell>
                    <TableCell>
                      <Badge variant={member.profileCompleted ? "success" : "secondary"}>
                        {member.profileCompleted ? "Active" : "Invited"}
                      </Badge>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
