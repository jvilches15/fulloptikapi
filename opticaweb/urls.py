from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ConsejoViewSet
from .views import consejos_view
from .views import recetas_saludables_view
from .viewsLogin import login_api
from .views import clima_view


router = DefaultRouter()
router.register(r'consejos', ConsejoViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
    path('consejos/', consejos_view, name='consejos'),
    path('alimentate-bien/', recetas_saludables_view, name='alimentate_bien'),
    path('login-api/', login_api, name= "login_api"),
    path('clima/', clima_view, name='clima'),
   
]