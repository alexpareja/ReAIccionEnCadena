from django.urls import path
from . import views
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('', views.index, name='index'),
    path('registro/', views.registro, name='registro'),
    path('login/', views.login, name='my_login'),
    path('palabras_encadenadas/', views.palabras_encadenadas, name='palabras_encadenadas'),
    path('pregame/', views.pregame, name='pregame'),
    path('perfil_usuario/', views.perfil_usuario, name='usuario'),
    path('cambiar_contraseña/', views.cambiar_contraseña, name='cambiar_contraseña'),
    path('logout/', auth_views.LogoutView.as_view(template_name= 'logout.html'), name='my_logout'),

    # Agrega más URLs según sea necesario
]
