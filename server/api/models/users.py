from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager


class CustomUserManager(BaseUserManager):
    """Manager for User that uses email as the unique identifier."""

    def create_user(self, email: str, password: str = None, **extra_fields):
        """Create and save a regular user with the given email and password.

        :param str email: Email address for the new user.
        :param str password: Password for the new user.
        :return: The newly created user instance.
        :rtype: User
        :raises ValueError: If email is not provided.
        """
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email: str, password: str = None, **extra_fields):
        """Create and save a superuser with the given email and password.

        :param str email: Email address for the superuser.
        :param str password: Password for the superuser.
        :return: The newly created superuser instance.
        :rtype: User
        :raises ValueError: If is_staff or is_superuser are not True.
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    """Custom user model that uses email instead of username for authentication."""

    phone = models.CharField(max_length=30, null=True, blank=True)
    email = models.EmailField(unique=True)
    username = None

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = CustomUserManager()


class Workspace(models.Model):
    """A workspace that groups members, roles, and schedules together."""

    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="created_workspaces"
    )
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="owned_workspaces")
    name = models.CharField(max_length=30, default="Unnamed Workspace")


class WorkspaceMember(models.Model):
    """A membership record linking a User to a Workspace."""

    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE, related_name="members")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="workspaces")
    added_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="added_members")
    pay_rate = models.DecimalField(max_digits=10, decimal_places=2, null=True)


class Group(models.Model):
    """A messaging group that can contain multiple users."""

    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
    name = models.CharField(max_length=30, blank=True)


class GroupMember(models.Model):
    """A membership record linking a User to a Group."""

    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name="members")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="messagegroups")
