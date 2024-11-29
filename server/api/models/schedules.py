from django.db import models
from .users import WorkspaceMember, Workspace
from .roles import WorkspaceRole

class Shift(models.Model):
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
    member_id = models.ForeignKey(WorkspaceMember, on_delete=models.CASCADE)
    workspace_id = models.ForeignKey(Workspace, on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    role_id = models.ForeignKey(WorkspaceRole, on_delete=models.CASCADE)
    created_by_id = models.ForeignKey(WorkspaceMember, on_delete=models.CASCADE, related_name='created_shifts')
    open = models.BooleanField(default=False)

class ShiftRequest(models.model):
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
    sender_id = models.ForeignKey(WorkspaceMember, on_delete=models.CASCADE)
    recipient_id = models.ForeignKey(WorkspaceMember, on_delete=models.CASCADE)
    sender_shift_id = models.ForeignKey(Shift, on_delete=models.CASCADE, related_name='shift_requests')
    recipient_shift_id = models.ForeignKey(Shift, on_delete=models.CASCADE, null=True, blank=True)
    accepted = models.BooleanField(default=False)
    approved = models.BooleanField(default=False)