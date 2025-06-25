/**
 * Sistema de Respostas
 */
class ReplySystem {
    constructor() {
        this.initializeEvents();
        this.updateCharCount();
    }

    initializeEvents() {
        // Contador de caracteres
        const textarea = document.getElementById('reply-content');
        if (textarea) {
            textarea.addEventListener('input', () => this.updateCharCount());
        }

        // Submissão do formulário
        const form = document.getElementById('reply-form');
        if (form) {
            form.addEventListener('submit', (e) => this.handleSubmit(e));
        }
    }

    show() {
        const container = document.getElementById('reply-form-container');
        const textarea = document.getElementById('reply-content');
        
        if (container && textarea) {
            container.classList.remove('hide');
            textarea.focus();
        }
    }

    hide() {
        const container = document.getElementById('reply-form-container');
        const form = document.getElementById('reply-form');
        
        if (container && form) {
            container.classList.add('hide');
            form.reset();
            this.updateCharCount();
        }
    }

    updateCharCount() {
        const textarea = document.getElementById('reply-content');
        const counter = document.getElementById('char-count');
        
        if (textarea && counter) {
            const length = textarea.value.length;
            counter.textContent = length;
            
            // Mudar cor quando próximo do limite
            if (length > 9000) {
                counter.style.color = '#ff5252';
            } else if (length > 8000) {
                counter.style.color = '#ff9800';
            } else {
                counter.style.color = '#666';
            }
        }
    }

    async handleSubmit(event) {
        event.preventDefault();
        
        const form = event.target;
        const submitBtn = form.querySelector('button[type="submit"]');
        const formData = new FormData(form);
        
        // Validação
        const content = formData.get('conteudo').trim();
        if (content.length < 10) {
            Notifications.show('A resposta deve ter pelo menos 10 caracteres.', 'error');
            return;
        }
        
        // Loading state
        submitBtn.classList.add('loading');
        submitBtn.disabled = true;
        
        try {
            const response = await fetch(form.action, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });
            
            const data = await response.json();
            
            if (data.success) {
                // Adicionar nova resposta à lista
                this.addReplyToDOM(data.reply_html);
                this.updateRepliesCount();
                this.hide();
                Notifications.show(data.message, 'success');
            } else {
                Notifications.show(data.error || 'Erro ao adicionar resposta', 'error');
            }
        } catch (error) {
            console.error('Erro:', error);
            Notifications.show('Erro de conexão', 'error');
        } finally {
            submitBtn.classList.remove('loading');
            submitBtn.disabled = false;
        }
    }

    addReplyToDOM(html) {
        const container = document.getElementById('replies-container');
        const noReplies = document.querySelector('.no-replies');
        
        if (container) {
            container.insertAdjacentHTML('beforeend', html);
        }
        
        if (noReplies) {
            noReplies.remove();
        }
    }

    updateRepliesCount() {
        const container = document.getElementById('replies-container');
        const countElement = document.getElementById('replies-count');
        
        if (container && countElement) {
            const count = container.children.length;
            countElement.textContent = count;
        }
    }

    async edit(replyId) {
        // Implementar edição inline
        console.log('Editar resposta:', replyId);
    }

    async delete(replyId) {
        if (!confirm('Tem certeza que deseja deletar esta resposta?')) {
            return;
        }

        try {
            const response = await fetch(`/posts/reply/${replyId}/delete/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': Utils.getCsrfToken(),
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });

            const data = await response.json();

            if (data.success) {
                document.querySelector(`#reply-${replyId}`).remove();
                this.updateRepliesCount();
                Notifications.show(data.message, 'success');
            } else {
                Notifications.show(data.error, 'error');
            }
        } catch (error) {
            console.error('Erro:', error);
            Notifications.show('Erro ao deletar resposta', 'error');
        }
    }
}

// Exportar instância global
window.Reply = new ReplySystem();