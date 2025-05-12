from django.shortcuts import render

def home(request):
    return render(request, 'forums.html')

def posts(request):
    return render(request, 'posts.html')

def detail(request):
    return render(request, 'detail.html')

def logout(request):
    return render(request, 'logout.html')

def login(request):
    return render(request, 'login.html')

def register(request):
    return render(request, 'register.html')

def search(request):
    return render(request, 'search.html')