from django.shortcuts import render, redirect
from .forms import RegistroFormulario, LoginFormulario, CambiarContraseñaFormulario, FormNombresJugadores, TurnFormulario
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.conf import settings
from .static import prompts
import openai
import json
from django.templatetags.static import static
import random
from django.contrib.auth import update_session_auth_hash, login
from django.contrib.auth.models import User
from .forms import OpcionForm
from .models import PalabrasEncadenadas, EslabonCentral, RondaFinal
from django import template
from django.urls import reverse

openai.api_key = settings.OPENAI_API_KEY


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
        return redirect(instrucciones_palabras_encadenadas)
    return render(request, 'pregame.html', {'form': form, 'j1':j1, 'j2':j2})

def instrucciones_palabras_encadenadas(request):
    imagen_url = static('img/palabras_encadenadas.png')
    texto_instrucciones = """
    En esta ronda, los jugadores deben adivinar 6 palabras, relacionadas todas ellas con un mismo tema, indicado al incio de la cadena.

    Todas las palabras comienzan con la letra final de la palabra anterior.

    Las palabras se adivinarán por turnos, en caso de acertar la palabra, el jugador obtendrá 2000 puntos y pasará a adivinar la siguiente palabra. En el caso contrario, el turno pasará al otro jugador y se mostrará una letra más de la palabra.

    Si ninguno de los jugadores logra adivinar la palabra, se mostrará la palabra completa y se pasará a la siguiente. 

    Comienza el jugador 2 a adivinar la primera palabra.

    """
    contexto = {
        'tituloDelJuego': 'Palabras encadenadas',
        'instrucciones': texto_instrucciones,
        'imagenDelJuego': imagen_url,
        'urlDelJuego': reverse('palabras_encadenadas'),
    }
    return render(request, 'base_instrucciones.html', contexto)

def instrucciones_centro_de_la_cadena(request):
    imagen_url = static('img/centro_de_la_cadena.png')
    texto_instrucciones = """
    En esta ronda, los jugadores deben adivinar 4 palabras.

    En el panel del juego, se mostrarán desde el inicio tres palabras: la primera, la última y la palabra intermedia de la cadena.

    Cada palabra a adivinar guarda relación con la palabra anterior y la palabra siguiente.

    En caso de acertar el jugador obtendrá 5000 puntos y pasará a adivinar la siguiente palabra. En el caso contrario, el turno pasará al otro jugador y se mostrará una letra más de la palabra.

    Comienza el jugador con menos puntos acumulados a adivinar la primera palabra.

    """
    contexto = {
        'tituloDelJuego': 'Centro de la cadena',
        'instrucciones': texto_instrucciones,
        'imagenDelJuego': imagen_url,
        'urlDelJuego': reverse('centro_de_la_cadena'),
    }
    return render(request, 'base_instrucciones.html', contexto)

def instrucciones_una_lleva_a_la_otra(request):
    imagen_url = static('img/una_lleva_a_la_otra.png')
    texto_instrucciones = """
    En esta ronda, los jugadores deben adivinar 5 palabras.

    En el panel del juego, se mostrarán desde el inicio dos palabras de la cadena: la primera, la última.

    Al igual que en la ronda anterior, cada palabra a adivinar guarda relación con la palabra anterior y la palabra siguiente.

    En caso de acertar el jugador obtendrá 10000 puntos y pasará a adivinar la siguiente palabra. En el caso contrario, el turno pasará al otro jugador y se mostrará una letra más de la palabra.

    Comienza el jugador con menos puntos acumulados a adivinar la primera palabra.

    """
    contexto = {
        'tituloDelJuego': 'Una lleva a la otra',
        'instrucciones': texto_instrucciones,
        'imagenDelJuego': imagen_url,
        'urlDelJuego': reverse('una_lleva_a_la_otra'),
    }
    return render(request, 'base_instrucciones.html', contexto)

def instrucciones_ultima_cadena(request):
    imagen_url = static('img/ultima_cadena.png')
    texto_instrucciones = """
    A partir de esta ronda, solo jugará el jugador con más puntos acumulados.

    El jugador deberá adivinar 6 palabras, las cuales tienen relación con las palabras que se encuentran arriba y abajo de ella.

    El jugador tendrá dos oportunidades para acertar la palabra. Sin embargo, cada fallo le costará la mitad de sus puntos.

    También contará con dos comodines, que le permitirán ver una letra más de la palabra.

    """
    contexto = {
        'tituloDelJuego': 'Última cadena',
        'instrucciones': texto_instrucciones,
        'imagenDelJuego': imagen_url,
        'urlDelJuego': reverse('ultima_cadena'),
    }
    return render(request, 'base_instrucciones.html', contexto)

def instrucciones_ultima_palabra(request):
    imagen_url = static('img/ultima_palabra.png')
    texto_instrucciones = """
    

    """
    contexto = {
        'tituloDelJuego': 'Última palabra',
        'instrucciones': texto_instrucciones,
        'imagenDelJuego': imagen_url,
        'urlDelJuego': reverse('ultima_palabra'),
    }
    return render(request, 'base_instrucciones.html', contexto)

