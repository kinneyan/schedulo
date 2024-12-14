from django.db import models
from .users import Workspace, WorkspaceMember

class WorkspaceRole(models.Model):
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
    workspace_id = models.ForeignKey(Workspace, on_delete=models.CASCADE)
    name = models.CharField(max_length=30)
    pay_rate = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

class MemberRole(models.Model):
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
    workspace_role_id = models.ForeignKey(WorkspaceRole, on_delete=models.CASCADE)
    member_id = models.ForeignKey(WorkspaceMember, on_delete=models.CASCADE)

class MemberPermissions(models.Model):
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
    workspace_role_id = models.ForeignKey(WorkspaceRole, on_delete=models.CASCADE)
    member_id = models.OneToOneField(WorkspaceMember, on_delete=models.CASCADE)

    # Permissions
    IS_OWNER = models.BooleanField(default=False)
    MANAGE_WORKSPACE_MEMBERS = models.BooleanField(default=False)
    MANAGE_WORKSPACE_ROLES = models.BooleanField(default=False)
    MANAGE_SCHEDULES = models.BooleanField(default=False)
    MANAGE_TIME_OFF = models.BooleanField(default=False)
