from django.shortcuts import render, redirect
from .forms import RegistroFormulario, LoginFormulario, CambiarContraseñaFormulario, FormNombresJugadores, TurnFormulario
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
import openai
import random
from django.contrib.auth import update_session_auth_hash, login
from django.contrib.auth.models import User
from .forms import OpcionForm
from .models import PalabrasEncadenadas, EslabonCentral, RondaFinal
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

def centro_de_la_cadena(request):
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
    return render(request, 'centro_de_la_cadena.html', {'j1': j1, 'j2' : j2, 'jugador1': jugador1, 
                                                         'jugador2' :jugador2, 'puntos_jugador1' :puntos_jugador1, 
                                                         'puntos_jugador2': puntos_jugador2, 'turno_actual': turno_actual, 
                                                         'palabras': palabras})

def una_lleva_a_la_otra(request):
    # Datos de los jugadores
    j1 = request.session.get('j1', 'Tipo de j1 no ingresado')
    jugador1 = request.session.get('jugador1', 'Nombre del jugador 1 no ingresado')
    j2 = request.session.get('j2', 'Tipo de j2 no ingresado')
    jugador2 = request.session.get('jugador2', 'Nombre del jugador 2 no ingresado')

    # Obteniendo las palabras de la ronda
    palabras = EslabonCentral.objects.first()
    letras_mostradas = request.session.get('letras_mostradasRonda3', 1)

    # Estado actual del juego
    turno_actual = request.session.get('turno_actual', j1)
    n_palabra_adivinado = request.session.get('n_palabra_adivinadoRonda3', 2)
    primera_letra = request.session.get('primera_letraRonda3', getattr(palabras, 'p' + str(n_palabra_adivinado), '')[0])
    puntos_jugador1 = request.session.get('puntos_jugador1', 0)
    puntos_jugador2 = request.session.get('puntos_jugador2', 0)

    palabras_modificadas = []

    for i in range(1, 7): 
        nombre_campo = 'p' + str(i)
        palabra = getattr(palabras, nombre_campo, '')
        palabra_modificada = ''
        if i != 1 and i != 7:
            if i == n_palabra_adivinado:
                palabra_modificada = primera_letra
            elif i > n_palabra_adivinado:
                palabra_modificada = '' 
            else:
                palabra_modificada = palabra
            palabras_modificadas.insert(i,palabra_modificada)

    if request.method == 'POST':
        respuesta = request.POST.get('respuesta', '').upper()
        nombre_campo = 'p' + str(n_palabra_adivinado)
        palabra_a_adivinar = getattr(palabras, nombre_campo, '').upper()

        if respuesta == palabra_a_adivinar:
        # Asignar puntos al jugador correcto
            if turno_actual == j1:
                puntos_jugador1 += 10000
            else:
                puntos_jugador2 += 10000

            palabras_modificadas[int(n_palabra_adivinado)-2] = palabra_a_adivinar
            n_palabra_adivinado += 1
            if n_palabra_adivinado > 6:
                return redirect('ultima_cadena')
            palabras_modificadas[int(n_palabra_adivinado)-2] = getattr(palabras, 'p' + str(n_palabra_adivinado), '')[0]
            primera_letra = getattr(palabras, 'p' + str(n_palabra_adivinado), None)[0]
            letras_mostradas = 1  
        else:
            turno_actual = j2 if turno_actual == j1 else j1
            letras_mostradas += 1
            if len(palabra_a_adivinar) <= letras_mostradas:
                # Lógica cuando se han revelado todas las letras
                if turno_actual == j1:
                    puntos_jugador1 += 10000
                else:
                    puntos_jugador2 += 10000

                palabras_modificadas[int(n_palabra_adivinado)-2] = palabra_a_adivinar
                n_palabra_adivinado += 1
                if n_palabra_adivinado > 6:
                    return redirect('ultima_cadena')
                palabras_modificadas[int(n_palabra_adivinado)-2] = getattr(palabras, 'p' + str(n_palabra_adivinado), '')[0]
                primera_letra = getattr(palabras, 'p' + str(n_palabra_adivinado), None)[0]
                letras_mostradas = 1 
            else:
                # Actualizar primera_letra para mostrar las letras acumuladas hasta ahora
                primera_letra += getattr(palabras, 'p' + str(n_palabra_adivinado), None)[letras_mostradas-1] 
                palabras_modificadas[int(n_palabra_adivinado)-2] = primera_letra
                    
        request.session['turno_actual'] = turno_actual
        request.session['n_palabra_adivinadoRonda3'] = n_palabra_adivinado
        request.session['letras_mostradasRonda3'] = letras_mostradas
        request.session['primera_letraRonda3'] = primera_letra
        request.session['puntos_jugador1'] = puntos_jugador1
        request.session['puntos_jugador2'] = puntos_jugador2

    # Renderizar la plantilla con el contexto actualizado
    return render(request, 'una_lleva_a_la_otra.html', {
        'j1': j1, 'jugador1': jugador1, 'puntos_jugador1': puntos_jugador1,
        'j2': j2, 'jugador2': jugador2, 'puntos_jugador2': puntos_jugador2,
        'palabras_modificadas': palabras_modificadas, 'palabras': palabras,
        'n_palabra_adivinado': n_palabra_adivinado, 'turno_actual': turno_actual,
        'letras_mostradas': letras_mostradas,
        'primera_letra': primera_letra,
        'idPalabra': "p" + str(n_palabra_adivinado)
    })


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

