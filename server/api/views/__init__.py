from .auth import Login, Register
from .user import GetUser
from .permissions import GetPermissions, UpdatePermissions
from .workspace import CreateWorkspace, AddWorkspaceMember, ModifyWorkspace
from .role import CreateRole, GetWorkspaceRoles, AddMemberRole, RemoveMemberRole, DeleteWorkspaceRole, GetMemberRoles, ModifyWorkspaceRole
from .shift import CreateShift, ModifyShift, DeleteShift, GetShifts
