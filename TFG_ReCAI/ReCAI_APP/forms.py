from django import forms
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django.contrib.auth.models import User

class RegistroFormulario(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

class CambiarContraseñaFormulario(PasswordChangeForm):
    class Meta:
        model = User

class OpcionForm(forms.Form):
    opciones = [
        ('2_jugadores', '2 Jugadores'),
        ('jugador_vs_ia', 'Jugador vs IA'),
        ('ia_vs_ia', 'IA vs IA'),
    ]
    opcion_elegida = forms.ChoiceField(choices=opciones, widget=forms.RadioSelect)