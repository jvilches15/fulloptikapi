"""
URL configuration for FullOptikWeb project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
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
from opticaweb import views
from django.conf import settings
from django.conf.urls.static import static



urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.login_view, name='login'),
    path('adulto/', views.adulto, name='adulto'),
    path('infantil/', views.infantil, name='infantil'),
    path('sobrelentes/', views.sobrelentes, name='sobrelentes'),
    path('sol/', views.sol, name='sol'),
    path('nosotros/', views.nosotros, name='nosotros'),
    path('registro/', views.registro, name='registro'),
    path('perfil/', views.perfil, name='perfil'),
    path('editar-perfil/', views.editar_perfil, name='editar_perfil'),
    path('logout/', views.cerrar_sesion, name='logout'),
    path('reset-password/', views.reset_password_page, name='reset_password'), 
    path('ajax/cargar-comunas/', views.cargar_comunas, name='cargar_comunas'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)