def palabras_encadenadas(request):
    #palabras_cargadasR1 = request.session.get('palabras_cargadasR1', False)
    #prompt = prompts.PROMPT_RONDA1
    #if palabras_cargadasR1 == False:
    #    JsonPalabras = llamadaAPIChatGPT(prompt)
    #    data = json.loads(JsonPalabras)
    #    request.session['datajson'] = data
    #    palabras = PalabrasEncadenadas(
    #        tema=data["tema"],
    #        p1=data["p1"],
    #        p2=data["p2"],
    #        p3=data["p3"],
    #        p4=data["p4"],
    #        p5=data["p5"],
    #        p6=data["p6"])
    #    palabras.save()
    #    palabras_cargadasR1 = True
    #    request.session['palabras_cargadasR1'] = palabras_cargadasR1

    fin=0
    j1 = request.session.get('j1', 'Tipo de j1 no ingresado')
    j2 = request.session.get('j2', 'Tipo de j2 no ingresado')
    jugador1 = request.session.get('jugador1', 'Nombre del jugador 1 no ingresado')
    jugador2 = request.session.get('jugador2', 'Nombre del jugador 2 no ingresado') 

    # Obteniendo las palabras de la ronda
    palabras = PalabrasEncadenadas.objects.last()
    letras_mostradas = request.session.get('lm', 1)

    # Estado actual del juego

    turno_actual = request.session.get('turno_actual', j1)
    n_palabra_adivinado = request.session.get('npa', 1)
    primera_letra = request.session.get('pl', getattr(palabras, 'p' + str(n_palabra_adivinado), '')[0])
    puntos_jugador1 = request.session.get('puntos_jugador1', 0)
    puntos_jugador2 = request.session.get('puntos_jugador2', 0)
    IA_jugando = 0
    palabras_modificadas = []

    for i in range(1, 7): 
        nombre_campo = 'p' + str(i)
        palabra = getattr(palabras, nombre_campo, '')
        palabra_modificada = ''
        if i == n_palabra_adivinado:
            guiones = '_ ' * (len(palabra) - 1 - i + n_palabra_adivinado)
            palabra_modificada = primera_letra.upper() + guiones + f" ({len(palabra)})"
        elif i > n_palabra_adivinado:
            palabra_modificada = '' 
        else:
            palabra_modificada = palabra
        palabras_modificadas.insert((i-1),palabra_modificada)
        
    nombre_campo = 'p' + str(n_palabra_adivinado)
    palabra_a_adivinar = getattr(palabras, nombre_campo, '').upper()
    respuestaJugadorIA1 = ''
    respuestaJugadorIA2 = ''

    html = 'palabras_encadenadas.html'
    if (turno_actual == "IA") | (turno_actual == 'IA 1') | (turno_actual == 'IA 2'):
        if n_palabra_adivinado > 1:
            palabra1 = getattr(palabras, 'p' + str(n_palabra_adivinado-1), '')
        else:
            palabra1 = '-'
        tema = getattr(palabras, 'tema', '')
        prompt = prompts.PROMPT_RONDA1_IA_PLAYER.format(palabra1, tema, primera_letra)
        respuesta = llamadaAPIChatGPT(prompt).upper()
        if (turno_actual == "IA") | (turno_actual == 'IA 2'):
            respuestaJugadorIA2 = 'Mi respuesta es ' + respuesta
        else:
            respuestaJugadorIA1 = 'Mi respuesta es ' + respuesta
        (request, html, j1, j2, jugador1, jugador2,
        puntos_jugador1, puntos_jugador2, turno_actual, palabras, 
        palabras_modificadas, n_palabra_adivinado, letras_mostradas,
        primera_letra, fin, respuesta, palabra_a_adivinar) = jugarTurnoPrimeraRonda(
        request, html, j1, j2, jugador1, jugador2,
        puntos_jugador1, puntos_jugador2, turno_actual, palabras,
        palabras_modificadas, n_palabra_adivinado, letras_mostradas,
        primera_letra, fin, respuesta, palabra_a_adivinar)
    else:
        if request.method == 'POST':
            respuesta = request.POST.get('respuesta', '').upper()
            print(palabra_a_adivinar)
            (request, html, j1, j2, jugador1, jugador2,
            puntos_jugador1, puntos_jugador2, turno_actual, palabras, 
            palabras_modificadas, n_palabra_adivinado, letras_mostradas,
            primera_letra, fin, respuesta, palabra_a_adivinar) = jugarTurnoPrimeraRonda(
            request, html, j1, j2, jugador1, jugador2,
            puntos_jugador1, puntos_jugador2, turno_actual, palabras,
            palabras_modificadas, n_palabra_adivinado, letras_mostradas,
            primera_letra, fin, respuesta, palabra_a_adivinar
            )
            
    request.session['turno_actual'] = turno_actual
    request.session['npa'] = n_palabra_adivinado
    request.session['lm'] = letras_mostradas
    request.session['pl'] = primera_letra
    request.session['puntos_jugador1'] = puntos_jugador1
    request.session['puntos_jugador2'] = puntos_jugador2
    request.session['ronda'] = 'Ronda 1: Palabras encadenadas'

    if (turno_actual == "IA") | (turno_actual == 'IA 1') | (turno_actual == 'IA 2'):
        IA_jugando = 1

    return render(request, 'palabras_encadenadas.html', {
        'j1': j1, 'j2' : j2, 'jugador1': jugador1, 'jugador2' :jugador2,
        'puntos_jugador1' :puntos_jugador1, 'puntos_jugador2': puntos_jugador2,
        'turno_actual': turno_actual, 'palabras': palabras, 'palabras_modificadas': palabras_modificadas,
        'n_palabra_adivinado': n_palabra_adivinado, 'turno_actual': turno_actual,
        'letras_mostradas': letras_mostradas, 'primera_letra': primera_letra, 'fin' : fin,
        'idPalabra': "p" + str(n_palabra_adivinado), 'respuestaIA1': respuestaJugadorIA1,
        'IA_jugando': IA_jugando, 'respuestaIA2': respuestaJugadorIA2
    })

