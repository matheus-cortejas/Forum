from django.shortcuts import render

def search(request):
    return render(request, 'core/search.html')

def novidades(request):
    return render(request, 'core/novidades.html')
