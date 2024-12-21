from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from ..models import Workspace, WorkspaceMember, User, MemberPermissions, WorkspaceRole, MemberRole

class CreateRoleTests(APITestCase):
    def setUp(self):
        self.url = reverse('create_role')
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

    def test_create_role_valid(self):
        data = {'workspace_id': self.workspace.id, 'name': 'test name1', 'pay_rate': 15.00}
        response = self.client.put(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        role = WorkspaceRole.objects.get(workspace=self.workspace, name=data['name'])

        self.assertEqual(role.workspace, self.workspace)
        self.assertEqual(role.name, data['name'])
        self.assertEqual(role.pay_rate, data['pay_rate'])

    def test_create_role_no_name_or_payrate(self):
        data = {'workspace_id': self.workspace.id}
        response = self.client.put(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        role = WorkspaceRole.objects.get(workspace=self.workspace)

        self.assertEqual(role.workspace, self.workspace)
        self.assertEqual(role.name, 'Unnamed Role')
        self.assertEqual(role.pay_rate, None)

    def test_create_role_without_permissions(self):
        data = {'workspace_id': self.workspace.id, 'name': 'test name1', 'pay_rate': 15.00}

        self.client.force_authenticate(user=self.user2) # change to send request from user 2

        response = self.client.put(self.url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_role_as_non_member(self):
        data = {'workspace_id': self.workspace.id, 'name': 'test name1', 'pay_rate': 15.00}

        self.client.force_authenticate(user=self.user3) # change to send request from user 2

        response = self.client.put(self.url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

class GetRolesTests(APITestCase):
    def setUp(self):
        self.url = reverse('create_role')
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



        
  




    


