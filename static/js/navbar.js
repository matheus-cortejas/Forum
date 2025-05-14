document.addEventListener('DOMContentLoaded', function() {
    const dropdownToggles = document.querySelectorAll('.dropdown-toggle');
    
    dropdownToggles.forEach(toggle => {
        toggle.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            
            // Feedback visual imediato
            this.classList.toggle('active');
            
            const dropdownMenu = this.nextElementSibling;
            const isExpanded = this.getAttribute('aria-expanded') === 'true';
            
            // Fecha todos os outros menus
            dropdownToggles.forEach(t => {
                if (t !== this) {
                    t.setAttribute('aria-expanded', 'false');
                    t.classList.remove('active');
                    t.nextElementSibling.setAttribute('aria-hidden', 'true');
                    t.nextElementSibling.classList.remove('show');
                }
            });
            
            // Toggle do menu atual
            this.setAttribute('aria-expanded', !isExpanded);
            dropdownMenu.setAttribute('aria-hidden', isExpanded);
            dropdownMenu.classList.toggle('show');
            
            // Remover qualquer ajuste manual de posição
            dropdownMenu.style.left = '';
            dropdownMenu.style.top = '';
        });
    });
    
    // Fecha os menus quando clicar fora
    document.addEventListener('click', function(e) {
        if (!e.target.matches('.dropdown-toggle')) {
            document.querySelectorAll('.dropdown-menu.show').forEach(menu => {
                menu.classList.remove('show');
            });
            dropdownToggles.forEach(toggle => {
                toggle.setAttribute('aria-expanded', 'false');
                toggle.nextElementSibling.setAttribute('aria-hidden', 'true');
                toggle.classList.remove('active');
            });
        }
    });

    // Melhorar a detecção de tamanho de tela
    const mobileMediaQuery = window.matchMedia('(max-width: 768px)');
    
    // Função para ajustar posicionamento de dropdown em mobile
    function positionDropdowns() {
        if (mobileMediaQuery.matches) {
            document.querySelectorAll('.dropdown-menu').forEach(menu => {
                // Garantir que menus não saiam da tela em mobile
                const menuRect = menu.getBoundingClientRect();
                const windowWidth = window.innerWidth;
                
                if (menuRect.right > windowWidth) {
                    menu.style.left = 'auto';
                    menu.style.right = '0';
                }
            });
        }
    }
    
    // Chamar quando o tamanho da tela muda
    mobileMediaQuery.addEventListener('change', positionDropdowns);
    
    // Chamar na inicialização
    positionDropdowns();

    // Mobile menu toggle
    const mobileMenuToggle = document.querySelector('.mobile-menu-toggle');
    const navigation = document.querySelector('.navigation');
    const navButtons = document.querySelector('.nav-buttons');
    
    // Verificar estado inicial baseado no tamanho da tela
    function updateMobileState() {
        const isMobileView = mobileMediaQuery.matches;
        
        // Garantir que o menu mobile esteja no estado correto
        if (!isMobileView) {
            navigation.classList.remove('active');
            navButtons.classList.remove('mobile-active');
            if (mobileMenuToggle) {
                mobileMenuToggle.classList.remove('active');
                mobileMenuToggle.setAttribute('aria-expanded', 'false');
            }
        }
    }
    
    // Executar ao carregar e quando a tela for redimensionada
    updateMobileState();
    window.addEventListener('resize', updateMobileState);
    
    if (mobileMenuToggle) {
        mobileMenuToggle.addEventListener('click', function() {
            this.classList.toggle('active');
            navigation.classList.toggle('active');
            
            // Se o menu estiver aberto, adicione a classe active aos botões de navegação
            if (this.classList.contains('active')) {
                navButtons.classList.add('mobile-active');
                this.setAttribute('aria-expanded', 'true');
            } else {
                navButtons.classList.remove('mobile-active');
                this.setAttribute('aria-expanded', 'false');
                
                // Fechar todos os dropdowns quando fechar o menu mobile
                document.querySelectorAll('.dropdown-menu.show').forEach(menu => {
                    menu.classList.remove('show');
                });
                dropdownToggles.forEach(toggle => {
                    toggle.setAttribute('aria-expanded', 'false');
                    toggle.classList.remove('active');
                });
            }
        });
    }
});