def marcador_ronda(request):

    j1 = request.session.get('j1', 'Tipo de j1 no ingresado')
    j2 = request.session.get('j2', 'Tipo de j2 no ingresado')
    jugador1 = request.session.get('jugador1', 'Nombre del jugador 1 no ingresado')
    jugador2 = request.session.get('jugador2', 'Nombre del jugador 2 no ingresado')
    puntos_jugador1 = request.session.get('puntos_jugador1', 0)
    puntos_jugador2 = request.session.get('puntos_jugador2', 0)
    ronda = request.session.get('ronda', 'Juego no empezado') 


    if ronda == 'Ronda 1: Palabras encadenadas':
        urlDelJuego = reverse('instrucciones_centro_de_la_cadena')
    elif ronda == "Ronda 2: Centro de la cadena":
        urlDelJuego = reverse('instrucciones_una_lleva_a_la_otra')
    elif ronda == 'Ronda 3: Una lleva a la otra':
        urlDelJuego = reverse('instrucciones_ultima_cadena')
    else:
        urlDelJuego = reverse('index')

    return render(request, 'marcador_ronda.html', {'j1': j1, 'j2' : j2, 'jugador1': jugador1, 'jugador2' :jugador2,
        'puntos_jugador1' :puntos_jugador1, 'puntos_jugador2': puntos_jugador2, 'ronda': ronda, 'urlDelJuego': urlDelJuego})

def centro_de_la_cadena(request):
    #palabras_cargadasR2 = request.session.get('palabras_cargadasR2', False)
    #prompt = prompts.PROMPT_RONDA2y3
    #if palabras_cargadasR2 == False:
    #    JsonPalabras = llamadaAPIChatGPT(prompt)
    #    data = json.loads(JsonPalabras)
    #    request.session['datajson'] = data
    #    palabras = PalabrasEncadenadas(
    #        p1=data["p1"],
    #        p2=data["p2"],
    #        p3=data["p3"],
    #        p4=data["p4"],
    #        p5=data["p5"],
    #        p6=data["p6"],
    #        p7=data["p7"])
    #    palabras.save()
    #    palabras_cargadasR2 = True
    #    request.session['palabras_cargadasR2'] = palabras_cargadasR2

    # Datos de los jugadores
    fin=0
    j1 = request.session.get('j1', 'Tipo de j1 no ingresado')
    jugador1 = request.session.get('jugador1', 'Nombre del jugador 1 no ingresado')
    j2 = request.session.get('j2', 'Tipo de j2 no ingresado')
    jugador2 = request.session.get('jugador2', 'Nombre del jugador 2 no ingresado')
    puntos_jugador1 = request.session.get('puntos_jugador1', 0)
    puntos_jugador2 = request.session.get('puntos_jugador2', 0)
    turno_actual = request.session.get('turno_actual', j1)
    n_palabra_adivinado = request.session.get('n_palabra_adivinadoRonda2', 0)

    # Obteniendo las palabras de la ronda
    palabras = EslabonCentral.objects.last()
    letras_mostradas = request.session.get('letras_mostradasRonda2', 1)
    nPalabrasRespondidas = request.session.get('nPalabrasRespondidasRonda2', 0)
    isSeleccionada = request.session.get('isSeleccionadaRonda2', 1)
    palabra_elegida = request.session.get('palabraElegida', '')
    primera_letra = ''
    palabras_modificadasInit = []
    for i in range(1, 7): 
        nombre_campo = 'p' + str(i)
        palabra = getattr(palabras, nombre_campo, '')
        palabra_modificada = ''
        if i != 1 and i != 7 and i != 4:
            if i == n_palabra_adivinado:
                palabra_modificada = primera_letra
            palabras_modificadasInit.insert(i,palabra_modificada)

    palabras_modificadas = request.session.get('palabrasModificadasR2', palabras_modificadasInit)

    if isSeleccionada == 0:
        primera_letra = request.session.get('primera_letraRonda2', getattr(palabras, 'p' + str(n_palabra_adivinado), '')[0])

        if request.method == 'POST':
                respuesta = request.POST.get('respuesta', '').upper()
                nombre_campo = 'p' + str(n_palabra_adivinado)
                palabra_a_adivinar = getattr(palabras, nombre_campo, '').upper()

                (request, respuesta, palabra_a_adivinar, j1, j2, jugador1, jugador2,
                turno_actual, puntos_jugador1, puntos_jugador2, palabras,
                n_palabra_adivinado, palabras_modificadas, fin, letras_mostradas, primera_letra,
                 isSeleccionada, nPalabrasRespondidas) = jugarTurnoSegundaRonda(request, 
                respuesta, palabra_a_adivinar, j1, j2, jugador1, jugador2,
                turno_actual, puntos_jugador1, puntos_jugador2, palabras,
                n_palabra_adivinado, palabras_modificadas, fin, letras_mostradas, primera_letra, 
                isSeleccionada, nPalabrasRespondidas)
    else:
        if (request.method == 'POST') & (fin == 0):
            palabra_elegida = request.POST.get('palabra_elegida', '')
            isSeleccionada = 0
            n_palabra_adivinado = int(palabra_elegida[1:])
            primera_letra = getattr(palabras, 'p' + str(n_palabra_adivinado), '')[0]
            if n_palabra_adivinado > 4:
                palabras_modificadas[int(n_palabra_adivinado)-3] = primera_letra
            else:
                palabras_modificadas[int(n_palabra_adivinado)-2] = primera_letra

    # Estado actual del juego
         
    request.session['turno_actual'] = turno_actual
    request.session['n_palabra_adivinadoRonda2'] = n_palabra_adivinado
    request.session['letras_mostradasRonda2'] = letras_mostradas
    request.session['primera_letraRonda2'] = primera_letra
    request.session['puntos_jugador1'] = puntos_jugador1
    request.session['puntos_jugador2'] = puntos_jugador2
    request.session['ronda'] = "Ronda 2: Centro de la cadena"
    request.session['palabraElegida'] = palabra_elegida
    request.session['isSeleccionadaRonda2'] = isSeleccionada
    request.session['nPalabrasRespondidasRonda2'] = nPalabrasRespondidas
    request.session['palabrasModificadasR2'] = palabras_modificadas



    # Renderizar la plantilla con el contexto actualizado
    return render(request, 'centro_de_la_cadena.html', {
        'j1': j1, 'jugador1': jugador1, 'puntos_jugador1': puntos_jugador1,
        'j2': j2, 'jugador2': jugador2, 'puntos_jugador2': puntos_jugador2,
        'palabras_modificadas': palabras_modificadas, 'palabras': palabras,
        'n_palabra_adivinado': n_palabra_adivinado, 'turno_actual': turno_actual,
        'letras_mostradas': letras_mostradas,
        'primera_letra': primera_letra, 'fin':fin,
        'idPalabra': "p" + str(n_palabra_adivinado),
        'isSeleccionada':isSeleccionada,
        'palabra_elegida': palabra_elegida,
    })

