from django.shortcuts import render

def home(request):
    return render(request, 'forum/forums.html')

def search(request):
    return render(request, 'core/search.html')

def novidades(request):
    return render(request, 'core/novidades.html')