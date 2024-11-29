from django.db import models
from .users import User, Group, Workspace

class Message(models.Model):
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
    sender_id = models.ForeignKey(User, on_delete=models.CASCADE)
    body = models.TextField()

class MessageRecipient(models.Model):
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
    conversation_id = models.ForeignKey(Group, on_delete=models.CASCADE)
    recipient_id = models.ForeignKey(User, on_delete=models.CASCADE)
    message_id = models.ForeignKey(Message, on_delete=models.CASCADE)

class Announcement(models.Model):
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
    sender_id = models.ForeignKey(User, on_delete=models.CASCADE)
    body = models.TextField()
    workspace_id = models.ForeignKey(Workspace, on_delete=models.CASCADE)