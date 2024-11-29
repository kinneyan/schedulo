from django.db import models

class User(models.Model):
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
    fname = models.CharField(max_length=30)
    lname = models.CharField(max_length=30)
    phone = models.CharField(max_length=30, null=True, blank=True)
    email = models.EmailField(max_length=100)
    password = models.CharField(max_length=100)

class Workspace(models.Model):
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
    created_by_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_workspaces')
    owner_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_workspaces')

class WorkspaceMember(models.Model):
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
    workspace_id = models.ForeignKey(Workspace, on_delete=models.CASCADE, related_name='members')
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name='workspaces')
    added_by_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name='added_members')
    pay_rate = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    # role_id = models.ForeignKey(Role, on_delete=models.CASCADE, null=True)    

class Group(models.Model):
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
    name = models.CharField(max_length=30, blank=True)

class GroupMember(models.Model):
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
    group_id = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='members')
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name='groups')
