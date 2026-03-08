from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='users/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    path('recover-code/', views.recover_code_email, name='recover_code_email'),
    path('recover-code/questions/', views.recover_code_questions, name='recover_code_questions'),
    path('recover-code/success/', views.recover_code_success, name='recover_code_success'),
]
