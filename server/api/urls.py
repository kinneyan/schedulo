from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    Login,
    Register,
    GetUser,
    WorkspaceView,
    WorkspaceMembersView,
    WorkspaceRolesView,
    WorkspaceShiftsView,
    MemberView,
    MemberPermissionsView,
    MemberRolesView,
    MemberShiftsView,
    PermissionsView,
    ShiftView,
    ShiftFilterView,
    RoleView
)

urlpatterns = [
    path("login", Login.as_view(), name="login"),
    path("register", Register.as_view(), name="register"),
    path("user", GetUser.as_view(), name="get_user"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("workspace/", WorkspaceView.as_view(), name="workspace"),
    path("workspace/<int:workspace_id>/", WorkspaceView.as_view(), name="workspace_parameters"),
    path("workspace/<int:workspace_id>/members/", WorkspaceMembersView.as_view(), name="workspace_members"),
    path("workspace/<int:workspace_id>/shifts/", WorkspaceShiftsView.as_view(), name="workspace_shifts"),
    path("workspace/<int:workspace_id>/roles/", WorkspaceRolesView.as_view(), name="workspace_roles"),
    path("member/<int:member_id>/", MemberView.as_view(), name="member"),
    path("member/<int:member_id>/permissions/", MemberPermissionsView.as_view(), name="member_permissions"),
    path("member/<int:member_id>/roles/", MemberRolesView.as_view(), name="member_roles"),
    path("member/<int:member_id>/shifts/", MemberShiftsView.as_view(), name="member_shifts"),
    path("permissions/", PermissionsView.as_view(), name="permissions"),
    path("shift/<int:shift_id>/", ShiftView.as_view(), name="shift"),
    path("shift/filter/", ShiftFilterView.as_view(), name="shift_filter"),
    path("role/<int:role_id>/", RoleView.as_view(), name="role")
]
