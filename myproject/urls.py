from django.urls import path
from myapp import views
from myapp.admin import admin



urlpatterns = [
    path('register/', views.RegisterView.as_view(), name='register'),
    path('', views.LoginView.as_view(), name='login'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('api/', views.ApiView.as_view(), name='api'),
    path('free/', views.FreeView.as_view(), name='free'),
    path('home/', views.HomeView.as_view(), name='home'),
    path('admin/', admin.site.urls),
]
