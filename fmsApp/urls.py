from django.contrib import admin
from django.urls import path
from django.conf.urls.static import static
from . import views
from django.contrib.auth import views as auth_views
from django.views.generic.base import RedirectView

urlpatterns = [
    path('redirect-admin', RedirectView.as_view(url="/admin"),name="redirect-admin"),
    path('', views.home, name='home-page'),  # Map the root URL to the home view
    path('login',auth_views.LoginView.as_view(template_name="login.html",redirect_authenticated_user = True),name='login'),
    path('userlogin', views.login_user, name="login-user"),
    path('user-register', views.registerUser, name="register-user"),
    path('logout',views.logoutuser,name='logout'),
    path('profile',views.profile,name='profile'),
    path('update-profile',views.update_profile,name='update-profile'),
    # path('update-avatar',views.update_avatar,name='update-avatar'),
    path('update-password',views.update_password,name='update-password'),
    path('portal', views.portal, name='portal'), # Login required
    path('tools', views.tools, name='tools'), # No login required
    path('calendar', views.calendar, name='calendar'), # No login required
    path('training_folder', views.training_folder, name='training_folder'), #login required
    path('inventory', views.inventory, name='inventory'), # login required
    path('reports', views.reports, name='reports'), # login required
    path('home', views.home, name='home-page'),
    path('my_posts', views.posts_mgt, name='posts-page'),
    path('manage_post', views.manage_post, name='manage-post'),
    path('manage_post/<int:pk>', views.manage_post, name='manage-post'),
    path('save_post', views.save_post, name='save-post'),
    path('delet_post', views.delete_post, name='delete-post'),
    path(r'shareF/<str:id>', views.shareF, name='share-file-id'),
    path('shareF/', views.shareF, name='share-file'),
]
