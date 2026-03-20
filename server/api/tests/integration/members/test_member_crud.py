from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from ....models import (
    Workspace,
    WorkspaceMember,
    User,
    MemberPermissions,
    WorkspaceRole,
    MemberRole,
)


class GetMemberTests(APITestCase):
    """Integration tests for the get member endpoint."""

    def setUp(self):
        """Create two workspaces with members and authenticate test users."""
        self.user = User.objects.create_user(
            email="testuser@example.com",
            password="testpassword",
            first_name="Test",
            last_name="User",
            phone="1234567890",
        )
        self.user2 = User.objects.create_user(
            email="testuser2@example.com",
            password="testpassword",
            first_name="Test2",
            last_name="User2",
            phone="1234567890",
        )
        self.user3 = User.objects.create_user(
            email="testuser3@example.com",
            password="testpassword",
            first_name="Test3",
            last_name="User3",
            phone="1234567890",
        )

        self.workspace1 = Workspace.objects.create(
            owner=self.user, created_by=self.user
        )
        self.workspace1_member1 = WorkspaceMember.objects.create(
            user=self.user, workspace=self.workspace1, added_by=self.user
        )
        self.workspace1_permissions1 = MemberPermissions.objects.create(
            workspace=self.workspace1,
            member=self.workspace1_member1,
            is_owner=True,
            manage_workspace_members=True,
            manage_workspace_roles=True,
            manage_schedules=True,
            manage_time_off=True,
        )
        self.workspace1_member2 = WorkspaceMember.objects.create(
            user=self.user2, workspace=self.workspace1, added_by=self.user
        )
        self.workspace1_permissions2 = MemberPermissions.objects.create(
            workspace=self.workspace1,
            member=self.workspace1_member2,
            is_owner=False,
            manage_workspace_members=True,
            manage_workspace_roles=True,
            manage_schedules=True,
            manage_time_off=True,
        )

        self.workspace2 = Workspace.objects.create(
            owner=self.user, created_by=self.user
        )
        self.workspace2_member1 = WorkspaceMember.objects.create(
            user=self.user, workspace=self.workspace2, added_by=self.user
        )
        self.workspace2_permissions1 = MemberPermissions.objects.create(
            workspace=self.workspace2,
            member=self.workspace2_member1,
            is_owner=True,
            manage_workspace_members=True,
            manage_workspace_roles=True,
            manage_schedules=True,
            manage_time_off=True,
        )

        self.role = WorkspaceRole.objects.create(
            workspace=self.workspace1, name="test role1", pay_rate=10
        )
        self.role2 = WorkspaceRole.objects.create(
            workspace=self.workspace1, name="test role2", pay_rate=10
        )
        self.role3 = WorkspaceRole.objects.create(
            workspace=self.workspace1, name="test role3", pay_rate=10
        )

        self.member_role = MemberRole.objects.create(
            workspace_role=self.role, member=self.workspace1_member1
        )
        self.member_role2 = MemberRole.objects.create(
            workspace_role=self.role, member=self.workspace1_member2
        )
        self.member_role3 = MemberRole.objects.create(
            workspace_role=self.role2, member=self.workspace1_member2
        )

        self.client.force_authenticate(user=self.user)

    def test_one_role(self):
        self.url = reverse("member", args=[self.workspace1_member1.id])
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        print(response.data["result"])

    def test_multiple_roles(self):
        self.url = reverse("member", args=[self.workspace1_member2.id])
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        print(response.data["result"])
