from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
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

class ShiftRequest(models.Model):
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
    sender_id = models.ForeignKey(WorkspaceMember, on_delete=models.CASCADE, related_name='sent_shift_requests')
    recipient_id = models.ForeignKey(WorkspaceMember, on_delete=models.CASCADE, related_name='received_shift_requests')
    sender_shift_id = models.ForeignKey(Shift, on_delete=models.CASCADE, related_name='shift_requests')
    recipient_shift_id = models.ForeignKey(Shift, on_delete=models.CASCADE, null=True, blank=True)
    accepted = models.BooleanField(default=False)
    approved = models.BooleanField(default=False)

class TimeOffRequest(models.Model):
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
    member_id = models.ForeignKey(WorkspaceMember, on_delete=models.CASCADE)
    workspace_id = models.ForeignKey(Workspace, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    approved = models.BooleanField(default=False)
    reason = models.TextField(blank=True)
    approved_by_id = models.ForeignKey(WorkspaceMember, on_delete=models.CASCADE, related_name='approved_time_off_requests', null=True, blank=True)

class Unavailability(models.Model):
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
    member_id = models.ForeignKey(WorkspaceMember, on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    day_of_week = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(6)])

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=models.Q(day_of_week__gte=0) & models.Q(day_of_week__lte=6),
                name="day_of_week_valid",
            )
        ]
