from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

from ..serializers import RoleSerializer
from ..models import Workspace, WorkspaceMember, User, MemberPermissions, WorkspaceRole, MemberRole

### WORKSPACE ROLE ENDPOINTS ###

class CreateRole(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def put(self, request):
        response = {"error": {}}

        serializer = RoleSerializer(data=request.data)
        if not serializer.is_valid():
            response["error"]["code"] = 400
            response["error"]["message"] = "Invalid request data"
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        
        # Verify body contains required fields
        if "workspace_id" not in request.data:
            response["error"]["message"] = "Workspace ID is required."
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        
        # Verify workspace exists
        try:
            workspace = Workspace.objects.get(pk=request.data["workspace_id"])
        except Workspace.DoesNotExist:
            response["error"]["message"] = "Workspace does not exist."
            return Response(response, status=status.HTTP_404_NOT_FOUND)
        
        # Verify user has permissions to manage workspace roles
        try:
            member = WorkspaceMember.objects.get(user=request.user, workspace=request.data["workspace_id"])
            permissions = MemberPermissions.objects.get(
                workspace=request.data["workspace_id"],
                member=member,
                MANAGE_WORKSPACE_ROLES=True
            )
        except MemberPermissions.DoesNotExist:
            response["error"]["message"] = "You do not have permission modify roles in this workspace."
            return Response(response, status=status.HTTP_403_FORBIDDEN)
        except WorkspaceMember.DoesNotExist:
            response["error"]["message"] = "You are not a member of this workspace."
            return Response(response, status=status.HTTP_403_FORBIDDEN)
        
        workspace_role = WorkspaceRole.objects.create(workspace=workspace)

        if 'name' in serializer.validated_data:
            workspace_role.name = serializer.validated_data['name']
        if 'pay_rate' in serializer.validated_data:
            workspace_role.pay_rate = serializer.validated_data['pay_rate']

        workspace_role.save()

        return Response(response, status=status.HTTP_201_CREATED)
    
class DeleteWorkspaceRole(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    '''
    # workspace_id (DEPRICATED)
    workspace_role_id
    '''

    def delete(self, request):
        response = {"error": {}}

        # Verify body contains required fields
        '''
        if "workspace_id" not in request.data:
            response["error"]["message"] = "Workspace ID is required."
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        '''
        if "workspace_role_id" not in request.data:
            response["error"]["message"] = "Workspace role ID is required."
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        
        # Verify role exists
        try:
            role = WorkspaceRole.objects.get(id=request.data['workspace_role_id'])
        except WorkspaceRole.DoesNotExist:
            response["error"]["message"] = "Workspace role does not exist or is not part of this workspace."
            return Response(response, status=status.HTTP_404_NOT_FOUND)

        # Get role's workspace
        try:
            workspace = Workspace.objects.get(id=role.workspace.id)
        except Workspace.DoesNotExist:
            response["error"]["message"] = "Workspace does not exist."
            return Response(response, status=status.HTTP_404_NOT_FOUND)
        
        # Verify user has permissions to manage workspace roles
        try:
            member = WorkspaceMember.objects.get(user=request.user, workspace=workspace)
            permissions = MemberPermissions.objects.get(
                workspace=workspace,
                member=member,
                MANAGE_WORKSPACE_ROLES=True
            )
        except MemberPermissions.DoesNotExist:
            response["error"]["message"] = "You do not have permission modify roles in this workspace."
            return Response(response, status=status.HTTP_403_FORBIDDEN)
        except WorkspaceMember.DoesNotExist:
            response["error"]["message"] = "You are not a member of this workspace."
            return Response(response, status=status.HTTP_403_FORBIDDEN)
            
        
        # delete role
        role = WorkspaceRole.objects.get(id=request.data['workspace_role_id']).delete()
        return Response(response, status=status.HTTP_200_OK)
    
class ModifyWorkspaceRole(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        response = {"error": {}}

        '''
        workspace_role_id
        name (optional)
        pay_rate (optional)
        '''

        if "workspace_role_id" not in request.data:
            response["error"]["message"] = "Workspace role ID is required."
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        serializer = RoleSerializer(data=request.data)
        if not serializer.is_valid():
            response["error"]["code"] = 400
            response["error"]["message"] = "Invalid request data"
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        
        # Verify role exists
        try:
            workspace_role = WorkspaceRole.objects.get(pk=request.data["workspace_role_id"])
        except WorkspaceRole.DoesNotExist:
            response["error"]["message"] = "Workspace role does not exist."
            return Response(response, status=status.HTTP_404_NOT_FOUND)

        # Verify workspace exists; this shouldnt ever fail but have to get the workspace
        try:
            workspace = Workspace.objects.get(pk=workspace_role.workspace.id)
        except Workspace.DoesNotExist:
            response["error"]["message"] = "Workspace does not exist."
            return Response(response, status=status.HTTP_404_NOT_FOUND)
        
        # Verify user has permissions to manage workspace roles
        try:
            member = WorkspaceMember.objects.get(user=request.user, workspace=workspace)
            permissions = MemberPermissions.objects.get(
                workspace=workspace,
                member=member,
                MANAGE_WORKSPACE_ROLES=True
            )
        except MemberPermissions.DoesNotExist:
            response["error"]["message"] = "You do not have permission modify roles in this workspace."
            return Response(response, status=status.HTTP_403_FORBIDDEN)
        except WorkspaceMember.DoesNotExist:
            response["error"]["message"] = "You are not a member of this workspace."
            return Response(response, status=status.HTTP_403_FORBIDDEN)
        
        # modify role
        if 'name' in serializer.validated_data:
            workspace_role.name = serializer.validated_data['name']
        if 'pay_rate' in serializer.validated_data:
            workspace_role.pay_rate = serializer.validated_data['pay_rate']

        workspace_role.save()

        return Response(response, status=status.HTTP_200_OK)
    
class GetWorkspaceRoles(APIView): # returns a list of all roles in a workspace
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        response = {"error": {}}

        '''
        workspace_id
        '''

        # Verify body contains required fields
        if "workspace_id" not in request.data:
            response["error"]["message"] = "Workspace ID is required."
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        # Verify workspace exists
        try:
            workspace = Workspace.objects.get(pk=request.data["workspace_id"])
        except Workspace.DoesNotExist:
            response["error"]["message"] = "Workspace does not exist."
            return Response(response, status=status.HTTP_404_NOT_FOUND)
  
        results = WorkspaceRole.objects.filter(workspace=workspace)

        role_list = [
            {
                'id': role.id,
                'name': role.name,
                'pay_rate': role.pay_rate,
            }
            for role in results
        ]

        response['roles'] = role_list

        return Response(response, status=status.HTTP_200_OK)

class GetMemberRoles(APIView): # returns of list of the WorkspaceRoles a member has
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        response = {"error": {}}

        ''' 
        member_id
        '''

        if "member_id" not in request.data:
            response["error"]["message"] = "Member ID is required"
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        
        # Verify that member exists
        try:
            member = WorkspaceMember.objects.get(id=request.data['member_id'])
        except WorkspaceMember.DoesNotExist:
            response["error"]["message"] = "Member does not exist."
            return Response(response, status=status.HTTP_404_NOT_FOUND)
        
        # get list of roles
        member_roles = MemberRole.objects.filter(member=member)
        results = WorkspaceRole.objects.filter(pk__in=member_roles)

        role_list = [
            {
                'id': role.id,
                'name': role.name,
                'pay_rate': role.pay_rate,
            }
            for role in results
        ]

        response['roles'] = role_list

        return Response(response, status=status.HTTP_200_OK)
    
### MEMBER ROLE ENDPOINTS ###
    
class AddMemberRole(APIView): # adds a role to a workspace member
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    '''
    # workspace_id (DEPRICATED)
    member_id; the member to have the role added to them
    workspace_role_id
    '''

    def put(self, request):
        response = {"error": {}}

        # Verify body contains required fields
        '''
        if "workspace_id" not in request.data:
            response["error"]["message"] = "Workspace ID is required."
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        '''
            
        if "member_id" not in request.data:
            response["error"]["message"] = "Member ID is required"
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        
        if "workspace_role_id" not in request.data:
            response["error"]["message"] = "Role ID is required"
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        
        '''
        # Verify workspace exists
        try:
            workspace = Workspace.objects.get(pk=request.data["workspace_id"])
        except Workspace.DoesNotExist:
            response["error"]["message"] = "Workspace does not exist."
            return Response(response, status=status.HTTP_404_NOT_FOUND)
        '''
        # Verify member exists
        try:
            modify_member = WorkspaceMember.objects.get(id=request.data['member_id'])
        except WorkspaceMember.DoesNotExist:
            response["error"]["message"] = "Member does not exist." 
            return Response(response, status=status.HTTP_404_NOT_FOUND)
        
        # Get workspace
        workspace = Workspace.objects.get(id=modify_member.workspace.id)
            
        # Verify user has permissions to manage workspace roles
        try:
            request_member = WorkspaceMember.objects.get(user=request.user, workspace=workspace)
            permissions = MemberPermissions.objects.get(
                workspace=workspace,
                member=request_member,
                MANAGE_WORKSPACE_ROLES=True
            )
        except MemberPermissions.DoesNotExist:
            response["error"]["message"] = "You do not have permission modify roles in this workspace."
            return Response(response, status=status.HTTP_403_FORBIDDEN)
        except WorkspaceMember.DoesNotExist:
            response["error"]["message"] = "You are not a member of this workspace."
            return Response(response, status=status.HTTP_403_FORBIDDEN)      

        # Verify that role exists and is part of workspace
        try:
            workspace_role = WorkspaceRole.objects.get(id=request.data['workspace_role_id'], workspace=workspace)
        except WorkspaceRole.DoesNotExist:
            response["error"]["message"] = "Role is not part of this workspace or does not exist."
            return Response(response, status=status.HTTP_404_NOT_FOUND)

        # Verify that member does not already have this role
        try:
            member_role = MemberRole.objects.get(member=request.data['member_id'], workspace_role=request.data['workspace_role_id'])
        except MemberRole.DoesNotExist:
            # add role to member if they did not have it
            member_role = MemberRole.objects.create(member=modify_member, workspace_role=workspace_role)
            return Response(response, status=status.HTTP_201_CREATED)
        
        # member already had role
        response["error"]["message"] = "Member already has this role."
        return Response(response, status=status.HTTP_409_CONFLICT)
    
class RemoveMemberRole(APIView): # removes a role from a workspace member
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    '''
    # workspace_id (DEPRICATED)
    member_id; the member to have the role removed from them
    workspace_role_id
    '''

    def delete(self, request):
        response = {"error": {}}

        # Verify body contains required fields
        '''
        if "workspace_id" not in request.data:
            response["error"]["message"] = "Workspace ID is required."
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        '''
        
        if "member_id" not in request.data:
            response["error"]["message"] = "Member ID is required"
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        
        if "workspace_role_id" not in request.data:
            response["error"]["message"] = "Role ID is required"
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        
        '''
        # Verify workspace exists
        try:
            workspace = Workspace.objects.get(pk=request.data["workspace_id"])
        except Workspace.DoesNotExist:
            response["error"]["message"] = "Workspace does not exist."
            return Response(response, status=status.HTTP_404_NOT_FOUND)
        '''
        # Verify member exists
        try:
            modify_member = WorkspaceMember.objects.get(id=request.data['member_id'])
        except WorkspaceMember.DoesNotExist:
            response["error"]["message"] = "Member does not exist." 
            return Response(response, status=status.HTTP_404_NOT_FOUND)
        
        # Get workspace
        workspace = Workspace.objects.get(id=modify_member.workspace.id)
            
        # Verify user has permissions to manage workspace roles
        try:
            request_member = WorkspaceMember.objects.get(user=request.user, workspace=workspace)
            permissions = MemberPermissions.objects.get(
                workspace=workspace,
                member=request_member,
                MANAGE_WORKSPACE_ROLES=True
            )
        except MemberPermissions.DoesNotExist:
            response["error"]["message"] = "You do not have permission modify roles in this workspace."
            return Response(response, status=status.HTTP_403_FORBIDDEN)
        except WorkspaceMember.DoesNotExist:
            response["error"]["message"] = "You are not a member of this workspace."
            return Response(response, status=status.HTTP_403_FORBIDDEN)

        # Verify that role exists and is part of workspace
        try:
            workspace_role = WorkspaceRole.objects.get(id=request.data['workspace_role_id'], workspace=workspace)
        except WorkspaceRole.DoesNotExist:
            response["error"]["message"] = "Role is not part of this workspace or does not exist."
            return Response(response, status=status.HTTP_404_NOT_FOUND)

        # Verify that member already has this role
        try:
            member_role = MemberRole.objects.get(member=request.data['member_id'], workspace_role=request.data['workspace_role_id'])
        except MemberRole.DoesNotExist:
            # add role to member if they did not have it
            response["error"]["message"] = "Member does not have this role."
            return Response(response, status=status.HTTP_404_NOT_FOUND)
        
        # remove role
        MemberRole.objects.get(member=request.data['member_id'], workspace_role=request.data['workspace_role_id']).delete()
        return Response(response, status=status.HTTP_200_OK)
    

        


        



