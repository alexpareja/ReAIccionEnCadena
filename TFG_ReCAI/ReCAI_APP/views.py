from django.shortcuts import render, redirect
from .forms import RegistroFormulario, CambiarContraseñaFormulario
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
import openai
from django.contrib.auth import update_session_auth_hash
from .forms import OpcionForm
from django import template
#from ReCAI_APP import settings


def index(request):
    form = OpcionForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            opcion_elegida = form.cleaned_data['opcion_elegida']
            return render(request, 'pregame.html', {'opcion_elegida': opcion_elegida})
    return render(request, 'index.html', {'form': form})

# Create your views here.
def registro(request):
    if request.method == 'POST':
        form = RegistroFormulario(request.POST)
        if form.is_valid():
            form.save()
            return redirect('index')  # Redirige a la página de inicio o a donde prefieras
    else:
        form = RegistroFormulario()

    return render(request, 'registro.html', {'form': form})

def game(request):
    return render(request, 'game.html')

def pregame(request):
    j1 = "Jugador 1"
    j2 = "Jugador 2"
    if request.method == 'POST':
        form = OpcionForm(request.POST)
        if form.is_valid():
            opcion_elegida = form.cleaned_data['opcion_elegida']
            # Lógica para determinar el valor de j1
            if opcion_elegida == 'jugador_vs_ia':
                j1 = "Jugador"
                j2 = "IA"
            elif opcion_elegida == 'ia_vs_ia':
                j1 = "IA 1"
                j2 = "IA 2"
            return render(request, 'pregame.html', {'opcion_elegida': opcion_elegida, 'j1': j1, 'j2' :j2})
    else:
        form = OpcionForm()
    return render(request, 'index.html', {'form': form})

def perfil_usuario(request):
    return render(request, 'perfil_usuario.html')

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
    openai.api_key = settings.OPENAI_API_KEY
    model = "text-davinci-003"  # Puedes cambiar el modelo según tus preferencias

    response = openai.Completion.create(
        engine=model,
        prompt=message,
        max_tokens=150
    )

    return response.choices[0].text.strip()