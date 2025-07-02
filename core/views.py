from django.shortcuts import render
from django.core.paginator import Paginator
from .search import search_posts, search_users, search_member_posts

def search(request):
    return render(request, 'core/search.html')

def search_view(request):
    # Determinar tipo de pesquisa
    search_type = request.GET.get('search_type', 'conteudo')
    
    if search_type == 'usuarios':
        return search_users_view(request)
    elif search_type == 'postagens_membro':
        return search_member_posts_view(request)
    
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

def search_users_view(request):
    """View específica para pesquisa de usuários"""
    username = request.GET.get('username', '')
    email = request.GET.get('email', '')
    data_registro_inicio = request.GET.get('data_registro_inicio', '')
    data_registro_fim = request.GET.get('data_registro_fim', '')
    ordenacao_user = request.GET.get('ordenacao_user', 'username')
    
    resultados = []
    total_resultados = 0
    busca_realizada = False
    
    if username or email:
        busca_realizada = True
        resultados = search_users(
            username=username,
            email=email,
            data_registro_inicio=data_registro_inicio,
            data_registro_fim=data_registro_fim,
            ordenacao=ordenacao_user
        )
        total_resultados = resultados.count()
        
        # Paginação
        page = request.GET.get('page', 1)
        try:
            page = int(page)
        except (ValueError, TypeError):
            page = 1
            
        paginator = Paginator(resultados, 20)
        resultados = paginator.get_page(page)
    
    context = {
        'resultados': resultados,
        'username': username,
        'email': email,
        'data_registro_inicio': data_registro_inicio,
        'data_registro_fim': data_registro_fim,
        'ordenacao_user': ordenacao_user,
        'total_resultados': total_resultados,
        'busca_realizada': busca_realizada,
        'search_type': 'usuarios'
    }
    
    return render(request, 'core/search_results.html', context)

def search_member_posts_view(request):
    """View específica para pesquisa de postagens de um membro"""
    membro_username = request.GET.get('membro_username', '')
    tipo_conteudo = request.GET.get('tipo_conteudo', 'todos')
    membro_data_inicio = request.GET.get('membro_data_inicio', '')
    membro_data_fim = request.GET.get('membro_data_fim', '')
    membro_subforum = request.GET.get('membro_subforum', '')
    membro_ordenacao = request.GET.get('membro_ordenacao', 'date')
    
    resultados = []
    total_resultados = 0
    busca_realizada = False
    membro_encontrado = None
    
    if membro_username:
        busca_realizada = True
        resultados, membro_encontrado = search_member_posts(
            username=membro_username,
            tipo_conteudo=tipo_conteudo,
            data_inicio=membro_data_inicio,
            data_fim=membro_data_fim,
            subforum=membro_subforum,
            ordenacao=membro_ordenacao
        )
        total_resultados = resultados.count() if resultados else 0
        
        # Paginação
        if resultados:
            page = request.GET.get('page', 1)
            try:
                page = int(page)
            except (ValueError, TypeError):
                page = 1
                
            paginator = Paginator(resultados, 20)
            resultados = paginator.get_page(page)
    
    context = {
        'resultados': resultados,
        'membro_username': membro_username,
        'membro_encontrado': membro_encontrado,
        'tipo_conteudo': tipo_conteudo,
        'membro_data_inicio': membro_data_inicio,
        'membro_data_fim': membro_data_fim,
        'membro_subforum': membro_subforum,
        'membro_ordenacao': membro_ordenacao,
        'total_resultados': total_resultados,
        'busca_realizada': busca_realizada,
        'search_type': 'postagens_membro'
    }
    
    return render(request, 'core/search_results.html', context)