from django.urls import path
from myapp import views
from myapp.middleware.rate_limiting import RateLimitingMiddleware 
from myapp.middleware.logging_middleware import RequestLoggingMiddleware
from django.utils.decorators import decorator_from_middleware
from myapp.admin import admin

# Create middleware decorators
rate_limiting_middleware = decorator_from_middleware(RateLimitingMiddleware)
logging_middleware = decorator_from_middleware(RequestLoggingMiddleware)

urlpatterns = [
    path('register/', views.RegisterView.as_view(), name='register'),
    path('', views.LoginView.as_view(), name='login'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('api/', logging_middleware(rate_limiting_middleware(views.ApiView.as_view())), name='api'),
    path('free/', views.FreeView.as_view(), name='free'),
    path('home/', views.HomeView.as_view(), name='home'),
    path('admin/', admin.site.urls),
]
