from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import Login, Register, GetUser, CreateWorkspace, ModifyWorkspace, GetPermissions, UpdatePermissions, AddWorkspaceMember, CreateRole

urlpatterns = [
    path('login', Login.as_view(), name='login'),
    path('register', Register.as_view(), name='register'),
    path('user', GetUser.as_view(), name='get_user'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('workspace/create/', CreateWorkspace.as_view(), name='create_workspace'),
    path('workspace/modify/', ModifyWorkspace.as_view(), name='modify_workspace'),
    path('workspace/permissions/', GetPermissions.as_view(), name='get_permissions'),
    path('workspace/permissions/update/', UpdatePermissions.as_view(), name='update_permissions'),
    path('workspace/add-user/', AddWorkspaceMember.as_view(), name='add_workspace_member'),
    path('workspace/create-role/', CreateRole.as_view(), name='create_role')
]
