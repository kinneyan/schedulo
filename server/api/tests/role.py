from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from ..models import Workspace, WorkspaceMember, User, MemberPermissions, WorkspaceRole, MemberRole

class CreateRoleTests(APITestCase):
    def setUp(self):
        self.url = reverse('create_workspace_role')
        self.user = User.objects.create_user(
            email='testuser@example.com',
            password='testpassword',
            first_name='Test',
            last_name='User',
            phone='1234567890'
        )
        self.user2 = User.objects.create_user(
            email='testuser2@example.com',
            password='testpassword',
            first_name='Test2',
            last_name='User2',
            phone='1234567890'
        )
        self.user3 = User.objects.create_user(
            email='testuser3@example.com',
            password='testpassword',
            first_name='Test3',
            last_name='User3',
            phone='1234567890'
        )

        self.workspace = Workspace.objects.create(owner=self.user, created_by=self.user)

        self.member = WorkspaceMember.objects.create(user=self.user, workspace=self.workspace, added_by=self.user)
        self.permissions = MemberPermissions.objects.create(
            workspace=self.workspace,
            member=self.member,
            IS_OWNER=True,
            MANAGE_WORKSPACE_MEMBERS=True,
            MANAGE_WORKSPACE_ROLES=True,
            MANAGE_SCHEDULES=True,
            MANAGE_TIME_OFF=True
        )

        self.member2 = WorkspaceMember.objects.create(user=self.user2, workspace=self.workspace, added_by=self.user)
        self.permissions2 = MemberPermissions.objects.create(
            workspace=self.workspace,
            member=self.member2,
            IS_OWNER=False,
            MANAGE_WORKSPACE_MEMBERS=False,
            MANAGE_WORKSPACE_ROLES=False,
            MANAGE_SCHEDULES=False,
            MANAGE_TIME_OFF=False
        )
        self.client.force_authenticate(user=self.member.user)

    def test_no_workspace(self):
        data = {'name': 'test name1', 'pay_rate': 15.00}
        response = self.client.put(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_workspace(self):
        data = {'workspace_id': 999, 'name': 'test name1', 'pay_rate': 15.00}
        response = self.client.put(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_workspace_role_valid(self):
        data = {'workspace_id': self.workspace.id, 'name': 'test name1', 'pay_rate': 15.00}
        response = self.client.put(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        role = WorkspaceRole.objects.get(workspace=self.workspace, name=data['name'])

        self.assertEqual(role.workspace, self.workspace)
        self.assertEqual(role.name, data['name'])
        self.assertEqual(role.pay_rate, data['pay_rate'])

    def test_create_workspace_role_no_name_or_payrate(self):
        data = {'workspace_id': self.workspace.id}
        response = self.client.put(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        role = WorkspaceRole.objects.get(workspace=self.workspace)

        self.assertEqual(role.workspace, self.workspace)
        self.assertEqual(role.name, 'Unnamed Role')
        self.assertEqual(role.pay_rate, None)

    def test_create_workspace_role_without_permissions(self):
        data = {'workspace_id': self.workspace.id, 'name': 'test name1', 'pay_rate': 15.00}

        self.client.force_authenticate(user=self.user2) # change to send request from user 2

        response = self.client.put(self.url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_workspace_role_as_non_member(self):
        data = {'workspace_id': self.workspace.id, 'name': 'test name1', 'pay_rate': 15.00}

        self.client.force_authenticate(user=self.user3) # change to send request from user 2

        response = self.client.put(self.url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

class DeleteRoleTests(APITestCase):
    def setUp(self):
        self.url = reverse('delete_workspace_role')
        self.user = User.objects.create_user(
            email='testuser@example.com',
            password='testpassword',
            first_name='Test',
            last_name='User',
            phone='1234567890'
        )
        self.user2 = User.objects.create_user(
            email='testuser2@example.com',
            password='testpassword',
            first_name='Test2',
            last_name='User2',
            phone='1234567890'
        )
        self.user3 = User.objects.create_user(
            email='testuser3@example.com',
            password='testpassword',
            first_name='Test3',
            last_name='User3',
            phone='1234567890'
        )

        self.workspace = Workspace.objects.create(owner=self.user, created_by=self.user)

        self.member = WorkspaceMember.objects.create(user=self.user, workspace=self.workspace, added_by=self.user)
        self.permissions = MemberPermissions.objects.create(
            workspace=self.workspace,
            member=self.member,
            IS_OWNER=True,
            MANAGE_WORKSPACE_MEMBERS=True,
            MANAGE_WORKSPACE_ROLES=True,
            MANAGE_SCHEDULES=True,
            MANAGE_TIME_OFF=True
        )

        self.member2 = WorkspaceMember.objects.create(user=self.user2, workspace=self.workspace, added_by=self.user)
        self.permissions2 = MemberPermissions.objects.create(
            workspace=self.workspace,
            member=self.member2,
            IS_OWNER=False,
            MANAGE_WORKSPACE_MEMBERS=False,
            MANAGE_WORKSPACE_ROLES=False,
            MANAGE_SCHEDULES=False,
            MANAGE_TIME_OFF=False
        )
        self.client.force_authenticate(user=self.member.user)

        self.role = WorkspaceRole.objects.create(workspace=self.workspace, name="test role", pay_rate=10)
        self.role2 = WorkspaceRole.objects.create(workspace=self.workspace, name="test role2", pay_rate=10)
        self.role3 = WorkspaceRole.objects.create(workspace=self.workspace, name="test role3", pay_rate=10)

    def test_no_workspace_id(self):
        data = {'workspace_role_id': self.role.id}
        response = self.client.delete(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_workspace_id(self):
        data = {'workspace_id': 999, 'workspace_role_id': self.role.id}
        response = self.client.delete(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_no_workspace_role_id(self):
        data = {'workspace_id': self.workspace.id}
        response = self.client.delete(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_workspace_id(self):
        data = {'workspace_id': self.workspace.id, 'workspace_role_id': 999}
        response = self.client.delete(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_valid(self):
        data = {'workspace_id': self.workspace.id, 'workspace_role_id': self.role.id}
        response = self.client.delete(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # check that role was deleted
        try:
            role = WorkspaceRole.objects.get(id=self.role.id)
            self.assertTrue(False)
        except WorkspaceRole.DoesNotExist:
            self.assertTrue(True)

    def test_delete_with_children(self):
        member_role = MemberRole.objects.create(workspace_role=self.role, member=self.member2) # create child member role

        data = {'workspace_id': self.workspace.id, 'workspace_role_id': self.role.id}
        response = self.client.delete(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # check that role was deleted
        try:
            role = WorkspaceRole.objects.get(id=self.role.id)
            self.assertTrue(False)
        except WorkspaceRole.DoesNotExist:
            self.assertTrue(True)

        # check that member role was deleted
        try:
            role = MemberRole.objects.get(id=member_role.id)
            self.assertTrue(False)
        except MemberRole.DoesNotExist:
            self.assertTrue(True)

class GetRolesTests(APITestCase):
    def setUp(self):
        self.url = reverse('create_workspace_role')
        self.user = User.objects.create_user(
            email='testuser@example.com',
            password='testpassword',
            first_name='Test',
            last_name='User',
            phone='1234567890'
        )
        self.user2 = User.objects.create_user(
            email='testuser2@example.com',
            password='testpassword',
            first_name='Test2',
            last_name='User2',
            phone='1234567890'
        )
        self.user3 = User.objects.create_user(
            email='testuser3@example.com',
            password='testpassword',
            first_name='Test3',
            last_name='User3',
            phone='1234567890'
        )

        self.workspace = Workspace.objects.create(owner=self.user, created_by=self.user)

        self.member = WorkspaceMember.objects.create(user=self.user, workspace=self.workspace, added_by=self.user)
        self.permissions = MemberPermissions.objects.create(
            workspace=self.workspace,
            member=self.member,
            IS_OWNER=True,
            MANAGE_WORKSPACE_MEMBERS=True,
            MANAGE_WORKSPACE_ROLES=True,
            MANAGE_SCHEDULES=True,
            MANAGE_TIME_OFF=True
        )

        self.member2 = WorkspaceMember.objects.create(user=self.user2, workspace=self.workspace, added_by=self.user)
        self.permissions2 = MemberPermissions.objects.create(
            workspace=self.workspace,
            member=self.member2,
            IS_OWNER=False,
            MANAGE_WORKSPACE_MEMBERS=False,
            MANAGE_WORKSPACE_ROLES=False,
            MANAGE_SCHEDULES=False,
            MANAGE_TIME_OFF=False
        )
        self.client.force_authenticate(user=self.member.user)

    def test_no_workspace(self):
        data = {'name': 'test name1', 'pay_rate': 15.00}

        self.url = reverse('get_workspace_roles')
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_workspace(self):
        data = {'workspace_id': 999, 'name': 'test name1', 'pay_rate': 15.00}

        self.url = reverse('get_workspace_roles')
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_single(self):
        data = {'workspace_id': self.workspace.id, 'name': 'test name1', 'pay_rate': 15.00}
        response = self.client.put(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.url = reverse('get_workspace_roles')
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        output = response.data['roles']
        role = WorkspaceRole.objects.get(id=output[0][0])
               
        self.assertEqual(role.name, data['name'])

    def test_multiple(self):
        data = []
        data.append({'workspace_id': self.workspace.id, 'name': 'test name1', 'pay_rate': 15.00})
        data.append({'workspace_id': self.workspace.id, 'name': 'test name2', 'pay_rate': 10.00})
        data.append({'workspace_id': self.workspace.id, 'name': 'test name3', 'pay_rate': 18.00})

        for i in range(3):
            response = self.client.put(self.url, data[i], format='json')
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.url = reverse('get_workspace_roles')
        response = self.client.post(self.url, {'workspace_id': self.workspace.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        output = response.data['roles']

        self.assertEqual(len(output), len(data))

        for i in range(len(data)):
            role = WorkspaceRole.objects.get(id=output[i][0])
            self.assertEqual(data[i]['name'], output[i][1])
            self.assertEqual(data[i]['name'], role.name)

    def test_multiple_workspaces(self):
        # add another workspace and role to this workspace
        self.workspace2 = Workspace.objects.create(owner=self.user, created_by=self.user)

        self.member5 = WorkspaceMember.objects.create(user=self.user, workspace=self.workspace2, added_by=self.user)
        self.permissions5 = MemberPermissions.objects.create(
            workspace=self.workspace2,
            member=self.member5,
            IS_OWNER=True,
            MANAGE_WORKSPACE_MEMBERS=True,
            MANAGE_WORKSPACE_ROLES=True,
            MANAGE_SCHEDULES=True,
            MANAGE_TIME_OFF=True
        )
        
        response = self.client.put(self.url, {'workspace_id': self.workspace2.id, 'name': 'test name4', 'pay_rate': 5.00})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED) 

        data = []
        data.append({'workspace_id': self.workspace.id, 'name': 'test name1', 'pay_rate': 15.00})
        data.append({'workspace_id': self.workspace.id, 'name': 'test name2', 'pay_rate': 10.00})
        data.append({'workspace_id': self.workspace.id, 'name': 'test name3', 'pay_rate': 18.00})

        for i in range(3):
            response = self.client.put(self.url, data[i], format='json')
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.url = reverse('get_workspace_roles')
        response = self.client.post(self.url, {'workspace_id': self.workspace.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        output = response.data['roles']

        self.assertEqual(len(output), len(data))

        for i in range(len(data)):
            role = WorkspaceRole.objects.get(id=output[i][0])
            self.assertEqual(data[i]['name'], output[i][1])
            self.assertEqual(data[i]['name'], role.name)

class GetMemberRoleTests(APITestCase):
    def setUp(self):
        self.url = reverse('get_member_roles')
        self.user = User.objects.create_user(
            email='testuser@example.com',
            password='testpassword',
            first_name='Test',
            last_name='User',
            phone='1234567890'
        )
        self.user2 = User.objects.create_user(
            email='testuser2@example.com',
            password='testpassword',
            first_name='Test2',
            last_name='User2',
            phone='1234567890'
        )
        self.user3 = User.objects.create_user(
            email='testuser3@example.com',
            password='testpassword',
            first_name='Test3',
            last_name='User3',
            phone='1234567890'
        )

        self.workspace = Workspace.objects.create(owner=self.user, created_by=self.user)

        self.member = WorkspaceMember.objects.create(user=self.user, workspace=self.workspace, added_by=self.user)
        self.permissions = MemberPermissions.objects.create(
            workspace=self.workspace,
            member=self.member,
            IS_OWNER=True,
            MANAGE_WORKSPACE_MEMBERS=True,
            MANAGE_WORKSPACE_ROLES=True,
            MANAGE_SCHEDULES=True,
            MANAGE_TIME_OFF=True
        )

        self.member2 = WorkspaceMember.objects.create(user=self.user2, workspace=self.workspace, added_by=self.user)
        self.permissions2 = MemberPermissions.objects.create(
            workspace=self.workspace,
            member=self.member2,
            IS_OWNER=False,
            MANAGE_WORKSPACE_MEMBERS=False,
            MANAGE_WORKSPACE_ROLES=False,
            MANAGE_SCHEDULES=False,
            MANAGE_TIME_OFF=False
        )
        self.client.force_authenticate(user=self.member.user)

        self.role = WorkspaceRole.objects.create(workspace=self.workspace, name="test role", pay_rate=10)
        self.role2 = WorkspaceRole.objects.create(workspace=self.workspace, name="test role2", pay_rate=10)
        self.role3 = WorkspaceRole.objects.create(workspace=self.workspace, name="test role3", pay_rate=10)

    def test_no_member_id(self):
        response = self.client.post(self.url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_member_id(self):
        response = self.client.post(self.url, {'member_id': 999}, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_no_roles(self):
        response = self.client.post(self.url, {'member_id': self.member2.id}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['roles']), 0)

    def test_single(self):
        member_role = MemberRole.objects.create(workspace_role=self.role, member=self.member2)

        response = self.client.post(self.url, {'member_id': self.member2.id}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['roles']), 1)

        role = WorkspaceRole.objects.get(id=response.data['roles'][0][0])
        self.assertEqual(self.role, role)

    def test_multiple(self):
        member_role = MemberRole.objects.create(workspace_role=self.role, member=self.member2)
        member_role2 = MemberRole.objects.create(workspace_role=self.role2, member=self.member2)
        member_role3 = MemberRole.objects.create(workspace_role=self.role3, member=self.member2)

        data = {'member_id': self.member2.id}

        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['roles']), 3)

        role = WorkspaceRole.objects.get(id=response.data['roles'][0][0])
        role2 = WorkspaceRole.objects.get(id=response.data['roles'][1][0])
        role3 = WorkspaceRole.objects.get(id=response.data['roles'][2][0])
        self.assertEqual(self.role, role)
        self.assertEqual(self.role2, role2)
        self.assertEqual(self.role3, role3)
      
class AddMemberRoleTests(APITestCase):
    def setUp(self):
        self.url = reverse('add_member_role')
        self.user = User.objects.create_user(
            email='testuser@example.com',
            password='testpassword',
            first_name='Test',
            last_name='User',
            phone='1234567890'
        )
        self.user2 = User.objects.create_user(
            email='testuser2@example.com',
            password='testpassword',
            first_name='Test2',
            last_name='User2',
            phone='1234567890'
        )
        self.user3 = User.objects.create_user(
            email='testuser3@example.com',
            password='testpassword',
            first_name='Test3',
            last_name='User3',
            phone='1234567890'
        )

        self.workspace = Workspace.objects.create(owner=self.user, created_by=self.user)

        self.member = WorkspaceMember.objects.create(user=self.user, workspace=self.workspace, added_by=self.user)
        self.permissions = MemberPermissions.objects.create(
            workspace=self.workspace,
            member=self.member,
            IS_OWNER=True,
            MANAGE_WORKSPACE_MEMBERS=True,
            MANAGE_WORKSPACE_ROLES=True,
            MANAGE_SCHEDULES=True,
            MANAGE_TIME_OFF=True
        )

        self.member2 = WorkspaceMember.objects.create(user=self.user2, workspace=self.workspace, added_by=self.user)
        self.permissions2 = MemberPermissions.objects.create(
            workspace=self.workspace,
            member=self.member2,
            IS_OWNER=False,
            MANAGE_WORKSPACE_MEMBERS=False,
            MANAGE_WORKSPACE_ROLES=False,
            MANAGE_SCHEDULES=False,
            MANAGE_TIME_OFF=False
        )
        self.client.force_authenticate(user=self.member.user)

        self.role = WorkspaceRole.objects.create(workspace=self.workspace, name="test role", pay_rate=10)
        self.role2 = WorkspaceRole.objects.create(workspace=self.workspace, name="test role2", pay_rate=10)
        self.role3 = WorkspaceRole.objects.create(workspace=self.workspace, name="test role3", pay_rate=10)
        
    def test_no_workspace(self):
        data = {'workspace_role_id': self.role.id, 'member_id': self.member2.id}
        response = self.client.put(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_workspace(self):
        data = {'workspace_id': 999,'workspace_role_id': self.role.id, 'member_id': self.member2.id}
        response = self.client.put(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_no_role(self):
        data = {'workspace_id': self.workspace.id, 'member_id': self.member2.id}
        response = self.client.put(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_role(self):
        data = {'workspace_id': self.workspace.id,'workspace_role_id': 999, 'member_id': self.member2.id}
        response = self.client.put(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_no_member(self):
        data = {'workspace_id': self.workspace.id,'workspace_role_id': self.role.id}
        response = self.client.put(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_member(self):
        data = {'workspace_id': self.workspace.id,'workspace_role_id': self.role.id, 'member_id': 999}
        response = self.client.put(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_add_single(self):
        data = {'workspace_id': self.workspace.id,'workspace_role_id': self.role.id, 'member_id': self.member2.id}

        response = self.client.put(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        try: # this is probably a bad way to handle this since the fail doesnt give any info but idk :(
            role = MemberRole.objects.get(workspace_role=self.role, member=self.member2)
        except MemberRole.DoesNotExist:
            self.assertTrue(False)

    def test_add_multiple(self):
        data = []
        data.append({'workspace_id': self.workspace.id,'workspace_role_id': self.role.id, 'member_id': self.member2.id})
        data.append({'workspace_id': self.workspace.id,'workspace_role_id': self.role2.id, 'member_id': self.member2.id})
        data.append({'workspace_id': self.workspace.id,'workspace_role_id': self.role3.id, 'member_id': self.member2.id})

        for i in range(3):
            response = self.client.put(self.url, data[i], format='json')
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        try: # this is probably a bad way to handle this since the fail doesnt give any info but idk :(
            roles = list(MemberRole.objects.filter(member=self.member2))
        except MemberRole.DoesNotExist:
            self.assertTrue(False)

        role = []
        for i in range(len(roles)):
            try:
                role.append(WorkspaceRole.objects.get(id=roles[i].workspace_role.id))
            except WorkspaceRole.DoesNotExist:
                self.assertTrue(False)

        self.assertEqual(self.role, role[0])
        self.assertEqual(self.role2, role[1])
        self.assertEqual(self.role3, role[2])

    def test_add_without_permissions(self):
        self.client.force_authenticate(user=self.member2.user)
        data = {'workspace_id': self.workspace.id,'workspace_role_id': self.role.id, 'member_id': self.member2.id}

        response = self.client.put(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        try: # this is probably a bad way to handle this since the fail doesnt give any info but idk :(
            role = MemberRole.objects.get(workspace_role=self.role, member=self.member2)
            self.assertTrue(False)
        except MemberRole.DoesNotExist:
            self.assertTrue(True)

class RemoveMemberRoleTests(APITestCase):
    def setUp(self):
        self.url = reverse('remove_member_role')
        self.user = User.objects.create_user(
            email='testuser@example.com',
            password='testpassword',
            first_name='Test',
            last_name='User',
            phone='1234567890'
        )
        self.user2 = User.objects.create_user(
            email='testuser2@example.com',
            password='testpassword',
            first_name='Test2',
            last_name='User2',
            phone='1234567890'
        )
        self.user3 = User.objects.create_user(
            email='testuser3@example.com',
            password='testpassword',
            first_name='Test3',
            last_name='User3',
            phone='1234567890'
        )

        self.workspace = Workspace.objects.create(owner=self.user, created_by=self.user)

        self.member = WorkspaceMember.objects.create(user=self.user, workspace=self.workspace, added_by=self.user)
        self.permissions = MemberPermissions.objects.create(
            workspace=self.workspace,
            member=self.member,
            IS_OWNER=True,
            MANAGE_WORKSPACE_MEMBERS=True,
            MANAGE_WORKSPACE_ROLES=True,
            MANAGE_SCHEDULES=True,
            MANAGE_TIME_OFF=True
        )

        self.member2 = WorkspaceMember.objects.create(user=self.user2, workspace=self.workspace, added_by=self.user)
        self.permissions2 = MemberPermissions.objects.create(
            workspace=self.workspace,
            member=self.member2,
            IS_OWNER=False,
            MANAGE_WORKSPACE_MEMBERS=False,
            MANAGE_WORKSPACE_ROLES=False,
            MANAGE_SCHEDULES=False,
            MANAGE_TIME_OFF=False
        )
        self.client.force_authenticate(user=self.member.user)

        self.role = WorkspaceRole.objects.create(workspace=self.workspace, name="test role1", pay_rate=10)
        self.role2 = WorkspaceRole.objects.create(workspace=self.workspace, name="test role2", pay_rate=10)
        self.role3 = WorkspaceRole.objects.create(workspace=self.workspace, name="test role3", pay_rate=10)

        self.member_role = MemberRole.objects.create(workspace_role=self.role, member=self.member2)
        self.member_role2 = MemberRole.objects.create(workspace_role=self.role2, member=self.member2)

    def test_no_workspace(self):
        data = {'workspace_role_id': self.role.id, 'member_id': self.member2.id}
        response = self.client.delete(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_workspace(self):
        data = {'workspace_id': 999,'workspace_role_id': self.role.id, 'member_id': self.member2.id}
        response = self.client.delete(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_no_role(self):
        data = {'workspace_id': self.workspace.id, 'member_id': self.member2.id}
        response = self.client.delete(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_role(self):
        data = {'workspace_id': self.workspace.id,'workspace_role_id': 999, 'member_id': self.member2.id}
        response = self.client.delete(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_no_member(self):
        data = {'workspace_id': self.workspace.id,'workspace_role_id': self.role.id}
        response = self.client.delete(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_member(self):
        data = {'workspace_id': self.workspace.id,'workspace_role_id': self.role.id, 'member_id': 999}
        response = self.client.delete(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        
    def test_remove_valid(self):
        data = {'workspace_id': self.workspace.id,'workspace_role_id': self.role.id, 'member_id': self.member2.id}
        response = self.client.delete(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # check that member role was deleted
        try:
            role = MemberRole.objects.get(member=self.member2, workspace_role=self.role)
            self.assertTrue(False)
        except MemberRole.DoesNotExist:
            self.assertTrue(True)

        # check that member still has other role
        try:
            role = MemberRole.objects.get(member=self.member2, workspace_role=self.role2)
        except MemberRole.DoesNotExist:
            self.assertTrue(False)

    def test_remove_role_member_doesnt_have(self):
        data = {'workspace_id': self.workspace.id,'workspace_role_id': self.role3.id, 'member_id': self.member2.id}
        response = self.client.delete(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)



    


