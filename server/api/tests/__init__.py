from .auth import LoginTests, RegisterTests
from .user import GetUserTests, UpdateUserTests
from .permissions import UpdatePermissionsTests
from .workspace import (
    AddMemberTests,
    ModifyWorkspaceTests,
    GetWorkspaceTests,
    DeleteWorkspaceTests,
)
from .role import (
    CreateRoleTests,
    GetRolesTests,
    AddMemberRoleTests,
    RemoveMemberRoleTests,
    DeleteRoleTests,
    GetMemberRoleTests,
    ModifyWorkspaceRoleTests,
)
from .shift import CreateShiftTests, ModifyShiftTests, DeleteShiftTests, GetShiftsTest
