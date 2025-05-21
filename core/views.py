from django.shortcuts import render
from django.core.paginator import Paginator
from .search import search_posts

def search(request):
    return render(request, 'core/search.html')

def search_view(request):
    # Extrair parâmetros do GET - aqui a mágica acontece!
    termo = request.GET.get('termo', '')
    apenas_titulo = request.GET.get('apenas_titulo') == 'on'
    autor = request.GET.get('autor', '')
    data_inicio = request.GET.get('data_inicio', '')
    data_fim = request.GET.get('data_fim', '')
    min_respostas = request.GET.get('min_respostas', 0)
    try:
        min_respostas = int(min_respostas)
    except (ValueError, TypeError):
        min_respostas = 0
    prefixos = request.GET.get('prefixos', '')
    subforum = request.GET.get('subforum', '')
    incluir_subforuns = request.GET.get('incluir_subforuns') == 'on'
    ordenacao = request.GET.get('ordenacao', 'relevance')
    
    # Por padrão, não mostramos resultados se nenhum termo for fornecido
    resultados = []
    total_resultados = 0
    busca_realizada = False
    
    # Se há um termo de pesquisa ou autor, realizamos a busca
    if termo or autor or subforum:
        busca_realizada = True
        resultados = search_posts(
            termo=termo,
            apenas_titulo=apenas_titulo,
            autor=autor,
            data_inicio=data_inicio,
            data_fim=data_fim,
            min_respostas=min_respostas,
            prefixos=prefixos,
            subforum=subforum,
            incluir_subforuns=incluir_subforuns,
            ordenacao=ordenacao
        )
        total_resultados = resultados.count()
        
        # Paginação dos resultados
        page = request.GET.get('page', 1)
        try:
            page = int(page)
        except (ValueError, TypeError):
            page = 1
            
        paginator = Paginator(resultados, 20)  # 20 resultados por página
        resultados_paginados = paginator.get_page(page)
        resultados = resultados_paginados
    
    # Contexto para o template
    context = {
        'resultados': resultados,
        'termo': termo,
        'apenas_titulo': apenas_titulo,
        'autor': autor,
        'data_inicio': data_inicio,
        'data_fim': data_fim,
        'min_respostas': min_respostas,
        'prefixos': prefixos,
        'subforum': subforum,
        'incluir_subforuns': incluir_subforuns,
        'ordenacao': ordenacao,
        'total_resultados': total_resultados,
        'busca_realizada': busca_realizada
    }
    
    return render(request, 'core/search_results.html', context)