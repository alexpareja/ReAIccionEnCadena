from django.shortcuts import render, redirect
from .forms import RegistroFormulario, LoginFormulario, CambiarContraseñaFormulario, FormNombresJugadores
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
import openai
import random
from django.contrib.auth import update_session_auth_hash, login
from django.contrib.auth.models import User
from .forms import OpcionForm
from .models import PalabrasEncadenadas, EslabonCentral
from django import template
#from ReCAI_APP import settings

def index(request):
    form = OpcionForm(request.POST or None)
    if request.method == 'POST':
        print(form.errors)
        if form.is_valid():
            opcion_elegida = form.cleaned_data['opcion_elegida']
            j1 = "Jugador 1"
            j2 = "Jugador 2"
            if opcion_elegida == 'jugador_vs_ia':
                j1 = "Jugador"
                j2 = "IA"
            elif opcion_elegida == 'ia_vs_ia':
                j1 = "IA 1"
                j2 = "IA 2"
            request.session['j1'] = j1
            request.session['j2'] = j2
            return redirect(pregame)
    return render(request, 'index.html', {'form': form})

def pregame(request):
    j1 = request.session.get('j1', 'Tipo de j1 no ingresado')
    j2 = request.session.get('j2', 'Tipo de j2 no ingresado')
    form = FormNombresJugadores(initial={'jugador1': request.user.get_username()})

    if request.method == 'POST':
        form = FormNombresJugadores(request.POST)
        if form.is_valid():
            jugador1 = form.cleaned_data['jugador1']
            jugador2 = form.cleaned_data['jugador2']
            request.session['jugador1'] = jugador1
            request.session['jugador2'] = jugador2
        return redirect(palabras_encadenadas)
    return render(request, 'pregame.html', {'form': form, 'j1':j1, 'j2':j2})

def palabras_encadenadas(request):
    j1 = request.session.get('j1', 'Tipo de j1 no ingresado')
    j2 = request.session.get('j2', 'Tipo de j2 no ingresado')
    jugador1 = request.session.get('jugador1', 'Nombre del jugador 1 no ingresado')
    jugador2 = request.session.get('jugador2', 'Nombre del jugador 2 no ingresado') 
    

    palabras = list(PalabrasEncadenadas.objects.all().order_by('?')[:1])  



    puntos_jugador1 = 0
    puntos_jugador2 = 0

    if request.session.get('turno_actual') == j1:
        turno_actual = j2
        request.session['turno_actual'] = turno_actual
    elif request.session.get('turno_actual') == j2:
        turno_actual = j1
        request.session['turno_actual'] = turno_actual
    else:
        turno_actual = random.choice([j1,j2])
        request.session['turno_actual'] = turno_actual
    

    return render(request, 'palabras_encadenadas.html', {'j1': j1, 'j2' : j2, 'jugador1': jugador1, 
                                                         'jugador2' :jugador2, 'puntos_jugador1' :puntos_jugador1, 
                                                         'puntos_jugador2': puntos_jugador2, 'turno_actual': turno_actual, 
                                                         'palabras': palabras})

def eslabon_central(request):
    j1 = request.session.get('j1', 'Tipo de j1 no ingresado')
    j2 = request.session.get('j2', 'Tipo de j2 no ingresado')
    jugador1 = request.session.get('jugador1', 'Nombre del jugador 1 no ingresado')
    jugador2 = request.session.get('jugador2', 'Nombre del jugador 2 no ingresado') 
    
    palabras = list(EslabonCentral.objects.all().order_by('?')[:1])  

    puntos_jugador1 = 0
    puntos_jugador2 = 0

    if request.session.get('turno_actual') == j1:
        turno_actual = j2
        request.session['turno_actual'] = turno_actual
    elif request.session.get('turno_actual') == j2:
        turno_actual = j1
        request.session['turno_actual'] = turno_actual
    else:
        turno_actual = random.choice([j1,j2])
        request.session['turno_actual'] = turno_actual
    return render(request, 'eslabon_central.html', {'j1': j1, 'j2' : j2, 'jugador1': jugador1, 
                                                         'jugador2' :jugador2, 'puntos_jugador1' :puntos_jugador1, 
                                                         'puntos_jugador2': puntos_jugador2, 'turno_actual': turno_actual, 
                                                         'palabras': palabras})


def perfil_usuario(request):
    return render(request, 'perfil_usuario.html')

def registro(request):
    if request.method == 'POST':
        form = RegistroFormulario(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']

            if User.objects.filter(username=username).exists():
                form.add_error('username', 'Este nombre de usuario ya está en uso.')
            elif User.objects.filter(email=email).exists():
                form.add_error('email', 'Este correo electrónico ya está registrado.')
            else:
                user = form.save(commit=False)
                user.save()
                login(request, user)
                return redirect('index')  # Redirige a la página de inicio o a donde prefieras
    else:
        form = RegistroFormulario()

    return render(request, 'registro.html', {'form': form})

def login(request):
    if request.method == 'POST':
        form = LoginFormulario(request.POST)
        if form.is_valid():
                login(request, form)
                return redirect('index')  # Redirige a la página de inicio o a donde prefieras
    else:
        form = LoginFormulario()

    return render(request, 'login.html', {'form': form})

@login_required
def cambiar_contraseña(request):
    if request.method == 'POST':
        form = CambiarContraseñaFormulario(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            return render(request, 'perfil_usuario.html')
    else:
        form = CambiarContraseñaFormulario(request.user)
    return render(request, 'cambiar_contraseña.html', {'form': form})




#@csrf_exempt
#def chatgpt_api(request):
    if request.method == 'POST':
        message = request.POST.get('message', '')
        response = chatgpt_request(message)
        return JsonResponse({'response': response})
    else:
        return JsonResponse({'error': 'Only POST requests are allowed.'})
    
#def chatgpt_request(message):
    openai.api_key = settings.OPENAI_API_KEYs
    model = "text-davinci-003"  # Puedes cambiar el modelo según tus preferencias

    response = openai.Completion.create(
        engine=model,
        prompt=message,
        max_tokens=150
    )

    return response.choices[0].text.strip()