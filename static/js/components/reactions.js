/**
 * Sistema de Reações
 */
class ReactionsSystem {
    constructor() {
        this.initializeEvents();
    }

    initializeEvents() {
        // Event listeners para botões de reação
        document.addEventListener('click', (e) => {
            // Botão principal de reação
            if (e.target.closest('.reaction-btn')) {
                e.preventDefault();
                this.toggleReactionsDropdown(e.target.closest('.reaction-btn'));
            }
            
            // Opção de reação no dropdown
            if (e.target.closest('.reaction-option')) {
                e.preventDefault();
                this.handleReactionClick(e.target.closest('.reaction-option'));
            }
            
            // Fechar dropdown quando clicar fora
            if (!e.target.closest('.reactions-container')) {
                this.closeAllDropdowns();
            }
        });
    }

    toggleReactionsDropdown(button) {
        const container = button.closest('.reactions-container');
        const dropdown = container.querySelector('.reactions-dropdown');
        
        // Fechar todos os outros dropdowns
        this.closeAllDropdowns();
        
        // Toggle do dropdown atual
        dropdown.classList.toggle('show');
        button.classList.toggle('active');
    }

    closeAllDropdowns() {
        document.querySelectorAll('.reactions-dropdown').forEach(dropdown => {
            dropdown.classList.remove('show');
        });
        document.querySelectorAll('.reaction-btn').forEach(btn => {
            btn.classList.remove('active');
        });
    }

    async handleReactionClick(option) {
        const container = option.closest('.reactions-container');
        const reacaoId = option.dataset.reacaoId;
        const type = container.dataset.type;
        const targetId = container.dataset.targetId;
        
        // Feedback visual imediato
        option.classList.add('loading');
        
        try {
            let url;
            if (type === 'postagem') {
                // Pegar categoria e assunto do URL atual
                const pathParts = window.location.pathname.split('/');
                const categoriaSlug = pathParts[1];
                const assuntoSlug = pathParts[2];
                url = `/${categoriaSlug}/${assuntoSlug}/${targetId}/react/`;
            } else {
                url = `/reply/${targetId}/react/`;
            }
            
            const formData = new FormData();
            formData.append('reacao_id', reacaoId);
            formData.append('csrfmiddlewaretoken', this.getCsrfToken());
            
            const response = await fetch(url, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.updateReactionsUI(container, data);
                this.closeAllDropdowns();
                
                // Feedback de sucesso
                this.showFeedback(container, data.action);
            } else {
                this.showError(data.error || 'Erro ao reagir');
            }
            
        } catch (error) {
            console.error('Erro:', error);
            this.showError('Erro de conexão');
        } finally {
            option.classList.remove('loading');
        }
    }

    updateReactionsUI(container, data) {
    console.log('Atualizando UI com dados:', data);
    
    const summaryContainer = container.querySelector('.reactions-summary');
    const reactionBtn = container.querySelector('.reaction-btn');
    const countSpan = reactionBtn.querySelector('.reaction-count');
    
    // Limpar resumo atual
    summaryContainer.innerHTML = '';
    
    // Adicionar reações atualizadas
    let totalReactions = 0;
    data.reacoes.forEach(reacao => {
        if (reacao.count > 0) {
            totalReactions += reacao.count;
            const item = document.createElement('div');
            item.className = 'reaction-summary-item';
            item.innerHTML = `
                <img src="${reacao.reacao__icone}" alt="${reacao.reacao__nome}" class="reaction-icon-small">
                <span class="reaction-count-small">${reacao.count}</span>
            `;
            summaryContainer.appendChild(item);
            console.log('Adicionado item de reação:', reacao);
        }
    });
    
    // Atualizar botão principal
    if (data.user_reaction_id) {
        reactionBtn.classList.add('has-reaction');
        reactionBtn.dataset.userReaction = data.user_reaction_id;
        console.log('Usuário tem reação:', data.user_reaction_id);
    } else {
        reactionBtn.classList.remove('has-reaction');
        delete reactionBtn.dataset.userReaction;
        console.log('Usuário não tem reação');
    }
    
    // Atualizar contador
    if (totalReactions > 0) {
        countSpan.textContent = totalReactions;
        countSpan.style.display = 'inline';
        console.log('Total de reações:', totalReactions);
    } else {
        countSpan.style.display = 'none';
        console.log('Nenhuma reação');
    }
}

    showFeedback(container, action) {
        const feedback = document.createElement('div');
        feedback.className = 'reaction-feedback';
        
        let message = '';
        switch (action) {
            case 'added':
                message = 'Reação adicionada!';
                break;
            case 'changed':
                message = 'Reação alterada!';
                break;
            case 'removed':
                message = 'Reação removida!';
                break;
        }
        
        feedback.textContent = message;
        container.appendChild(feedback);
        
        // Remover feedback após animação
        setTimeout(() => {
            feedback.remove();
        }, 2000);
    }

    showError(message) {
        // Usar sistema de notificações se disponível
        if (window.Notifications) {
            Notifications.show(message, 'error');
        } else {
            alert(message);
        }
    }

    getCsrfToken() {
        const cookie = document.cookie
            .split('; ')
            .find(row => row.startsWith('csrftoken='));
        return cookie ? cookie.split('=')[1] : '';
    }
}

// Inicializar quando DOM estiver pronto
document.addEventListener('DOMContentLoaded', function() {
    window.Reactions = new ReactionsSystem();
});