from django import forms
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm, AuthenticationForm
from django.contrib.auth.models import User



class LoginFormulario(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'registro-input'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'registro-input'}))

    class Meta:
        model = User
        fields = ['username', 'password']

class RegistroFormulario(UserCreationForm):
    username = forms.CharField(max_length=30, required=True)
    email = forms.EmailField(required=True)


    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super(RegistroFormulario, self).__init__(*args, **kwargs)
        # Agregar clases de estilo a los campos y etiquetas
        self.fields['username'].widget.attrs['class'] = 'registro-input'
        self.fields['email'].widget.attrs['class'] = 'registro-input'
        self.fields['password1'].widget.attrs['class'] = 'registro-input'
        self.fields['password2'].widget.attrs['class'] = 'registro-input'

        self.fields['username'].label_class = 'registro-label'
        self.fields['email'].label_class = 'registro-label'
        self.fields['password1'].label_class = 'registro-label'
        self.fields['password2'].label_class = 'registro-label'

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

class FormNombresJugadores(forms.Form):
    jugador1 = forms.CharField(max_length=20)
    jugador2 = forms.CharField(max_length=20)