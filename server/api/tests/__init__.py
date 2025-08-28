# Import from new organized structure
from .auth.test_login import LoginTests
from .auth.test_registration import RegisterTests
from .users.test_user_retrieval import GetUserTests
from .users.test_user_updates import UpdateUserTests
from .permissions.test_permission_updates import UpdatePermissionsTests
from .workspaces.test_workspace_members import AddMemberTests
from .workspaces.test_workspace_crud import ModifyWorkspaceTests, DeleteWorkspaceTests
from .workspaces.test_workspace_queries import GetWorkspaceTests
from .roles.test_role_crud import CreateRoleTests, DeleteRoleTests, ModifyWorkspaceRoleTests
from .roles.test_role_queries import GetRolesTests, GetMemberRoleTests
from .roles.test_member_roles import AddMemberRoleTests, RemoveMemberRoleTests
from .shifts.test_shift_crud import CreateShiftTests, ModifyShiftTests, DeleteShiftTests
from .shifts.test_shift_queries import GetShiftsTest
