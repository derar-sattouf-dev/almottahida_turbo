from django.contrib import messages
from django.contrib.auth import authenticate, logout, login
from django.shortcuts import render, redirect


def home(request):
    return render(request, "home.html")


def login_user(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(username=username, password=password)

        if user is None:
            messages.add_message(request, messages.WARNING, 'Wrong username or password.')
            return render(request, "users/login.html")
        else:
            login(request, user)
            print(request.GET.get("next"))
            if request.GET.get("next") is not None:
                return redirect(request.GET.get('next'))
            else:
                return redirect("home")
    else:
        return render(request, "users/login.html")


def logout_user(request):
    logout(request)
    return redirect("users.login")
