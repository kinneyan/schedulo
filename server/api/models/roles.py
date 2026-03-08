from django.db import models
from .users import Workspace, WorkspaceMember


class WorkspaceRole(models.Model):
    """A named role within a workspace, optionally associated with a pay rate."""

    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE)
    name = models.CharField(max_length=30, default="Unnamed Role")
    pay_rate = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True
    )


class MemberRole(models.Model):
    """An assignment of a WorkspaceRole to a WorkspaceMember."""

    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
    workspace_role = models.ForeignKey(WorkspaceRole, on_delete=models.CASCADE)
    member = models.ForeignKey(WorkspaceMember, on_delete=models.CASCADE)


class MemberPermissions(models.Model):
    """Permission flags controlling what actions a WorkspaceMember can perform."""

    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE, null=True)
    member = models.OneToOneField(WorkspaceMember, on_delete=models.CASCADE)

    # Permissions
    is_owner = models.BooleanField(default=False)
    manage_workspace_members = models.BooleanField(default=False)
    manage_workspace_roles = models.BooleanField(default=False)
    manage_schedules = models.BooleanField(default=False)
    manage_time_off = models.BooleanField(default=False)
