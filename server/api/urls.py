from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    Login,
    Register,
    GetUser,
    WorkspaceView,
    GetPermissions,
    UpdatePermissions,
    AddWorkspaceMember,
    CreateRole,
    GetWorkspaceRoles,
    AddMemberRole,
    RemoveMemberRole,
    DeleteWorkspaceRole,
    GetMemberRoles,
    ModifyWorkspaceRole,
    CreateShift,
    ModifyShift,
    DeleteShift,
    GetShifts,
    GetWorkspaceMembers,
)

urlpatterns = [
    path("login", Login.as_view(), name="login"),
    path("register", Register.as_view(), name="register"),
    path("user", GetUser.as_view(), name="get_user"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("workspace/", WorkspaceView.as_view(), name="workspace"),
    path(
        "workspace/<int:workspace_id>/",
        WorkspaceView.as_view(),
        name="workspace_parameters",
    ),
    path(
        "workspace/get-members/<int:workspace_id>/",
        GetWorkspaceMembers.as_view(),
        name="get_workspace_members",
    ),
    path(
        "workspace/get-members/",
        GetWorkspaceMembers.as_view(),
        name="get_workspace_members_no_id",
    ),
    path("workspace/permissions/", GetPermissions.as_view(), name="get_permissions"),
    path(
        "workspace/permissions/update/",
        UpdatePermissions.as_view(),
        name="update_permissions",
    ),
    path(
        "workspace/add-user/<int:workspace_id>/",
        AddWorkspaceMember.as_view(),
        name="add_workspace_member",
    ),
    path(
        "workspace/add-user/",
        AddWorkspaceMember.as_view(),
        name="add_workspace_member_no_id",
    ),
    path("workspace/create-role/", CreateRole.as_view(), name="create_workspace_role"),
    path(
        "workspace/delete-role",
        DeleteWorkspaceRole.as_view(),
        name="delete_workspace_role",
    ),
    path(
        "workspace/modify-role/",
        ModifyWorkspaceRole.as_view(),
        name="modify_workspace_role",
    ),
    path(
        "workspace/get-roles/", GetWorkspaceRoles.as_view(), name="get_workspace_roles"
    ),
    path(
        "workspace/get-member-roles/", GetMemberRoles.as_view(), name="get_member_roles"
    ),
    path("workspace/add-role/", AddMemberRole.as_view(), name="add_member_role"),
    path(
        "workspace/remove-role", RemoveMemberRole.as_view(), name="remove_member_role"
    ),
    path("workspace/create-shift", CreateShift.as_view(), name="create_shift"),
    path("workspace/modify-shift", ModifyShift.as_view(), name="modify_shift"),
    path("workspace/delete-shift", DeleteShift.as_view(), name="delete_shift"),
    path("workspace/get-shifts", GetShifts.as_view(), name="get_shifts"),
]
