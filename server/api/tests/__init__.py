# Import from integration tests
from .integration.auth.test_login import LoginTests
from .integration.auth.test_registration import RegisterTests
from .integration.users.test_user_retrieval import GetUserTests
from .integration.users.test_user_updates import UpdateUserTests
from .integration.permissions.test_permission_updates import UpdatePermissionsTests
from .integration.workspaces.test_workspace_members import AddMemberTests
from .integration.workspaces.test_workspace_crud import (
    ModifyWorkspaceTests,
    DeleteWorkspaceTests,
)
from .integration.workspaces.test_workspace_queries import GetWorkspaceTests
from .integration.roles.test_role_crud import (
    CreateRoleTests,
    DeleteRoleTests,
    ModifyWorkspaceRoleTests,
)
from .integration.roles.test_role_queries import GetRolesTests, GetMemberRoleTests
from .integration.roles.test_member_roles import (
    AddMemberRoleTests,
    RemoveMemberRoleTests,
)
from .integration.shifts.test_shift_crud import (
    CreateShiftTests,
    ModifyShiftTests,
    DeleteShiftTests,
)
from .integration.shifts.test_shift_queries import GetShiftsTest

# Unit tests will be imported here as they are added
# from .unit.models.test_user_model import UserModelTests
# from .unit.serializers.test_user_serializer import UserSerializerTests
# etc...
