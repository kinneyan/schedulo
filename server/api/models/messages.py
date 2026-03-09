from django.db import models
from .users import User, Group, Workspace


class Message(models.Model):
    """A message sent by a user."""

    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    body = models.TextField()


class MessageRecipient(models.Model):
    """A record linking a Message to a recipient User within a Group conversation."""

    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
    conversation = models.ForeignKey(Group, on_delete=models.CASCADE)
    recipient = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.ForeignKey(Message, on_delete=models.CASCADE)


class Announcement(models.Model):
    """A broadcast message sent to all members of a workspace."""

    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    body = models.TextField()
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE)
