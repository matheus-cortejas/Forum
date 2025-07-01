from django.utils import timezone
from django.utils.deprecation import MiddlewareMixin
from .models import UsuarioOnline
import re


class OnlineUsersMiddleware(MiddlewareMixin):
    """Middleware para rastrear usuários online"""
    
    # Lista de bots conhecidos
    BOT_USER_AGENTS = [
        'googlebot', 'bingbot', 'slurp', 'duckduckbot', 'baiduspider',
        'yandexbot', 'facebookexternalhit', 'twitterbot', 'linkedinbot',
        'whatsapp', 'telegrambot', 'applebot', 'discordbot', 'crawler',
        'spider', 'bot', 'scraper'
    ]
    
    def process_request(self, request):
        """Processa cada requisição para rastrear atividade"""
        # Obter informações da requisição
        session_key = request.session.session_key
        if not session_key:
            request.session.save()
            session_key = request.session.session_key
        
        ip_address = self.get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        pagina_atual = request.get_full_path()
        
        # Detectar bots
        is_bot, bot_name = self.detect_bot(user_agent)
        
        # Obter ou criar registro de usuário online
        online_user, created = UsuarioOnline.objects.get_or_create(
            session_key=session_key,
            defaults={
                'ip_address': ip_address,
                'user_agent': user_agent,
                'is_bot': is_bot,
                'bot_name': bot_name,
                'pagina_atual': pagina_atual,
            }
        )
        
        # Atualizar informações
        online_user.ip_address = ip_address
        online_user.user_agent = user_agent
        online_user.pagina_atual = pagina_atual
        online_user.is_authenticated = request.user.is_authenticated
        online_user.is_bot = is_bot
        online_user.bot_name = bot_name
        
        if request.user.is_authenticated:
            online_user.usuario = request.user
        else:
            online_user.usuario = None
        
        online_user.save()
        
        # Cleanup periódico (apenas 1% das requisições para performance)
        import random
        if random.randint(1, 100) == 1:
            UsuarioOnline.cleanup_old_sessions()
    
    def get_client_ip(self, request):
        """Obter IP real do cliente considerando proxies"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def detect_bot(self, user_agent):
        """Detectar se é um bot baseado no user agent"""
        if not user_agent:
            return False, ''
        
        user_agent_lower = user_agent.lower()
        
        for bot_name in self.BOT_USER_AGENTS:
            if bot_name in user_agent_lower:
                # Extrair nome específico do bot
                if 'googlebot' in user_agent_lower:
                    return True, 'Googlebot'
                elif 'bingbot' in user_agent_lower:
                    return True, 'Bingbot'
                elif 'duckduckbot' in user_agent_lower:
                    return True, 'DuckDuckBot'
                elif 'facebookexternalhit' in user_agent_lower:
                    return True, 'Facebook'
                elif 'twitterbot' in user_agent_lower:
                    return True, 'Twitter'
                elif 'linkedinbot' in user_agent_lower:
                    return True, 'LinkedIn'
                elif 'telegrambot' in user_agent_lower:
                    return True, 'Telegram'
                elif 'discordbot' in user_agent_lower:
                    return True, 'Discord'
                else:
                    return True, bot_name.title()
        
        return False, ''
