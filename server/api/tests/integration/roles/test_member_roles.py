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


class AddMemberRoleTests(APITestCase):
    """Integration tests for assigning roles to workspace members."""

    def setUp(self):
        """Create a workspace, owner, and member with manage_workspace_roles permission."""
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

        self.workspace = Workspace.objects.create(owner=self.user, created_by=self.user)

        self.member = WorkspaceMember.objects.create(
            user=self.user, workspace=self.workspace, added_by=self.user
        )
        self.permissions = MemberPermissions.objects.create(
            workspace=self.workspace,
            member=self.member,
            is_owner=True,
            manage_workspace_members=True,
            manage_workspace_roles=True,
            manage_schedules=True,
            manage_time_off=True,
        )

        self.member2 = WorkspaceMember.objects.create(
            user=self.user2, workspace=self.workspace, added_by=self.user
        )
        self.permissions2 = MemberPermissions.objects.create(
            workspace=self.workspace,
            member=self.member2,
            is_owner=False,
            manage_workspace_members=False,
            manage_workspace_roles=False,
            manage_schedules=False,
            manage_time_off=False,
        )
        self.client.force_authenticate(user=self.member.user)

        self.role = WorkspaceRole.objects.create(
            workspace=self.workspace, name="test role", pay_rate=10
        )
        self.role2 = WorkspaceRole.objects.create(
            workspace=self.workspace, name="test role2", pay_rate=10
        )
        self.role3 = WorkspaceRole.objects.create(
            workspace=self.workspace, name="test role3", pay_rate=10
        )
        self.url = reverse("member_roles", kwargs={"member_id": self.member2.id})

    def test_no_role(self):
        """Verify that omitting workspace_role_id returns 400."""
        response = self.client.post(self.url, {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_role(self):
        """Verify that a nonexistent workspace_role_id returns 404."""
        data = {"workspace_role_id": 999}
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_invalid_member(self):
        """Verify that a nonexistent member_id returns 404."""
        url = reverse("member_roles", kwargs={"member_id": 999})
        data = {"workspace_role_id": self.role.id}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_add_single(self):
        """Verify that assigning a single valid role returns 201 and persists the MemberRole."""
        data = {"workspace_role_id": self.role.id}

        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertTrue(
            MemberRole.objects.filter(workspace_role=self.role, member=self.member2).exists()
        )

    def test_add_multiple(self):
        """Verify that assigning multiple roles in sequence returns 201 each time and persists all MemberRoles."""
        data = []
        data.append({"workspace_role_id": self.role.id})
        data.append({"workspace_role_id": self.role2.id})
        data.append({"workspace_role_id": self.role3.id})

        for i in range(3):
            response = self.client.post(self.url, data[i], format="json")
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        roles = list(MemberRole.objects.filter(member=self.member2).order_by("id"))
        self.assertEqual(len(roles), 3)
        self.assertEqual(roles[0].workspace_role.id, self.role.id)
        self.assertEqual(roles[1].workspace_role.id, self.role2.id)
        self.assertEqual(roles[2].workspace_role.id, self.role3.id)

    def test_add_without_permissions(self):
        """Verify that a member without manage_workspace_roles permission receives 403 and no role is assigned."""
        self.client.force_authenticate(user=self.member2.user)
        data = {"workspace_role_id": self.role.id}

        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.assertFalse(
            MemberRole.objects.filter(workspace_role=self.role, member=self.member2).exists()
        )

    def test_add_cross_workspace_isolation(self):
        """Verify that a privileged member of another workspace cannot assign a role in this workspace."""
        other_workspace = Workspace.objects.create(owner=self.user3, created_by=self.user3)
        other_member = WorkspaceMember.objects.create(
            user=self.user3, workspace=other_workspace, added_by=self.user3
        )
        MemberPermissions.objects.create(
            workspace=other_workspace,
            member=other_member,
            is_owner=True,
            manage_workspace_roles=True,
        )
        self.client.force_authenticate(user=self.user3)

        response = self.client.post(self.url, {"workspace_role_id": self.role.id}, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(
            MemberRole.objects.filter(workspace_role=self.role, member=self.member2).exists()
        )


class RemoveMemberRoleTests(APITestCase):
    """Integration tests for removing roles from workspace members."""

    def setUp(self):
        """Create a workspace, owner, member with manage_workspace_roles permission, and pre-assigned member roles."""
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

        self.workspace = Workspace.objects.create(owner=self.user, created_by=self.user)

        self.member = WorkspaceMember.objects.create(
            user=self.user, workspace=self.workspace, added_by=self.user
        )
        self.permissions = MemberPermissions.objects.create(
            workspace=self.workspace,
            member=self.member,
            is_owner=True,
            manage_workspace_members=True,
            manage_workspace_roles=True,
            manage_schedules=True,
            manage_time_off=True,
        )

        self.member2 = WorkspaceMember.objects.create(
            user=self.user2, workspace=self.workspace, added_by=self.user
        )
        self.permissions2 = MemberPermissions.objects.create(
            workspace=self.workspace,
            member=self.member2,
            is_owner=False,
            manage_workspace_members=False,
            manage_workspace_roles=False,
            manage_schedules=False,
            manage_time_off=False,
        )
        self.client.force_authenticate(user=self.member.user)

        self.role = WorkspaceRole.objects.create(
            workspace=self.workspace, name="test role1", pay_rate=10
        )
        self.role2 = WorkspaceRole.objects.create(
            workspace=self.workspace, name="test role2", pay_rate=10
        )
        self.role3 = WorkspaceRole.objects.create(
            workspace=self.workspace, name="test role3", pay_rate=10
        )

        self.member_role = MemberRole.objects.create(
            workspace_role=self.role, member=self.member2
        )
        self.member_role2 = MemberRole.objects.create(
            workspace_role=self.role2, member=self.member2
        )
        self.url = reverse("member_roles", kwargs={"member_id": self.member2.id})

    def test_no_role(self):
        """Verify that omitting workspace_role_id returns 400."""
        response = self.client.delete(self.url, {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_role(self):
        """Verify that a nonexistent workspace_role_id returns 404."""
        data = {"workspace_role_id": 999}
        response = self.client.delete(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_invalid_member(self):
        """Verify that a nonexistent member_id returns 404."""
        url = reverse("member_roles", kwargs={"member_id": 999})
        data = {"workspace_role_id": self.role.id}
        response = self.client.delete(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_remove_valid(self):
        """Verify that removing an assigned role returns 200, deletes the MemberRole, and leaves other roles intact."""
        data = {"workspace_role_id": self.role.id}
        response = self.client.delete(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertFalse(
            MemberRole.objects.filter(member=self.member2, workspace_role=self.role).exists()
        )
        self.assertTrue(
            MemberRole.objects.filter(member=self.member2, workspace_role=self.role2).exists()
        )

    def test_remove_role_member_doesnt_have(self):
        """Verify that removing a role not assigned to the member returns 404."""
        data = {"workspace_role_id": self.role3.id}
        response = self.client.delete(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_remove_without_permissions(self):
        """Verify that a member without manage_workspace_roles permission receives 403 and the role is not removed."""
        self.client.force_authenticate(user=self.member2.user)
        data = {"workspace_role_id": self.role.id}
        response = self.client.delete(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.assertTrue(
            MemberRole.objects.filter(member=self.member2, workspace_role=self.role).exists()
        )

    def test_remove_cross_workspace_isolation(self):
        """Verify that a privileged member of another workspace cannot remove a role in this workspace."""
        other_workspace = Workspace.objects.create(owner=self.user3, created_by=self.user3)
        other_member = WorkspaceMember.objects.create(
            user=self.user3, workspace=other_workspace, added_by=self.user3
        )
        MemberPermissions.objects.create(
            workspace=other_workspace,
            member=other_member,
            is_owner=True,
            manage_workspace_roles=True,
        )
        self.client.force_authenticate(user=self.user3)

        response = self.client.delete(self.url, {"workspace_role_id": self.role.id}, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(
            MemberRole.objects.filter(member=self.member2, workspace_role=self.role).exists()
        )
