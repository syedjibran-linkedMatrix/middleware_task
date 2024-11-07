#views.py
from datetime import timedelta
from django.contrib.auth import login, logout
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.contrib.auth import get_user_model
from django.views.generic import View, TemplateView
from django.shortcuts import redirect
from django.contrib import messages
from myapp.models import CustomUser 
from django.utils import timezone  


User = get_user_model()


@method_decorator(csrf_exempt, name="dispatch")
class RegisterView(TemplateView):
    template_name = "myapp/register.html"

    def post(self, request, *args, **kwargs):
        try:
            # Get the POST data
            data = request.POST
            email = data.get("email")
            password = data.get("password")
            user_type = data.get("user_type", "DEFAULT")  # Default to "DEFAULT" if not provided

            # Validate required fields
            if not email or not password:
                return JsonResponse(
                    {"error": "Email and password are required"}, status=400
                )

            # Ensure the user_type is valid
            if user_type not in ["BRONZE", "SILVER", "GOLD", "DEFAULT"]:
                return JsonResponse(
                    {"error": "Invalid user type"}, status=400
                )

            # Create user with the specified type
            user = CustomUser.objects.create_user(
                email=email, password=password, user_type=user_type
            )

            return redirect("login")  # Redirect to login page after successful registration

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)


@method_decorator(csrf_exempt, name="dispatch")
class LoginView(TemplateView):
    template_name = "myapp/login.html"

    def post(self, request, *args, **kwargs):
        try:
            data = request.POST
            email = data.get("email")
            password = data.get("password")

            if not email or not password:
                return JsonResponse(
                    {"error": "Email and password are required"}, status=400
                )

            user = User.objects.get(email=email)
            if user.check_password(password):
                login(request, user)
                return redirect("home")
            else:
                return JsonResponse({"error": "Invalid credentials"}, status=401)
        except User.DoesNotExist:
            return JsonResponse({"error": "User not found"}, status=404)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)


class LogoutView(View):
    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            logout(request)
            return redirect("login")
        else:
            logout(request)
            messages.warning(request, "You are not logged in.")
            return redirect("home")


class HomeView(TemplateView):
    template_name = "myapp/home.html"


class ApiView(View):
    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({"error": "User is not authenticated"}, status=403)

        user = request.user
        rate_limit = user.get_rate_limit()

        return JsonResponse({
            "status": "success",
            "user": {
                "email": user.email,
                "type": user.user_type,
            },
            "rate_limiting": {
                "current_requests": user.hit_count,
                "rate_limit": rate_limit,
                "window_size": "1 minute"
            }
        })

    def error_response(self, message, status):
        return JsonResponse({"error": message}, status=status)



class FreeView(View):
    def get(self, request, *args, **kwargs):
        return JsonResponse({"message": "This is a free endpoint"})