def una_lleva_a_la_otra(request):
    #palabras_cargadasR3 = request.session.get('palabras_cargadasR3', False)
    #prompt = prompts.PROMPT_RONDA2y3
    #if palabras_cargadasR3 == False:
    #    JsonPalabras = llamadaAPIChatGPT(prompt)
    #    data = json.loads(JsonPalabras)
    #    request.session['datajson'] = data
    #    palabras = PalabrasEncadenadas(
    #        p1=data["p1"],
    #        p2=data["p2"],
    #        p3=data["p3"],
    #        p4=data["p4"],
    #        p5=data["p5"],
    #        p6=data["p6"],
    #        p7=data["p7"])
    #    palabras.save()
    #    palabras_cargadasR3 = True
    #    request.session['palabras_cargadasR3'] = palabras_cargadasR3

    # Datos de los jugadores
    fin=0
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
                fin=1
                request.session['puntos_jugador1'] = puntos_jugador1
                request.session['puntos_jugador2'] = puntos_jugador2
                return render(request, 'una_lleva_a_la_otra.html', {
        'j1': j1, 'jugador1': jugador1, 'puntos_jugador1': puntos_jugador1,
        'j2': j2, 'jugador2': jugador2, 'puntos_jugador2': puntos_jugador2,
        'palabras_modificadas': palabras_modificadas, 'palabras': palabras,
        'n_palabra_adivinado': n_palabra_adivinado, 'turno_actual': turno_actual,
        'letras_mostradas': letras_mostradas,
        'primera_letra': primera_letra, 'fin': fin, 
        'idPalabra': "p" + str(n_palabra_adivinado)
    })
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
                    fin=1
                    request.session['puntos_jugador1'] = puntos_jugador1
                    request.session['puntos_jugador2'] = puntos_jugador2
                    return render(request, 'una_lleva_a_la_otra.html', {
        'j1': j1, 'jugador1': jugador1, 'puntos_jugador1': puntos_jugador1,
        'j2': j2, 'jugador2': jugador2, 'puntos_jugador2': puntos_jugador2,
        'palabras_modificadas': palabras_modificadas, 'palabras': palabras,
        'n_palabra_adivinado': n_palabra_adivinado, 'turno_actual': turno_actual,
        'letras_mostradas': letras_mostradas,
        'primera_letra': primera_letra, 'fin': fin, 
        'idPalabra': "p" + str(n_palabra_adivinado)
    })
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
        request.session['ronda'] = "Ronda 3: Una lleva a la otra"

    # Renderizar la plantilla con el contexto actualizado
    return render(request, 'una_lleva_a_la_otra.html', {
        'j1': j1, 'jugador1': jugador1, 'puntos_jugador1': puntos_jugador1,
        'j2': j2, 'jugador2': jugador2, 'puntos_jugador2': puntos_jugador2,
        'palabras_modificadas': palabras_modificadas, 'palabras': palabras,
        'n_palabra_adivinado': n_palabra_adivinado, 'turno_actual': turno_actual,
        'letras_mostradas': letras_mostradas,
        'primera_letra': primera_letra, 'fin': fin, 
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
    #palabras_cargadasR4 = request.session.get('palabras_cargadasR4', False)
    #prompt = prompts.PROMPT_RONDA4
    #if palabras_cargadasR4 == False:
    #    JsonPalabras = llamadaAPIChatGPT(prompt)
    #    data = json.loads(JsonPalabras)
    #    request.session['datajson'] = data
    #    palabras = PalabrasEncadenadas(
    #        p1=data["p1"],
    #        p2=data["p2"],
    #        p3=data["p3"],
    #        p4=data["p4"],
    #        p5=data["p5"],
    #        p6=data["p6"],
    #        p7=data["p7"],
    #        p8=data["p8"],
    #        p9=data["p9"],
    #        p10=data["p10"],
    #        p11=data["p11"],
    #        p12=data["p12"],
    #        p13=data["p13"],
    #        final=data["final"],
    #        pista=data["pista"])
    #    palabras.save()
    #    palabras_cargadasR4 = True
    #    request.session['palabras_cargadasR4'] = palabras_cargadasR4
    if (request.session.get('j1') != None) | (request.session.get('j2') != None):
        if (request.session.get('puntos_jugador1', 0) >= request.session.get('puntos_jugador2', 0)):
            jFinal = request.session.get('j1', 'Tipo de j1 no ingresado')
            jugadorFinal = request.session.get('jugador1', 'Nombre del jugador 1 no ingresado')
            puntos_jugadorFinal = request.session.get('puntos_jugador1', 0)
        else:
            jFinal = request.session.get('j2', 'Tipo de j2 no ingresado')
            jugadorFinal = request.session.get('jugador2', 'Nombre del jugador 2 no ingresado')
            puntos_jugadorFinal = request.session.get('puntos_jugador2', 0)
        del request.session['j1']
        del request.session['j2']
        del request.session['jugador1']
        del request.session['jugador2']
        del request.session['puntos_jugador1']
        del request.session['puntos_jugador2'] 
        request.session['jFinal'] = jFinal
        request.session['jugadorFinal'] = jugadorFinal
        request.session['puntos_jugadorFinal'] = puntos_jugadorFinal
    jFinal = request.session.get('jFinal', 'Tipo de j1 no ingresado')
    jugadorFinal = request.session.get('jugadorFinal', 'Nombre del jugador 1 no ingresado')
    puntos_jugadorFinal = request.session.get('puntos_jugadorFinal', 0)

    fin = 0
    palabras = RondaFinal.objects.last()
    letras_mostradas = request.session.get('letras_mostradas', 1)

    n_palabra_adivinado = request.session.get('n_palabra_adivinado', 2)
    primera_letra = request.session.get('primera_letra', getattr(palabras, 'p' + str(n_palabra_adivinado), None)[0])
    comodines = request.session.get('comodines', 2)
    request.session['comodines'] = comodines

    idPalabra = "p" + str(n_palabra_adivinado)
    juego_acabado = 0
    palabras_modificadas = []

    for i in range(1, 14):  # Assuming there are 15 fields in RondaFinal
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
    respuestaIA = ''

    if (n_palabra_adivinado > 12):
        fin=1
        return render(request, 'ultima_cadena.html', {'jFinal': jFinal, 'jugadorFinal': jugadorFinal, 
                    'puntos_jugadorFinal' :puntos_jugadorFinal, 'palabras_modificadas': palabras_modificadas,
                    'palabras': palabras,'n_palabra_adivinado': n_palabra_adivinado,'primera_letra': primera_letra,
                    'comodines': comodines,'idPalabra': idPalabra,'fin': fin, 'respuesta_jugadorIA' :respuestaIA
                    })
    
    if (jFinal == "IA") | (jFinal == 'IA 1') | (jFinal == 'IA 2'):
        palabra1 = getattr(palabras, 'p' + str(n_palabra_adivinado-1), '')
        palabra2 = getattr(palabras, 'p' + str(n_palabra_adivinado+1), '')
        prompt = prompts.PROMPT_RONDAFINAL_IA_PLAYER.format(palabra1, palabra2, primera_letra)
        respuesta = llamadaAPIChatGPT(prompt).upper()
        respuestaIA = 'Mi respuesta es ' + respuesta
        (request, jFinal, jugadorFinal,
        puntos_jugadorFinal, palabras, palabras_modificadas, 
        n_palabra_adivinado, letras_mostradas,
        primera_letra, fin, respuesta, palabra_a_adivinar
        ,comodines, idPalabra, juego_acabado) = jugarTurnoUltimaCadena(
                                                        request, jFinal, jugadorFinal,
                                                        puntos_jugadorFinal, palabras, palabras_modificadas, 
                                                        n_palabra_adivinado, letras_mostradas,
                                                        primera_letra, fin, respuesta, palabra_a_adivinar
                                                        ,comodines, idPalabra, juego_acabado)
    else:
        if request.method == 'POST':
            print(n_palabra_adivinado)
            form = TurnFormulario(request.POST)
            if form.is_valid():
                respuesta = form.cleaned_data['respuesta'].upper()
                nombre_campo = 'p' + str(n_palabra_adivinado)
                palabra_a_adivinar = getattr(palabras, nombre_campo, None)
                (request, jFinal, jugadorFinal,
                puntos_jugadorFinal, palabras, palabras_modificadas, 
                n_palabra_adivinado, letras_mostradas,
                primera_letra, fin, respuesta, palabra_a_adivinar
                ,comodines, idPalabra, juego_acabado) = jugarTurnoUltimaCadena(
                                                                request, jFinal, jugadorFinal,
                                                                puntos_jugadorFinal, palabras, palabras_modificadas, 
                                                                n_palabra_adivinado, letras_mostradas,
                                                                primera_letra, fin, respuesta, palabra_a_adivinar
                                                                ,comodines, idPalabra, juego_acabado)


    idPalabra = "p" + str(n_palabra_adivinado)
    return render(request, 'ultima_cadena.html', {'jFinal': jFinal, 'jugadorFinal': jugadorFinal, 
                    'puntos_jugadorFinal' :puntos_jugadorFinal, 'palabras_modificadas': palabras_modificadas,
                    'palabras': palabras, 'n_palabra_adivinado': n_palabra_adivinado,
                    'primera_letra': primera_letra,'comodines': comodines, 'idPalabra': idPalabra,
                    'fin': fin, 'juego_acabado' : juego_acabado, 'respuesta_jugadorIA' :respuestaIA
                    })

def ultima_palabra(request):
    juego_acabado=0  
    jFinal = request.session.get('jFinal', 'Tipo de j1 no ingresado')
    jugadorFinal = request.session.get('jugadorFinal', 'Nombre del jugador 1 no ingresado')
    puntos_jugadorFinal = request.session.get('puntos_jugadorFinal', 80000)

    palabras = RondaFinal.objects.last()

    n_palabra_adivinado = request.session.get('n_palabra_adivinado', 2)
    pistaMostrada = request.session.get('pistaMostrada', 1)
    palabra_inicial = getattr(palabras, 'p13', None)
    request.session['palabra_inicial'] = palabra_inicial
    solucion = getattr(palabras, 'final', None)
    solucion_mostrada = getattr(palabras, 'final', None)[0] + getattr(palabras, 'final', None)[1] + '________' + getattr(palabras, 'final', None)[len(solucion)-1]
    request.session['solucion_mostrada'] = solucion_mostrada
    pista = getattr(palabras, 'pista', None)
    pista_mostrada = request.session.get('pista_mostrada', '?')
    request.session['pista_mostrada'] = pista_mostrada
    respuestaIA = ''

    if (jFinal == "IA") | (jFinal == 'IA 1') | (jFinal == 'IA 2'):
        if pistaMostrada == 0:
            prompt = prompts.PROMPT_PALABRAFINAL_IA_PLAYER.format(palabra_inicial, solucion_mostrada)
            jsonRespuesta = llamadaAPIChatGPT(prompt).upper()
            data = json.loads(jsonRespuesta)
            if data["pista"] == 'SI':
                (request, pistaMostrada, pista_mostrada, pista, 
                puntos_jugadorFinal) = jugarTurnoUltimaPalabraMostrarPista(request, pistaMostrada, 
                pista_mostrada, pista, puntos_jugadorFinal)
            else:
                respuesta = data["respuesta"]
                respuestaIA = 'Mi respuesta es ' + respuesta
                (request, puntos_jugadorFinal, respuesta,
                solucion, solucion_mostrada, juego_acabado) = jugarTurnoUltimaPalabra(request,
                puntos_jugadorFinal, respuesta,
                solucion, solucion_mostrada, juego_acabado)
        else:
            prompt = prompts.PROMPT_PALABRAFINALCONPISTA_IA_PLAYER.format(palabra_inicial, pista_mostrada, solucion_mostrada)
            respuesta = llamadaAPIChatGPT(prompt).upper()
            respuestaIA = 'Mi respuesta es ' + respuesta
            (request, puntos_jugadorFinal, respuesta,
            solucion, solucion_mostrada, juego_acabado) = jugarTurnoUltimaPalabra(request,
            puntos_jugadorFinal, respuesta,
            solucion, solucion_mostrada, juego_acabado)
    else:
        if request.method == 'POST':
            solicitaPista = request.POST.get('pista', '')
            if solicitaPista == 'yes':
                (request, pistaMostrada, pista_mostrada, pista, 
                puntos_jugadorFinal) = jugarTurnoUltimaPalabraMostrarPista(request, pistaMostrada, 
                pista_mostrada, pista, puntos_jugadorFinal)
            else:
                respuesta = request.POST.get('respuesta', '')
                (request, puntos_jugadorFinal, respuesta,
                solucion, solucion_mostrada, juego_acabado) = jugarTurnoUltimaPalabra(request,
                puntos_jugadorFinal, respuesta,
                solucion, solucion_mostrada, juego_acabado)
    idPalabra = "p" + str(n_palabra_adivinado)
    return render(request, 'ultima_palabra.html', {'jFinal': jFinal, 'jugadorFinal': jugadorFinal, 
                                                'puntos_jugadorFinal' :puntos_jugadorFinal,
                                                'idPalabra': idPalabra,
                                                'palabra_inicial': palabra_inicial,
                                                'solucion': solucion,
                                                'solucion_mostrada':solucion_mostrada,
                                                'pista': pista,
                                                'pista_mostrada': pista_mostrada,
                                                'fin': 0,
                                                'juego_acabado' : juego_acabado,
                                                'pistaMostrada': pistaMostrada,
                                                'respuestaIA': respuestaIA
                                                })

def fin_juego(request):

    jFinal = request.session.get('jFinal', 'Tipo de j1 no ingresado')
    jugadorFinal = request.session.get('jugadorFinal', 'Nombre del jugador 1 no ingresado')
    puntos_jugadorFinal = request.session.get('puntos_jugadorFinal', 0)

    del request.session['npa']
    del request.session['lm']
    del request.session['pl']


    del request.session['primera_letraRonda2']
    del request.session['letras_mostradasRonda2']
    del request.session['n_palabra_adivinadoRonda2']

    del request.session['primera_letraRonda3']
    del request.session['letras_mostradasRonda3']
    del request.session['n_palabra_adivinadoRonda3']

    del request.session['ronda']
    del request.session['turno_actual']

        
    del request.session['letras_mostradas']
    del request.session['primera_letra']
    del request.session['n_palabra_adivinado']
    del request.session['palabrasModificadas']
    del request.session['comodines']

    del request.session['palabra_inicial']
    del request.session['solucion_mostrada']
    del request.session['pista_mostrada']

    #guardar puntos en bbdd

    del request.session['jFinal']
    del request.session['jugadorFinal']
    del request.session['puntos_jugadorFinal']


    return render(request, 'fin_juego.html', {'jFinal': jFinal, 'jugadorFinal': jugadorFinal,
        'puntos_jugadorFinal' :puntos_jugadorFinal})


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


def llamadaAPIChatGPT(prompt):
    response = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                        {"role": "user", "content": prompt},
                    ]
                )
    return response.choices[0].message.content

