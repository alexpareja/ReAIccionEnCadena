from django.urls import path
from . import views
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('', views.index, name='index'),
    path('registro/', views.registro, name='registro'),
    path('accounts/login/', auth_views.LoginView.as_view(template_name= 'login.html'), name='my_login'),
    path('instrucciones/palabras_encadenadas/', views.instrucciones_palabras_encadenadas, name='instrucciones_palabras_encadenadas'),
    path('instrucciones/centro_de_la_cadena/', views.instrucciones_centro_de_la_cadena, name='instrucciones_centro_de_la_cadena'),
    path('instrucciones/una_lleva_a_la_otra/', views.instrucciones_una_lleva_a_la_otra, name='instrucciones_una_lleva_a_la_otra'),
    path('instrucciones/ultima_cadena/', views.instrucciones_ultima_cadena, name='instrucciones_ultima_cadena'),
    path('instrucciones/ultima_palabra/', views.instrucciones_ultima_palabra, name='instrucciones_ultima_palabra'),
    path('palabras_encadenadas/', views.palabras_encadenadas, name='palabras_encadenadas'),
    path('centro_de_la_cadena/', views.centro_de_la_cadena, name='centro_de_la_cadena'),
    path('una_lleva_a_la_otra/', views.una_lleva_a_la_otra, name='una_lleva_a_la_otra'),
    path('ultima_cadena/', views.ultima_cadena, name='ultima_cadena'),
    path('ultima_palabra/', views.ultima_palabra, name='ultima_palabra'),
    path('fin_juego/', views.fin_juego, name='fin_juego'),
    path('puntuaciones/', views.puntuaciones, name='puntuaciones'),
    path('pregame/', views.pregame, name='pregame'),
    path('marcador_ronda', views.marcador_ronda, name='marcador_ronda'),
    path('logout/', auth_views.LogoutView.as_view(template_name= 'logout.html'), name='my_logout'),

]
