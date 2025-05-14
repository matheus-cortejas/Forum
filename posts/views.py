from django.shortcuts import render

def posts(request):
    return render(request, 'posts/posts.html')

def detail(request):
    return render(request, 'posts/detail.html')

def novos_posts(request):
    return render(request, 'posts/novos_posts.html')