def jugarTurnoPrimeraRonda(request, html, j1, j2, jugador1, jugador2,
                            puntos_jugador1, puntos_jugador2, turno_actual, palabras, 
                            palabras_modificadas, n_palabra_adivinado, letras_mostradas,
                            primera_letra, fin, respuesta, palabra_a_adivinar):
    if respuesta == palabra_a_adivinar:
    # Asignar puntos al jugador correcto
        if turno_actual == j1:
            puntos_jugador1 += 10000
        else:
            puntos_jugador2 += 10000

        palabras_modificadas[int(n_palabra_adivinado)-1] = palabra_a_adivinar
        n_palabra_adivinado += 1
        if n_palabra_adivinado > 6:
                fin=1
                request.session['puntos_jugador1'] = puntos_jugador1
                request.session['puntos_jugador2'] = puntos_jugador2
                return (request, html, j1, j2, jugador1, jugador2,
                puntos_jugador1, puntos_jugador2, turno_actual, palabras, 
                palabras_modificadas, n_palabra_adivinado, letras_mostradas,
                primera_letra, fin, respuesta, palabra_a_adivinar)
        letras_mostradas = 1 
        palabra_adivinada = getattr(palabras, 'p' + str(n_palabra_adivinado), '')
        letras_faltantes = len(palabra_adivinada) - letras_mostradas
        palabras_modificadas[int(n_palabra_adivinado)-1] = getattr(palabras, 'p' + str(n_palabra_adivinado), '')[0] +'_ ' * letras_faltantes + f" ({len(palabra_adivinada)})"
        primera_letra = getattr(palabras, 'p' + str(n_palabra_adivinado), None)[0] 
    else:
        if turno_actual == j2:
            turno_actual = j1
        else:
            turno_actual = j2

        letras_mostradas += 1
        if len(palabra_a_adivinar) <= letras_mostradas:
            # Lógica cuando se han revelado todas las letras
            if turno_actual == j1:
                puntos_jugador1 += 10000
            else:
                puntos_jugador2 += 10000

            palabras_modificadas[int(n_palabra_adivinado)-1] = palabra_a_adivinar
            n_palabra_adivinado += 1
            if n_palabra_adivinado > 6:
                fin=1
                request.session['puntos_jugador1'] = puntos_jugador1
                request.session['puntos_jugador2'] = puntos_jugador2
                return (request, html, j1, j2, jugador1, jugador2,
                puntos_jugador1, puntos_jugador2, turno_actual, palabras, 
                palabras_modificadas, n_palabra_adivinado, letras_mostradas,
                primera_letra, fin, respuesta, palabra_a_adivinar)
            
            palabras_modificadas[int(n_palabra_adivinado)-1] = getattr(palabras, 'p' + str(n_palabra_adivinado), '')[0]
            primera_letra = getattr(palabras, 'p' + str(n_palabra_adivinado), None)[0]
            letras_mostradas = 1 
        else:
            palabra_adivinada = getattr(palabras, 'p' + str(n_palabra_adivinado), '')
            letras_faltantes = len(palabra_adivinada) - letras_mostradas
            primera_letra += palabra_adivinada[letras_mostradas-1] 
            palabras_modificadas[int(n_palabra_adivinado)-1] = primera_letra +'_ ' * letras_faltantes + f" ({len(palabra_adivinada)})"
    return (request, html, j1, j2, jugador1, jugador2,
            puntos_jugador1, puntos_jugador2, turno_actual, palabras, 
            palabras_modificadas, n_palabra_adivinado, letras_mostradas,
            primera_letra, fin, respuesta, palabra_a_adivinar)

