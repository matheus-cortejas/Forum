from django.shortcuts import render

def home(request):
    return render(request, 'forum/forums.html')

def topicos(request):
    return render(request, 'topics/list.html')

def posts(request):
    return render(request, 'posts/posts.html')

def detail(request):
    return render(request, 'posts/detail.html')

def logout(request):
    return render(request, 'accounts/logout.html')

def login(request):
    return render(request, 'accounts/login.html')

def register(request):
    return render(request, 'accounts/register.html')

def search(request):
    return render(request, 'core/search.html')

def novos_topicos(request):
    return render(request, 'topics/novos_topicos.html')

def novos_posts(request):
    return render(request, 'posts/novos_posts.html')

def novidades(request):
    return render(request, 'core/novidades.html')

def members(request):
    return render(request, 'accounts/members.html')

def online(request):
    return render(request, 'accounts/online.html')

def profile(request):
    return render(request, 'accounts/profile.html')