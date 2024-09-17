import requests
from django.shortcuts import render, redirect
from django.views import View
from .forms import RegistrationForm, LoginForm
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.contrib import messages


class HomeView(View):
    def get(self, request):
        access_token = request.COOKIES['access_token']

        if not access_token:
            return HttpResponseRedirect('login')
        headers = {
            'Authorization': f'Bearer {access_token}'
        }

        response = requests.get('http://127.0.0.3:8002/auth/token/verify', headers=headers)

        if response.status_code == 200:
            return render(request, 'home.html')
        elif response.status_code == 401:
            response = HttpResponseRedirect('/login/')
            response.delete_cookie('access_token')
            return response
        else:
            return HttpResponse("Noma'lum xato yuz berdi", status=500)


class RegisterView(View):
    def get(self, request):
        form = RegistrationForm
        return render(request, 'register.html', {"form": form})

    def post(self, request):
        form = RegistrationForm(request.POST)
        if form.is_valid():
            url = "http://127.0.0.3:8002/auth/register"
            data = {
                "username": form.cleaned_data['username'],
                "email": form.cleaned_data['email'],
                "password": form.cleaned_data['password']
            }
            response = requests.post(url, json=data)
            print(response.json())
            if response.json()["status_code"] == 201:
                return HttpResponse("User registered successfully")

            else:
                return HttpResponse(f"Error: {response.json()['detail']}")

        else:
            return HttpResponse("Form is not valid")


class LoginView(View):
    def get(self, request):
        return render(request, 'home.html')
    def get(self, request):
        form = LoginForm()
        return render(request, 'login.html', {"form": form})

    def post(self, request):
        form = LoginForm(request.POST)
        if form.is_valid():
            url = "http://127.0.0.3:8002/auth/login"
            data = {
                "username_or_email": form.cleaned_data['username'],
                "password": form.cleaned_data['password']
            }
            response = requests.post(url, json=data)

            if response.json()["status_code"] == 200:
                access_token = response.json()['access_token']

                response = redirect('home')
                response.set_cookie('access_token', access_token, httponly=True)
                return response
            else:
                messages.error(request, "Invalid login credentials")

        return render(request, 'login.html')


class PostGetView(View):
    def get(self, request):
        return render(request, 'post.html')

    def post(self, request):
        caption = request.POST.get('caption')
        image_path = request.POST.get('image_path')

        api_url = 'http://127.0.0.3:8002/posts/create'

        data = {
            "caption": caption,
            "image_path": image_path
        }

        response = requests.post(api_url, json=data)
        if response.status_code == 200:
            return render(request, 'post.html')

        else:
            return JsonResponse({'error': 'Failed to login user', 'details': response.json()},
                                status=response.status_code)

    def get(self, request, *args, **kwargs):
        page = requests.get("http://127.0.0.3:8002/posts/?size=2").json()['page']
        pages = requests.get("http://127.0.0.3:8003/posts/?size=2").json()["pages"]

        if page is not None:
            if int(page) <= int(pages):
                data = requests.get(f"http://127.0.0.3:8002/posts/?size=2").json()["items"]
                return render(request, "post.html",
                              context={"posts": data, "pages": pages, "page": 1, "next": 2, "previous": 0})

            data = requests.get(f"http://127.0.0.3:8002/posts/?page={page}&size=2").json()["items"]
            return render(request, "post.html",
                          context={"posts": data, "pages": pages, "page": page, "next": int(page) + 1,
                                   "previous": int(page) - 1})

        return render(request, "post.html", context={"message": "Not found"})