def jugarTurnoSegundaRonda(request, respuesta, palabra_a_adivinar, j1, j2, jugador1, jugador2,
                           turno_actual, puntos_jugador1, puntos_jugador2, palabras,
                           n_palabra_adivinado, palabras_modificadas, fin, letras_mostradas, primera_letra, 
                           isSeleccionada, nPalabrasRespondidas):
    if respuesta == palabra_a_adivinar:
        nPalabrasRespondidas += 1
        isSeleccionada = 1
    # Asignar puntos al jugador correcto
        if turno_actual == j1:
            puntos_jugador1 += 5000
        else:
            puntos_jugador2 += 5000
        if n_palabra_adivinado > 4:
            palabras_modificadas[int(n_palabra_adivinado)-3] = palabra_a_adivinar
        else:
            palabras_modificadas[int(n_palabra_adivinado)-2] = palabra_a_adivinar
        n_palabra_adivinado += 1
        if n_palabra_adivinado == 4:
            n_palabra_adivinado += 1
        if nPalabrasRespondidas == 4:
            fin=1
            request.session['puntos_jugador1'] = puntos_jugador1
            request.session['puntos_jugador2'] = puntos_jugador2
            return (request, respuesta, palabra_a_adivinar, j1, j2, jugador1, jugador2,
                           turno_actual, puntos_jugador1, puntos_jugador2, palabras,
                           n_palabra_adivinado, palabras_modificadas, fin , letras_mostradas, primera_letra
                           ,isSeleccionada, nPalabrasRespondidas)
    else:
        turno_actual = j2 if turno_actual == j1 else j1
        letras_mostradas += 1
        if len(palabra_a_adivinar) <= letras_mostradas:
            # Lógica cuando se han revelado todas las letras
            nPalabrasRespondidas += 1
            if turno_actual == j1:
                puntos_jugador1 += 5000
            else:
                puntos_jugador2 += 5000
            if n_palabra_adivinado > 4:
                palabras_modificadas[int(n_palabra_adivinado)-3] = palabra_a_adivinar
            else:
                palabras_modificadas[int(n_palabra_adivinado)-2] = palabra_a_adivinar
            n_palabra_adivinado += 1
            if n_palabra_adivinado == 4: 
                n_palabra_adivinado += 1
            if nPalabrasRespondidas == 4:
                fin=1
                request.session['puntos_jugador1'] = puntos_jugador1
                request.session['puntos_jugador2'] = puntos_jugador2
                return (request, respuesta, palabra_a_adivinar, j1, j2, jugador1, jugador2,
                           turno_actual, puntos_jugador1, puntos_jugador2, palabras,
                           n_palabra_adivinado, palabras_modificadas, fin,letras_mostradas, primera_letra, 
                            isSeleccionada, nPalabrasRespondidas)
            letras_mostradas = 1  
        else:
            # Actualizar primera_letra para mostrar las letras acumuladas hasta ahora
            primera_letra += getattr(palabras, 'p' + str(n_palabra_adivinado), None)[letras_mostradas-1] 
            if n_palabra_adivinado > 4:
                palabras_modificadas[int(n_palabra_adivinado)-3] = primera_letra
            else:
                palabras_modificadas[int(n_palabra_adivinado)-2] = primera_letra
    return (request, respuesta, palabra_a_adivinar, j1, j2, jugador1, jugador2,
                           turno_actual, puntos_jugador1, puntos_jugador2, palabras,
                           n_palabra_adivinado, palabras_modificadas, fin , letras_mostradas, primera_letra,
                              isSeleccionada, nPalabrasRespondidas)

