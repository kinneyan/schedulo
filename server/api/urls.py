from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import Login, Register, GetUser, CreateWorkspace, AddWorkspaceMember

urlpatterns = [
    path('login', Login.as_view(), name='login'),
    path('register', Register.as_view(), name='register'),
    path('user', GetUser.as_view(), name='get_user'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('workspace/create/', CreateWorkspace.as_view(), name='create_workspace'),
    path('workspace/add-user/', AddWorkspaceMember.as_view(), name='add_workspace_member')
]
