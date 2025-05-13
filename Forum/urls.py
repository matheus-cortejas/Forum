"""
URL configuration for Forum project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),

    # primary nav
    path('', views.home, name='home'),
    path('topicos/', views.topicos, name='topicos'),
    path('posts/', views.posts, name='posts'),
    path('members/', views.members, name='members'),
    path('online/', views.online, name='online'),
    path('detail/', views.detail, name='detail'),
    path('search/', views.search, name='search'),
    path('novos_topicos/', views.novos_topicos, name='novos_topicos'),
    path('novos_posts/', views.novos_posts, name='novos_posts'),
    path('novidades/', views.novidades, name='novidades'),

    # auth
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('register/', views.register, name='register'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
