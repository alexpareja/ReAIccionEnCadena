from django.urls import path
from . import views

urlpatterns = [
    path('prueba/', views.prueba, name='prueba'),
    # Agrega más URLs según sea necesario
]
