"use client";

import { AlertCircle, Users, Construction } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { PageHeader } from "@/components/common/page-header";

export default function AdminUsersPage() {
  return (
    <div className="space-y-6">
      <PageHeader
        title="Team & Access"
        description="User management and role administration"
      />

      <Card className="max-w-2xl">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Construction className="size-5 text-amber-500" />
            Coming Soon
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4 text-center py-8">
          <Users className="size-16 mx-auto text-muted-foreground/50" />
          <h3 className="text-lg font-medium">User Management Not Yet Available</h3>
          <p className="text-muted-foreground">
            This page requires backend user-management endpoints that are not yet implemented.
          </p>
          <div className="space-y-2 text-sm text-muted-foreground">
            <p>Planned features:</p>
            <ul className="list-disc list-inside space-y-1 text-left max-w-md mx-auto">
              <li>View all users and their roles</li>
              <li>Invite new team members</li>
              <li>Edit user roles and permissions</li>
              <li>Deactivate/reactivate accounts</li>
              <li>Audit log of user actions</li>
            </ul>
          </div>
          <div className="pt-4 border-t">
            <p className="text-sm text-muted-foreground mb-2">
              Backend endpoints needed:
            </p>
            <div className="bg-muted p-3 rounded text-xs font-mono text-left space-y-1">
              <code>GET    /api/v1/admin/users</code>
              <br />
              <code>POST   /api/v1/admin/users</code>
              <br />
              <code>PATCH  /api/v1/admin/users/&#123;id&#125;</code>
              <br />
              <code>DELETE /api/v1/admin/users/&#123;id&#125;</code>
            </div>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <AlertCircle className="size-5 text-blue-500" />
            Current User Info
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground">
            You are currently viewing this page as a user with the <strong>ADMINISTRATOR</strong> role.
            The navigation shows this item because your role has access, but the backend functionality
            is not yet implemented.
          </p>
        </CardContent>
      </Card>
    </div>
  );
}