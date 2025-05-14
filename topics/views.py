from django.shortcuts import render

def topicos(request):
    return render(request, 'topics/list.html')

def novos_topicos(request):
    return render(request, 'topics/novos_topicos.html')
