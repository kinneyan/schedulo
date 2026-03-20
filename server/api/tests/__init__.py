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
from .integration.workspaces.test_workspace_queries import (
    GetWorkspaceTests,
    GetWorkspaceMembersTests,
    GetWorkspaceShiftsTests,
)
from .integration.roles.test_role_crud import (
    CreateRoleTests,
    DeleteRoleTests,
    ModifyWorkspaceRoleTests,
    GetRoleTests,
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
    GetShiftTests,
)
from .integration.shifts.test_shift_queries import GetShiftsTest
from .integration.members.test_member_crud import GetMemberTests
from .integration.members.test_member_queries import GetMemberPermissionsTests

# Import from unit tests
from .unit.models.test_user_models import (
    CustomUserManagerTest,
    UserModelTest,
    WorkspaceModelTest,
    WorkspaceMemberModelTest,
)
from .unit.models.test_role_models import (
    WorkspaceRoleModelTest,
    MemberRoleModelTest,
    MemberPermissionsModelTest,
)
from .unit.models.test_schedule_models import (
    ShiftModelTest,
    ShiftRequestModelTest,
    TimeOffRequestModelTest,
    UnavailabilityModelTest,
)
from .unit.serializers.test_user_serializers import (
    LoginUserSerializerTest,
    RegisterUserSerializerTest,
)
from .unit.serializers.test_role_serializers import RoleSerializerTest
from .unit.views.test_auth_views import RegisterViewTest
