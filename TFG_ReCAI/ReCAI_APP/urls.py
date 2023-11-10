from django.urls import path
from . import views
from .views import registro

urlpatterns = [
    path('registro/', registro, name='registro'),
    # Agrega más URLs según sea necesario
]