def my_login(request):
    if request.method == 'POST':
        form = LoginFormulario(request.POST)
        if form.is_valid():
                login(request, form)
                return redirect('index')  # Redirige a la página de inicio o a donde prefieras
    else:
        form = LoginFormulario()

    return render(request, 'login.html', {'form': form})

def ultima_cadena(request):
    finRonda = False
  
    j1 = request.session.get('j1', 'Tipo de j1 no ingresado')
    jugador1 = request.session.get('jugador1', 'Nombre del jugador 1 no ingresado')

    palabras = RondaFinal.objects.first()
    letras_mostradas = request.session.get('letras_mostradas', 1)

    n_palabra_adivinado = request.session.get('n_palabra_adivinado', 2)
    primera_letra = request.session.get('primera_letra', getattr(palabras, 'p' + str(n_palabra_adivinado), None)[0])
    puntos_jugador1 = request.session.get('puntos_jugador1', 80000)
    comodines = request.session.get('comodines', 2)

    palabras_modificadas = []

    for i in range(1, 13):  # Assuming there are 15 fields in RondaFinal
        nombre_campo = 'p' + str(i)
        palabra = getattr(palabras, nombre_campo, '')
        palabra_modificada = ''
        if i % 2 == 0:
            if i == n_palabra_adivinado:
                palabra_modificada = primera_letra
            elif i > n_palabra_adivinado:
                palabra_modificada = '' 
            else:
                palabra_modificada = palabra
            palabras_modificadas.insert(i,palabra_modificada)

    request.session['palabrasModificadas'] = palabras_modificadas

    if request.method == 'POST':
        form = TurnFormulario(request.POST)
        if form.is_valid():
            respuesta = form.cleaned_data['respuesta']
            nombre_campo = 'p' + str(n_palabra_adivinado)
            palabra_a_adivinar = getattr(palabras, nombre_campo, None)

            if respuesta.upper() == palabra_a_adivinar:
                print("Acertaste!! La solución era " + palabra_a_adivinar)
                if (n_palabra_adivinado == 12):
                    redirect('index')
                palabras_modificadas[int(n_palabra_adivinado/2)-1] = palabra_a_adivinar
                n_palabra_adivinado += 2
                palabras_modificadas[int(n_palabra_adivinado/2)-1] = getattr(palabras, 'p' + str(n_palabra_adivinado), '')[0]
                request.session['palabrasModificadas'] = palabras_modificadas
                primera_letra = getattr(palabras, 'p' + str(n_palabra_adivinado), None)[0]
                request.session['primera_letra'] = primera_letra
                request.session["n_palabra_adivinado"] = n_palabra_adivinado
                letras_mostradas = 1
                request.session['letras_mostradas'] = letras_mostradas

            else:
                letras_mostradas += 1
                request.session['letras_mostradas'] = letras_mostradas

                if letras_mostradas > 3:
                    palabras_modificadas[int(n_palabra_adivinado/2)-1] = palabra_a_adivinar
                    request.session['palabrasModificadas'] = palabras_modificadas
                    if (n_palabra_adivinado > 12):
                        redirect('index')
                    n_palabra_adivinado += 2
                    palabras_modificadas[int(n_palabra_adivinado/2)-1] = getattr(palabras, 'p' + str(n_palabra_adivinado), '')[0]
                    request.session['palabrasModificadas'] = palabras_modificadas
                    primera_letra = getattr(palabras, 'p' + str(n_palabra_adivinado), None)[0]
                    request.session['primera_letra'] = primera_letra
                    request.session["n_palabra_adivinado"] = n_palabra_adivinado
                    letras_mostradas = 1
                    request.session['letras_mostradas'] = letras_mostradas
                else:
                    primera_letra += getattr(palabras, 'p' + str(n_palabra_adivinado), None)[letras_mostradas-1] 
                    request.session['primera_letra'] = primera_letra
                    palabras_modificadas[int(n_palabra_adivinado/2)-1] = primera_letra
                    request.session['palabrasModificadas'] = palabras_modificadas



                if (comodines > 0):
                    comodines -= 1
                    request.session['comodines'] = comodines
                else:
                    puntos_jugador1 =  puntos_jugador1/2
                    request.session['puntos_jugador1'] = puntos_jugador1

    idPalabra = "p" + str(n_palabra_adivinado)
    
    if(finRonda == True):
        return redirect('index')
    return render(request, 'ultima_cadena.html', {'j1': j1, 'jugador1': jugador1, 
                                                'puntos_jugador1' :puntos_jugador1, 'palabras_modificadas': palabras_modificadas,
                                                'palabras': palabras,
                                                'n_palabra_adivinado': n_palabra_adivinado,
                                                'primera_letra': primera_letra,
                                                'comodines': comodines,
                                                'idPalabra': idPalabra
                                                })


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