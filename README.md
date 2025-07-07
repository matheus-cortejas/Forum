# Forum
Django Discussion forum inspired at Invision Style but with the "modern face"

## Visão Geral

Este é um projeto de fórum de discussão completo, construído com Django. Ele foi projetado para ser uma plataforma moderna, rica em recursos e interativa para comunidades online. A inspiração visual vem de plataformas como Invision Community, mas com uma abordagem de design e funcionalidades atualizadas.

## Funcionalidades Principais

- **Estrutura de Fórum Clássica**: Organizado em Categorias e Assuntos para uma navegação intuitiva.
- **Tipos de Conteúdo**: Suporte para Tópicos (Threads) e Posts simples.
- **Sistema de Respostas (Replies)**: Usuários podem responder a tópicos, com um editor de texto e contador de caracteres.
- **Reações**: Sistema de reações (like, haha, etc.) para postagens e respostas, similar às redes sociais modernas.
- **Perfis de Usuário**: Perfis detalhados com avatar, biografia, estatísticas (posts, reputação), e a habilidade de seguir outros usuários.
- **Feed de Atividades Recentes**: Uma página dedicada que mostra as últimas atividades no fórum, como novos tópicos, respostas e reações, com opções de filtro.
- **Filtros Avançados**: Poderoso sistema de filtros para tópicos e posts, permitindo buscas por prefixo, tags, autor, e data.
- **Usuários Online**: Widget e página que mostram quem está online (membros, visitantes e bots).
- **Notificações Visuais**: Notificações em tempo real (toast) para novas atividades e interações.
- **Design Responsivo**: Interface adaptada para funcionar em desktops, tablets e dispositivos móveis.
- **Transições de Página Suaves**: Efeitos de carregamento para uma experiência de usuário mais fluida.

## Bibliotecas e Tecnologias Utilizadas

### Backend (Python/Django)
- **Django**: O framework web principal para toda a lógica de backend.
- **django-colorfield**: Para fornecer um seletor de cores amigável no painel de administração (usado para cargos de membros).

### Frontend
- **HTML5 / CSS3**: Estrutura e estilização.
- **JavaScript (Vanilla)**: Para toda a interatividade do lado do cliente, incluindo requisições AJAX, manipulação de DOM e componentes dinâmicos.
- **Font Awesome**: Para ícones em toda a interface.

## Como Executar o Projeto

### Pré-requisitos
- Python 3.8+
- pip (gerenciador de pacotes Python)

### Instalação
1.  **Clone o repositório:**
    ```bash
    git clone <url-do-seu-repositorio>
    cd Forum
    ```

2.  **Crie e ative um ambiente virtual:**
    ```bash
    # Windows
    python -m venv venv
    .\venv\Scripts\activate

    # macOS/Linux
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Instale as dependências:**
    ```bash
    pip install Django django-colorfield
    ```

4.  **Aplique as migrações do banco de dados:**
    O projeto inclui migrações de dados para popular o fórum com categorias, usuários e posts de exemplo, facilitando o teste inicial.
    ```bash
    python manage.py migrate
    ```

5.  **Crie um superusuário (opcional, se a migração não criar um 'admin'):**
    ```bash
    python manage.py createsuperuser
    ```

6.  **Execute o servidor de desenvolvimento:**
    ```bash
    python manage.py runserver
    ```

7.  Acesse o fórum em `http://127.0.0.1:8000/` no seu navegador.
    -   O painel de administração estará disponível em `http://127.0.0.1:8000/admin/`.
    -   As credenciais de exemplo (se as migrações foram executadas) são `admin` / `123456`.

## Estrutura do Projeto

-   `Forum/`: Configurações principais do projeto Django.
-   `accounts/`: App para gerenciamento de usuários, perfis, autenticação e cargos.
-   `core/`: App para funcionalidades centrais, como o feed de atividades, estatísticas e o sistema de pesquisa.
-   `home/`: App responsável pela página inicial e listagem de categorias/assuntos.
-   `posts/`: App que gerencia postagens, tópicos, respostas, tags e reações.
-   `static/`: Contém todos os arquivos estáticos (CSS, JavaScript, imagens).
-   `templates/`: Contém os templates HTML do projeto.
-   `media/`: Diretório onde os uploads de usuários (como avatares) são armazenados.
