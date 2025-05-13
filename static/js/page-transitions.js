document.addEventListener('DOMContentLoaded', function() {
    // Criar o overlay de carregamento
    const loadingOverlay = document.createElement('div');
    loadingOverlay.className = 'page-loading-overlay';
    loadingOverlay.innerHTML = '<div class="page-loading-spinner"></div>';
    document.body.appendChild(loadingOverlay);

    // Interceptar cliques em links
    document.addEventListener('click', function(event) {
        // Verificar se o clique foi em um link ou botão de navegação
        const link = event.target.closest('a, button[type="submit"]');
        
        if (link && !event.ctrlKey && !event.metaKey) {
            // Ignorar links que abrem em nova aba ou são # ou javascript:
            if (link.target === '_blank' || 
                link.href.includes('javascript:') || 
                (link.tagName === 'A' && link.getAttribute('href') === '#') ||
                link.classList.contains('dropdown-toggle') ||
                link.closest('.dropdown-menu')) {
                return;
            }
            
            // Adicionar estado de loading ao elemento clicado
            if (!link.querySelector('.loading-spinner')) {
                link.classList.add('loading');
                const spinner = document.createElement('span');
                spinner.className = 'loading-spinner';
                link.appendChild(spinner);
            }
            
            // Para formulários, mostrar overlay ao submeter
            if (link.tagName === 'BUTTON' && link.type === 'submit') {
                const form = link.closest('form');
                if (form) {
                    form.addEventListener('submit', function() {
                        loadingOverlay.classList.add('visible');
                    }, { once: true });
                }
            } 
            // Para links regulares, mostrar overlay após pequeno delay
            else if (link.tagName === 'A' && link.getAttribute('href')) {
                setTimeout(function() {
                    loadingOverlay.classList.add('visible');
                }, 150); // Pequeno delay para mostrar o efeito no botão primeiro
            }
        }
    });

    // Pré-carregar páginas ao hover sobre links
    const preloadCache = {};
    
    document.addEventListener('mouseover', function(event) {
        const link = event.target.closest('a');
        if (link && 
            link.href && 
            link.hostname === window.location.hostname &&
            !link.href.includes('#') &&
            !preloadCache[link.href]) {
            
            // Marcar como em cache para não solicitar novamente
            preloadCache[link.href] = true;
            
            // Pré-carregar a página
            const prefetchLink = document.createElement('link');
            prefetchLink.rel = 'prefetch';
            prefetchLink.href = link.href;
            document.head.appendChild(prefetchLink);
        }
    });
});
