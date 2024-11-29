from django.db import models
from .users import Workspace

class WorkspaceRole(models.Model):
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
    workspace_id = models.ForeignKey(Workspace, on_delete=models.CASCADE)
    name = models.CharField(max_length=30)
    pay_rate = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)