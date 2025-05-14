from django.shortcuts import render

def logout(request):
    return render(request, 'accounts/logout.html')

def login(request):
    return render(request, 'accounts/login.html')

def register(request):
    return render(request, 'accounts/register.html')

def members(request):
    return render(request, 'accounts/members.html')

def online(request):
    return render(request, 'accounts/online.html')

def profile(request):
    return render(request, 'accounts/profile.html')
