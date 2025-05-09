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
from django.urls import path, include
from opticaweb import views
from django.conf import settings
from django.conf.urls.static import static






urlpatterns = [
    path('admin/', admin.site.urls), 
    path('', include('opticaweb.urls')),
    path('api/', include('opticaweb.urls')),
    path('consejos/', views.consejos_view, name='consejos'), 
    path('consejos/', views.consejos_list, name='consejos_list'),
    path('consejos/<int:id>/', views.consejo_detail, name='consejo_detail'),
    path('alimentate-bien/', views.recetas_saludables_view, name='alimentate_bien'),
    path('promociones/', views.ver_promociones, name='ver_promociones'),
    path('admin-login/', views.admin_login, name='login_admin'),
    path('', views.index, name='index'),
    path('login/', views.login_view, name='login'),
    path('panel-admin/', views.panel_administrador, name='panel_administrador'),
    path('panel-colaborador/', views.panel_colaborador, name='panel_colaborador'),
    path('crear-usuario/', views.crear_usuario, name='crear_usuario'),
    path('lista-usuarios/', views.lista_usuarios, name='lista_usuarios'),
    path('lista-usuarioss/', views.lista_usuarioss, name='lista_usuarioss'),
    path('ingresar-producto/', views.ingresar_producto, name='ingresar_producto'),
    path('usuarios/eliminar/<int:usuario_id>/', views.eliminar_usuario, name='eliminar_usuario'),
    path('productos/eliminar/<int:producto_id>/', views.eliminar_producto, name='eliminar_producto'),
    path('productos/', views.lista_productos, name='lista_productos'),
    path('productoss/', views.lista_productoss, name='lista_productoss'),
    path('reporte/usuarios/excel/', views.reporte_usuarios_excel, name='reporte_usuarios_excel'),
    path('reporte/usuarios/pdf/', views.reporte_usuarios_pdf, name='reporte_usuarios_pdf'),
    path('reporte/productos/excel/', views.reporte_productos_excel, name='reporte_productos_excel'),
    path('reporte/productos/pdf/', views.reporte_productos_pdf, name='reporte_productos_pdf'),
    path('ventas/', views.lista_ventas, name='lista_ventas'),
    path('adulto/', views.adulto, name='adulto'),
    path('infantil/', views.infantil, name='infantil'),
    path('sobrelentes/', views.sobrelentes, name='sobrelentes'),
    path('sol/', views.sol, name='sol'),
    path('nosotros/', views.nosotros, name='nosotros'),
    path('registro/', views.registro, name='registro'),
    path('perfil/', views.perfil, name='perfil'),
    path('editar-perfil/', views.editar_perfil, name='editar_perfil'),
    path('cita/<int:cita_id>/gestionar/', views.gestionar_cita, name='gestionar_cita'),
    path('agendar-cita/', views.agendar_cita, name='agendar_cita'),
    path('editar-cita/<int:cita_id>/', views.editar_cita, name='editar_cita'),
    path('eliminar-cita/<int:cita_id>/', views.eliminar_cita, name='eliminar_cita'),
    path('logout/', views.cerrar_sesion, name='logout'),
    path('reset-password/', views.reset_password_page, name='reset_password'), 
    path('ajax/cargar-comunas/', views.cargar_comunas, name='cargar_comunas'),
    
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)