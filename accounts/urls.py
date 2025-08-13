from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('login-page/', views.login_page, name='login_page'),
    path('signup/', views.signup_view, name='signup'),
    path('logout/', views.logout_view, name='logout'),
    path('check-auth/', views.check_auth, name='check_auth'),
    path('google/login/', views.google_login, name='google_login'),
    path('google/callback/', views.google_callback, name='google_callback'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/update/', views.profile_update, name='profile_update'),
] 