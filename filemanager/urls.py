from django.urls import path
from . import views
from django.http import HttpResponseRedirect

app_name = 'filemanager'

urlpatterns = [
    path('', lambda request: HttpResponseRedirect('upload/')),
    path('accounts/login/', views.login_view, name='login'),
    path('accounts/logout/', views.logout_view, name='logout'),
    path('user_page/', views.user_page, name='user_page'),
    path('upload/', views.file_upload, name='file_upload'),
    path('admin_page/', views.admin_page, name='admin_page'),
    path('admin_page/manage-photos/', views.admin_manage_photos, name='admin_manage_photos'),
    path('user_list/', views.user_list, name='user_list'),
    path('delete_user/<int:user_id>/', views.delete_user, name='delete_user'),
    path('edit_user/<int:user_id>/', views.edit_user, name='edit_user'),
]
