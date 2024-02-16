from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('registro/', views.registro, name='registro'),
    path('game/', views.game, name='game'),
    path('perfil_usuario/', views.perfil_usuario, name='usuario'),
    path('cambiar_contraseña/', views.cambiar_contraseña, name='cambiar_contraseña'),
    # Agrega más URLs según sea necesario
]