def jugarTurnoUltimaCadena(request, jFinal, jugadorFinal,
                            puntos_jugadorFinal, palabras, palabras_modificadas, 
                            n_palabra_adivinado, letras_mostradas,
                            primera_letra, fin, respuesta, palabra_a_adivinar
                            ,comodines, idPalabra, juego_acabado):
    if respuesta == palabra_a_adivinar:
        palabras_modificadas[int(n_palabra_adivinado/2)-1] = palabra_a_adivinar
        if n_palabra_adivinado >= 12:
            fin=1
            juego_acabado = 0
            return (request, jFinal, jugadorFinal,
                        puntos_jugadorFinal, palabras, palabras_modificadas, 
                        n_palabra_adivinado, letras_mostradas,
                        primera_letra, fin, respuesta, palabra_a_adivinar
                        ,comodines, idPalabra, juego_acabado)
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
            if n_palabra_adivinado >= 12:
                fin=1
                juego_acabado = 0
                return (request, jFinal, jugadorFinal,
                        puntos_jugadorFinal, palabras, palabras_modificadas, 
                        n_palabra_adivinado, letras_mostradas,
                        primera_letra, fin, respuesta, palabra_a_adivinar
                        ,comodines, idPalabra, juego_acabado)
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
            puntos_jugadorFinal =  puntos_jugadorFinal/2
            request.session['puntos_jugadorFinal'] = puntos_jugadorFinal

    return (request, jFinal, jugadorFinal,
        puntos_jugadorFinal, palabras, palabras_modificadas, 
        n_palabra_adivinado, letras_mostradas,
        primera_letra, fin, respuesta, palabra_a_adivinar
        ,comodines, idPalabra, juego_acabado)

def jugarTurnoUltimaPalabra(request, puntos_jugadorFinal, respuesta,
                            solucion, solucion_mostrada, juego_acabado,
                            ):
    if respuesta.upper() != solucion.upper():
        puntos_jugadorFinal = 0
        request.session['puntos_jugadorFinal'] = puntos_jugadorFinal
    solucion_mostrada = solucion
    request.session['solucion_mostrada'] = solucion_mostrada
    juego_acabado = 1
    return (request, puntos_jugadorFinal, respuesta,
            solucion, solucion_mostrada, juego_acabado)

def jugarTurnoUltimaPalabraMostrarPista(request, pistaMostrada, pista_mostrada, pista, puntos_jugadorFinal):
    pistaMostrada = 0
    request.session['pistaMostrada'] = pistaMostrada
    pista_mostrada = pista
    request.session['pista_mostrada'] = pista_mostrada
    puntos_jugadorFinal = puntos_jugadorFinal / 2
    request.session['puntos_jugadorFinal'] = puntos_jugadorFinal
    return(request, pistaMostrada, pista_mostrada, pista, puntos_jugadorFinal)
