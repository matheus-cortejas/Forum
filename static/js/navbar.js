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
});
