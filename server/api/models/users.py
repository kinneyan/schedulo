from django.db import models

class User(models.Model):
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
    fname = models.CharField(max_length=30)
    lname = models.CharField(max_length=30)
    phone = models.CharField(max_length=30, null=True, blank=True)
    email = models.EmailField(max_length=100)
    password = models.CharField(max_length=100)