from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('registro/', views.registro, name='registro'),
    path('game/', views.game, name='game'),
    path('perfil_usuario/', views.perfil_usuario, name='usuario'),
    # Agrega más URLs según sea necesario
]
