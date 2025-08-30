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
    def setUp(self):
        self.url = reverse("add_member_role")
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
            IS_OWNER=True,
            MANAGE_WORKSPACE_MEMBERS=True,
            MANAGE_WORKSPACE_ROLES=True,
            MANAGE_SCHEDULES=True,
            MANAGE_TIME_OFF=True,
        )

        self.member2 = WorkspaceMember.objects.create(
            user=self.user2, workspace=self.workspace, added_by=self.user
        )
        self.permissions2 = MemberPermissions.objects.create(
            workspace=self.workspace,
            member=self.member2,
            IS_OWNER=False,
            MANAGE_WORKSPACE_MEMBERS=False,
            MANAGE_WORKSPACE_ROLES=False,
            MANAGE_SCHEDULES=False,
            MANAGE_TIME_OFF=False,
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

    def test_no_role(self):
        data = {"member_id": self.member2.id}
        response = self.client.put(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_role(self):
        data = {"workspace_role_id": 999, "member_id": self.member2.id}
        response = self.client.put(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_no_member(self):
        data = {"workspace_role_id": self.role.id}
        response = self.client.put(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_member(self):
        data = {"workspace_role_id": self.role.id, "member_id": 999}
        response = self.client.put(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_add_single(self):
        data = {"workspace_role_id": self.role.id, "member_id": self.member2.id}

        response = self.client.put(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        try:  # this is probably a bad way to handle this since the fail doesnt give any info but idk :(
            MemberRole.objects.get(workspace_role=self.role, member=self.member2)
        except MemberRole.DoesNotExist:
            self.assertTrue(False)

    def test_add_multiple(self):
        data = []
        data.append({"workspace_role_id": self.role.id, "member_id": self.member2.id})
        data.append({"workspace_role_id": self.role2.id, "member_id": self.member2.id})
        data.append({"workspace_role_id": self.role3.id, "member_id": self.member2.id})

        for i in range(3):
            response = self.client.put(self.url, data[i], format="json")
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        try:  # this is probably a bad way to handle this since the fail doesnt give any info but idk :(
            roles = list(MemberRole.objects.filter(member=self.member2))
        except MemberRole.DoesNotExist:
            self.assertTrue(False)

        role = []
        for i in range(len(roles)):
            try:
                role.append(WorkspaceRole.objects.get(id=roles[i].workspace_role.id))
            except WorkspaceRole.DoesNotExist:
                self.assertTrue(False)

        self.assertEqual(self.role.id, role[0].id)
        self.assertEqual(self.role2.id, role[1].id)
        self.assertEqual(self.role3.id, role[2].id)

    def test_add_without_permissions(self):
        self.client.force_authenticate(user=self.member2.user)
        data = {"workspace_role_id": self.role.id, "member_id": self.member2.id}

        response = self.client.put(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        try:  # this is probably a bad way to handle this since the fail doesnt give any info but idk :(
            MemberRole.objects.get(workspace_role=self.role, member=self.member2)
            self.assertTrue(False)
        except MemberRole.DoesNotExist:
            self.assertTrue(True)


class RemoveMemberRoleTests(APITestCase):
    def setUp(self):
        self.url = reverse("remove_member_role")
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
            IS_OWNER=True,
            MANAGE_WORKSPACE_MEMBERS=True,
            MANAGE_WORKSPACE_ROLES=True,
            MANAGE_SCHEDULES=True,
            MANAGE_TIME_OFF=True,
        )

        self.member2 = WorkspaceMember.objects.create(
            user=self.user2, workspace=self.workspace, added_by=self.user
        )
        self.permissions2 = MemberPermissions.objects.create(
            workspace=self.workspace,
            member=self.member2,
            IS_OWNER=False,
            MANAGE_WORKSPACE_MEMBERS=False,
            MANAGE_WORKSPACE_ROLES=False,
            MANAGE_SCHEDULES=False,
            MANAGE_TIME_OFF=False,
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

    def test_no_role(self):
        data = {"member_id": self.member2.id}
        response = self.client.delete(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_role(self):
        data = {"workspace_role_id": 999, "member_id": self.member2.id}
        response = self.client.delete(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_no_member(self):
        data = {"workspace_role_id": self.role.id}
        response = self.client.delete(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_member(self):
        data = {"workspace_role_id": self.role.id, "member_id": 999}
        response = self.client.delete(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_remove_valid(self):
        data = {"workspace_role_id": self.role.id, "member_id": self.member2.id}
        response = self.client.delete(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # check that member role was deleted
        try:
            MemberRole.objects.get(member=self.member2, workspace_role=self.role)
            self.assertTrue(False)
        except MemberRole.DoesNotExist:
            self.assertTrue(True)

        # check that member still has other role
        try:
            MemberRole.objects.get(member=self.member2, workspace_role=self.role2)
        except MemberRole.DoesNotExist:
            self.assertTrue(False)

    def test_remove_role_member_doesnt_have(self):
        data = {"workspace_role_id": self.role3.id, "member_id": self.member2.id}
        response = self.client.delete(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_remove_without_permissions(self):
        self.client.force_authenticate(user=self.member2.user)
        data = {"workspace_role_id": self.role.id, "member_id": self.member2.id}
        response = self.client.delete(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # check that member role wasnt deleted
        try:
            MemberRole.objects.get(member=self.member2, workspace_role=self.role)
        except MemberRole.DoesNotExist:
            self.assertTrue(False)
