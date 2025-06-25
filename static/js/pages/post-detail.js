/**
 * Script específico para página de detalhes do post
 */
document.addEventListener('DOMContentLoaded', function() {
    // Importar componentes necessários
    loadScript('/static/js/components/reply-system.js');
    loadScript('/static/js/components/reactions.js');
    loadScript('/static/js/components/notifications.js');
    
    // Funções globais para compatibilidade com templates
    window.editReply = (id) => Reply.edit(id);
    window.deleteReply = (id) => Reply.delete(id);
    
    // Auto-scroll para resposta específica se houver hash
    if (window.location.hash.startsWith('#reply-')) {
        const replyId = window.location.hash.substring(7);
        const element = document.getElementById(`reply-${replyId}`);
        if (element) {
            element.scrollIntoView({ behavior: 'smooth' });
            element.classList.add('highlight-reply');
        }
    }
});

function loadScript(src) {
    const script = document.createElement('script');
    script.src = src;
    document.head.appendChild(script);
}