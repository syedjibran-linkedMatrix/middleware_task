from django.contrib.auth import login, logout
from django.views.generic import View
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.views.generic import View, TemplateView
from django.shortcuts import redirect
from django.contrib import messages 




User = get_user_model()

@method_decorator(csrf_exempt, name='dispatch')
class RegisterView(TemplateView):
    template_name = 'myapp/register.html'
    def post(self, request, *args, **kwargs):
        try:
            data = request.POST
            email = data.get('email')
            password = data.get('password')
            user_type = data.get('user_type', 'BRONZE')

            if not email or not password:
                return JsonResponse({'error': 'Email and password are required'}, 
                                 status=400)

            user = User.objects.create_user(
                email=email,
                password=password,
                user_type=user_type
            )
        
            
            return redirect('login')
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
        


@method_decorator(csrf_exempt, name='dispatch')
class LoginView(TemplateView):
    template_name = 'myapp/login.html' 
    def post(self, request, *args, **kwargs):
        try:
            data = request.POST
            email = data.get('email')
            password = data.get('password')

            if not email or not password:
                return JsonResponse({'error': 'Email and password are required'}, 
                                 status=400)

            user = User.objects.get(email=email)
            if user.check_password(password):
                login(request, user)
                return redirect('home')
            else:
                return JsonResponse({'error': 'Invalid credentials'}, status=401)
        except User.DoesNotExist:
            return JsonResponse({'error': 'User not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

class LogoutView(View):
    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            logout(request)  
            return redirect('login')  
        else:
            logout(request)
            messages.warning(request, "You are not logged in.")  # Show warning message
            return redirect('home')


    
class HomeView(TemplateView):
    template_name = 'myapp/home.html'

class ApiView(View):
    def get(self, request, *args, **kwargs):
        ip_address = request.META.get('REMOTE_ADDR')
        cache_key = f'rate_limit_{ip_address}'
        requests = cache.get(cache_key, [])

        # Check if the user is authenticated to set the rate limit
        if request.user.is_authenticated:
            if request.user.user_type == 'GOLD':
                rate_limit = 10
            elif request.user.user_type == 'SILVER':
                rate_limit = 5
            elif request.user.user_type == 'BRONZE':
                rate_limit = 2
            else:
                rate_limit = 1
        else:
            # Rate limit for unauthenticated users
            rate_limit = 1

        return JsonResponse({
            'hit_count': len(requests),
            'rate_limit': rate_limit
        })

class FreeView(View):
    def get(self, request, *args, **kwargs):
        return JsonResponse({'message': 'This is a free endpoint'})