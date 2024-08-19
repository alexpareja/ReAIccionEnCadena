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
from django.contrib.auth import update_session_auth_hash, login, authenticate
from django.contrib.auth.models import User
from .forms import OpcionForm
from .models import PalabrasEncadenadas, EslabonCentral, RondaFinal, Puntuaciones
from django import template
from django.urls import reverse
import unicodedata
import re

openai.api_key = settings.OPENAI_API_KEY


def index(request):
    user_id = request.session.get('_auth_user_id')
    user_backend = request.session.get('_auth_user_backend')
    user_hash = request.session.get('_auth_user_hash')

    request.session.flush()

    request.session['_auth_user_id'] = user_id
    request.session['_auth_user_backend'] = user_backend
    request.session['_auth_user_hash'] = user_hash

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
    form = FormNombresJugadores(
        initial={'jugador1': request.user.get_username()})

    if request.method == 'POST':
        form = FormNombresJugadores(request.POST)
        if form.is_valid():
            jugador1 = form.cleaned_data['jugador1']
            jugador2 = form.cleaned_data['jugador2']
            request.session['jugador1'] = jugador1
            request.session['jugador2'] = jugador2
        return redirect(instrucciones_palabras_encadenadas)
    return render(request, 'pregame.html', {'form': form, 'j1': j1, 'j2': j2})

def instrucciones_palabras_encadenadas(request):
    texto_instrucciones = """
    En esta ronda, los jugadores deben adivinar 6 palabras, relacionadas todas ellas con un mismo tema, indicado al incio de la cadena.

    Todas las palabras comienzan con la letra final de la palabra anterior.

    Las palabras se adivinarán por turnos, en caso de acertar la palabra, el jugador obtendrá 2000 puntos y pasará a adivinar la siguiente palabra. En el caso contrario, el turno pasará al otro jugador y se mostrará una letra más de la palabra.

    Si ninguno de los jugadores logra adivinar la palabra, se mostrará la palabra completa y se pasará a la siguiente. 

    Comienza el jugador 2 a adivinar la primera palabra.

    """
    contexto = {
        'tituloDelJuego': 'palabras encadenadas',
        'instrucciones': texto_instrucciones,
        'urlDelJuego': reverse('palabras_encadenadas'),
    }
    return render(request, 'base_instrucciones.html', contexto)

def instrucciones_centro_de_la_cadena(request):
    texto_instrucciones = """
    En esta ronda, los jugadores deben adivinar 4 palabras.

    En el panel del juego, se mostrarán desde el inicio tres palabras: la primera, la última y la palabra intermedia de la cadena.

    Cada palabra a adivinar guarda relación con la palabra anterior y la palabra siguiente.

    En caso de acertar el jugador obtendrá 5000 puntos y pasará a adivinar la siguiente palabra. En el caso contrario, el turno pasará al otro jugador y se mostrará una letra más de la palabra.

    Cada vez que a un jugador le toque adivinar una nueva palabra, podrá seleccionar que quiera, eligiendo entre la que está más arriba o abajo en el panel.

    Comienza el jugador con menos puntos acumulados a adivinar la primera palabra.

    """
    contexto = {
        'tituloDelJuego': 'centro de la cadena',
        'instrucciones': texto_instrucciones,
        'urlDelJuego': reverse('centro_de_la_cadena'),
    }
    return render(request, 'base_instrucciones.html', contexto)

def instrucciones_una_lleva_a_la_otra(request):
    texto_instrucciones = """
    En esta ronda, los jugadores deben adivinar 5 palabras.

    En el panel del juego, se mostrarán desde el inicio dos palabras de la cadena: la primera, la última.

    Al igual que en la ronda anterior, cada palabra a adivinar guarda relación con la palabra anterior y la palabra siguiente.

    En caso de acertar el jugador obtendrá 10000 puntos y pasará a adivinar la siguiente palabra. En el caso contrario, el turno pasará al otro jugador y se mostrará una letra más de la palabra.

    Cada vez que a un jugador le toque adivinar una nueva palabra, podrá seleccionar que quiera, eligiendo entre la que está más arriba o abajo en el panel.

    Comienza el jugador con menos puntos acumulados a adivinar la primera palabra.

    """
    contexto = {
        'tituloDelJuego': 'una lleva a la otra',
        'instrucciones': texto_instrucciones,
        'urlDelJuego': reverse('una_lleva_a_la_otra'),
    }
    return render(request, 'base_instrucciones.html', contexto)

def instrucciones_ultima_cadena(request):
    texto_instrucciones = """
    A partir de esta ronda, solo jugará el jugador con más puntos acumulados.

    El jugador deberá adivinar 6 palabras, las cuales tienen relación con las palabras que se encuentran arriba y abajo de ella.

    El jugador tendrá dos oportunidades para acertar la palabra. Sin embargo, cada fallo le costará la mitad de sus puntos.

    También contará con dos comodines, que en los primeros dos fallos, le permitirán ver una letra más de la palabra.

    """
    contexto = {
        'tituloDelJuego': 'última cadena',
        'instrucciones': texto_instrucciones,
        'urlDelJuego': reverse('ultima_cadena'),
    }
    return render(request, 'base_instrucciones.html', contexto)

def instrucciones_ultima_palabra(request):
    texto_instrucciones = """
    Esta es la última ronda del juego.

    EL jugador debe de adivinar unícamente una palabra. Para adivinarla tendrá como pistas la palabra de arriba con la que tiene relación y las dos primeras letras y la última letra de la palabra.

    El jugador puede tomar la decisión de comprar o no el eslabón misterio. Si lo compra se mostrará la palabra de abajo, con la que también tiene relación. Este eslabón le costará la mitad de sus puntos.

    En caso de acertar la palabra el jugador ganará los puntos que tenga acumulados hasta ese momento. En caso contrario, perderá todos los puntos.

    """
    contexto = {
        'tituloDelJuego': 'último eslabón',
        'instrucciones': texto_instrucciones,
        'urlDelJuego': reverse('ultima_palabra'),
    }
    return render(request, 'base_instrucciones.html', contexto)

def palabras_encadenadas(request):
    palabras_cargadasR1 = request.session.get('palabras_cargadasR1', False)
    prompt = prompts.PromptPrueba1
    system_prompts = [
        "Eres un generador de palabras únicas y reales en español.", #2 like #2 dislike
        "Proporciona dos palabras reales y únicas en español.", #2 like
        "Genera dos palabras que sean válidas en el idioma español. ", #2 like 
        "Eres un generador de temas para un concurso. Debes ser creativo a la hora de ofrecer temas, abarcando cualquier tema en español."] # 1 meh
    sys_pr = random.choice(system_prompts)
    print(sys_pr)
    while not palabras_cargadasR1:
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": sys_pr
                },
                {
                    "role": "user",
                    "content": "Piensa en un tema (máximo 2 palabras) y damelo con la siguiente estructura JSON:\n{\n  \"tema\": \"\"\n}"
                }
            ],
            temperature=1.65,
            max_tokens=20,
            response_format={"type": "json_object"}
        )
        print(response)
        # JsonPalabras = llamadaAPIChatGPT(prompt)
        tema = json.loads(response.choices[0].message.content)["tema"]

        prompt2 = "Dame una lista de 6 palabras en castellano relacionadas con el tema " + tema + \
            ". Asegurate de que cada palabra empiece con la última letra de la anterior palabra de la lista. Las 6 palabras no pueden ser iguales ni poner palabras compuestas por más de una palabra, con un máximo de 12 letras. Devuelveme esta lista en un JSON con la siguiente estructura {\"tema\": \"\",   \"p1\": \"\",   \"p2\": \"\",   \"p3\": \"\",   \"p4\": \"\",   \"p5\": \"\",   \"p6\": \"\" }"
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "Eres un generador de palabras. Debes asegurarte de que todas las palabras que generas empiezan por la última letra de la palabra anterior en la lista en español castellano."
                },
                {
                    "role": "user",
                    "content": prompt2
                }
            ],
            temperature=0.5,
            max_tokens=300,
            response_format={"type": "json_object"}
        )
        data = json.loads(response.choices[0].message.content)
        palabras = [data["p1"], data["p2"], data["p3"],
                    data["p4"], data["p5"], data["p6"]]

        # Verificar si las palabras encadenadas son correctas
        if all(palabras[i].startswith(palabras[i-1][-1]) for i in range(1, len(palabras))):
            request.session['datajson'] = data
            modelo_palabras = PalabrasEncadenadas(
                tema=tema,
                p1=data["p1"],
                p2=data["p2"],
                p3=data["p3"],
                p4=data["p4"],
                p5=data["p5"],
                p6=data["p6"])
            modelo_palabras.save()
            palabras_cargadasR1 = True

    request.session['palabras_cargadasR1'] = palabras_cargadasR1

    fin = 0
    j1 = request.session.get('j1', 'Tipo de j1 no ingresado')
    j2 = request.session.get('j2', 'Tipo de j2 no ingresado')
    jugador1 = request.session.get(
        'jugador1', 'Nombre del jugador 1 no ingresado')
    jugador2 = request.session.get(
        'jugador2', 'Nombre del jugador 2 no ingresado')

    # Obteniendo las palabras de la ronda
    palabras = PalabrasEncadenadas.objects.last()
    letras_mostradas = request.session.get('lm', 1)

    # Estado actual del juego

    turno_actual = request.session.get('turno_actual', j2)
    n_palabra_adivinado = request.session.get('npa', 1)
    primera_letra = request.session.get('pl', getattr(
        palabras, 'p' + str(n_palabra_adivinado), '')[0])
    puntos_jugador1 = request.session.get('puntos_jugador1', 0)
    puntos_jugador2 = request.session.get('puntos_jugador2', 0)
    IA_jugando = 0
    palabras_modificadas = []
    primer_intentoR1 = request.session.get('primer_intentoR1', 0)

    for i in range(1, 7):
        nombre_campo = 'p' + str(i)
        palabra = getattr(palabras, nombre_campo, '')
        palabra_modificada = ''
        if i == n_palabra_adivinado:
            guiones = '_ ' * (len(palabra) - 1)
            palabra_modificada = primera_letra.upper() + guiones + \
                f" ({len(palabra)})"
        elif i > n_palabra_adivinado:
            palabra_modificada = ''
        else:
            palabra_modificada = palabra
        palabras_modificadas.insert((i-1), palabra_modificada)

    nombre_campo = 'p' + str(n_palabra_adivinado)
    palabra_a_adivinar = getattr(palabras, nombre_campo, '').upper()
    respuestaJugadorIA1 = ''
    respuestaJugadorIA2 = ''

    html = 'palabras_encadenadas.html'
    if (turno_actual == "IA") | (turno_actual == 'IA 1') | (turno_actual == 'IA 2'):
        if primer_intentoR1 == 1:
            IA_jugando = 1
            tema = getattr(palabras, 'tema', '')
            n_letras = len(
                getattr(palabras, 'p' + str(n_palabra_adivinado), ''))
            # prompt = prompts.PROMPT_RONDA1_IA_PLAYER.format(
            # tema, primera_letra, n_letras)
            # print(prompt)
            # respuesta = llamadaAPIChatGPT(prompt).upper()
            jsonrespuesta = openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "Debes responder palabras relacionadas a un tema que te indica el usuario. Debes relacionar tu respuesta a este tema obligatoriamente."
                    },
                    {
                        "role": "user",
                        "content": "Dame una palabra que se relacione con el tema " + tema + " y que empiece por " + palabras_modificadas[int(n_palabra_adivinado)-1] + ". La palabra tiene" + str(n_letras) + " letras en español. Devuélveme un JSON con la siguiente estructura:\n{\n\"palabra\": \"\",\n\"explicacion\":\"\"\n}\nLa explicación de la relación con el tema debe ser muy breve."
                    }
                ],
                temperature=1.2,
                max_tokens=100,
                response_format={"type": "json_object"}
            )
            dataRespuesta = json.loads(
                jsonrespuesta.choices[0].message.content)
            respuesta = dataRespuesta['palabra'].upper()
            if (turno_actual == 'IA 1'):
                respuestaJugadorIA1 = 'Mi respuesta es ' + respuesta + \
                    '. Explicación: ' + dataRespuesta['explicacion']
            else:
                respuestaJugadorIA2 = 'Mi respuesta es ' + respuesta + \
                    '. Explicación: ' + dataRespuesta['explicacion']
            (request, html, j1, j2, jugador1, jugador2,
             puntos_jugador1, puntos_jugador2, turno_actual, palabras,
             palabras_modificadas, n_palabra_adivinado, letras_mostradas,
             primera_letra, fin, respuesta, palabra_a_adivinar) = jugarTurnoPrimeraRonda(
                request, html, j1, j2, jugador1, jugador2,
                puntos_jugador1, puntos_jugador2, turno_actual, palabras,
                palabras_modificadas, n_palabra_adivinado, letras_mostradas,
                primera_letra, fin, respuesta, palabra_a_adivinar)
        else:
            primer_intentoR1 = 1
            request.session['primer_intentoR1'] = primer_intentoR1
    else:
        IA_jugando = 0
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
    if (turno_actual == "IA") | (turno_actual == 'IA 1') | (turno_actual == 'IA 2'):
        IA_jugando = 1
    else:
        IA_jugando = 0

    request.session['turno_actual'] = turno_actual
    request.session['npa'] = n_palabra_adivinado
    request.session['lm'] = letras_mostradas
    request.session['pl'] = primera_letra
    request.session['puntos_jugador1'] = puntos_jugador1
    request.session['puntos_jugador2'] = puntos_jugador2
    request.session['ronda'] = 'Ronda 1: Palabras encadenadas'

    return render(request, 'palabras_encadenadas.html', {
        'j1': j1, 'j2': j2, 'jugador1': jugador1, 'jugador2': jugador2,
        'puntos_jugador1': puntos_jugador1, 'puntos_jugador2': puntos_jugador2,
        'turno_actual': turno_actual, 'palabras': palabras, 'palabras_modificadas': palabras_modificadas,
        'n_palabra_adivinado': n_palabra_adivinado, 'turno_actual': turno_actual,
        'letras_mostradas': letras_mostradas, 'primera_letra': primera_letra, 'fin': fin,
        'idPalabra': "p" + str(n_palabra_adivinado), 'respuestaIA1': respuestaJugadorIA1,
        'IA_jugando': IA_jugando, 'respuestaIA2': respuestaJugadorIA2
    })

def marcador_ronda(request):

    j1 = request.session.get('j1', 'Tipo de j1 no ingresado')
    j2 = request.session.get('j2', 'Tipo de j2 no ingresado')
    jugador1 = request.session.get(
        'jugador1', 'Nombre del jugador 1 no ingresado')
    jugador2 = request.session.get(
        'jugador2', 'Nombre del jugador 2 no ingresado')
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

    return render(request, 'marcador_ronda.html', {'j1': j1, 'j2': j2, 'jugador1': jugador1, 'jugador2': jugador2,
                                                   'puntos_jugador1': puntos_jugador1, 'puntos_jugador2': puntos_jugador2, 'ronda': ronda, 'urlDelJuego': urlDelJuego})

def centro_de_la_cadena(request):
    palabras_cargadasR2 = request.session.get('palabras_cargadasR2', False)
    prompt = prompts.PROMPT_RONDA2Y3
    if palabras_cargadasR2 == False:
        arrayPanel = generarPanel7huecos()
        while len(set(arrayPanel)) != 7:
            arrayPanel = generarPanel7huecos()

        # JsonPalabras = llamadaAPIChatGPTModeloFineTuning(prompt)
        # JsonPalabras = llamadaAPIChatGPT(prompt)
        print(arrayPanel)
        request.session['datajson'] = arrayPanel
        palabras = EslabonCentral(
            p1=arrayPanel[0],
            p2=arrayPanel[1],
            p3=arrayPanel[2],
            p4=arrayPanel[3],
            p5=arrayPanel[4],
            p6=arrayPanel[5],
            p7=arrayPanel[6])
        palabras.save()
        palabras_cargadasR2 = True
        request.session['palabras_cargadasR2'] = palabras_cargadasR2

    # Datos de los jugadores
    fin = request.session.get('finR2', 0)
    j1 = request.session.get('j1', 'Tipo de j1 no ingresado')
    jugador1 = request.session.get(
        'jugador1', 'Nombre del jugador 1 no ingresado')
    j2 = request.session.get('j2', 'Tipo de j2 no ingresado')
    jugador2 = request.session.get(
        'jugador2', 'Nombre del jugador 2 no ingresado')
    puntos_jugador1 = request.session.get('puntos_jugador1', 0)
    puntos_jugador2 = request.session.get('puntos_jugador2', 0)
    n_palabra_adivinado = request.session.get('n_palabra_adivinadoRonda2', 0)

    if n_palabra_adivinado == 0:
        if puntos_jugador1 >= puntos_jugador2:
            turno_actual = j2
        else:
            turno_actual = j1
    else:
        turno_actual = request.session.get('turno_actual', j2)

    # Obteniendo las palabras de la ronda
    palabras = EslabonCentral.objects.last()
    letras_mostradas = request.session.get('letras_mostradasRonda2', 1)
    nPalabrasRespondidas = request.session.get('nPalabrasRespondidasRonda2', 0)
    isSeleccionada = request.session.get('isSeleccionadaRonda2', 1)
    palabra_elegida = request.session.get('palabraElegida', '')
    primera_letra = ''
    respuesta = ''
    actualizarActivos = False
    respuestaJugadorIA1 = ''
    respuestaJugadorIA2 = ''
    IA_jugando = 0
    primer_intentoR2 = request.session.get('primer_intentoR2', 0)
    palabras_modificadasInit = []
    for i in range(1, 7):
        nombre_campo = 'p' + str(i)
        palabra_modificada = ''
        if i != 1 and i != 7 and i != 4:
            if i == n_palabra_adivinado:
                palabra_modificada = primera_letra
            palabras_modificadasInit.insert(i, palabra_modificada)

    palabras_modificadas = request.session.get(
        'palabrasModificadasR2', palabras_modificadasInit)

    if isSeleccionada == 0:
        primera_letra = request.session.get('primera_letraRonda2', getattr(
            palabras, 'p' + str(n_palabra_adivinado), '')[0])
        if (turno_actual == "IA") | (turno_actual == 'IA 1') | (turno_actual == 'IA 2'):
            if primer_intentoR2 == 1:
                IA_jugando = 1
                palabra_antes = '-'
                palabra_despues = '-'
                if n_palabra_adivinado > 4:
                    if 0 < (int(n_palabra_adivinado)-3) <= 3:
                        if palabras_modificadas[int(n_palabra_adivinado)-4] != '':
                            palabra_antes = palabras_modificadas[int(
                                n_palabra_adivinado)-4]
                    else:
                        palabra_antes = getattr(
                            palabras, 'p' + str(n_palabra_adivinado-1), '')
                    if 0 <= (int(n_palabra_adivinado)-3) < 3:
                        if palabras_modificadas[int(n_palabra_adivinado)-2] != '':
                            palabra_despues = palabras_modificadas[int(
                                n_palabra_adivinado)-2]
                    else:
                        palabra_despues = getattr(
                            palabras, 'p' + str(n_palabra_adivinado+1), '')
                else:
                    if 0 < (int(n_palabra_adivinado)-2) <= 3:
                        if palabras_modificadas[int(n_palabra_adivinado)-3] != '':
                            palabra_antes = palabras_modificadas[int(
                                n_palabra_adivinado)-3]
                    else:
                        palabra_antes = getattr(
                            palabras, 'p' + str(n_palabra_adivinado-1), '')
                    if 0 <= (int(n_palabra_adivinado)-2) < 3:
                        if palabras_modificadas[int(n_palabra_adivinado)-1] != '':
                            palabra_despues = palabras_modificadas[int(
                                n_palabra_adivinado)-1]
                    else:
                        palabra_despues = getattr(
                            palabras, 'p' + str(n_palabra_adivinado+1), '')
                # prompt = prompts.PROMPT_RONDA2y3_IA_PLAYER_JUGARTURNO.format(palabra_antes, palabra_despues, primera_letra)
                # print(prompt)
                respuestaJSON = json.loads(openai.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {
                            "role": "user",
                            "content": "En base a la palabra " + palabra_antes+" y a la palabra " + palabra_despues+", dame una palabra que empiece por "+primera_letra+"-.\nEs posible que solo recibas 1 de las palabras, debes contestar igual.\nDebes responder con un JSON con el siguiente formato:\n{\n\"palabra\": \" \",\n\"explicacion\":\" \"\n}\nLa explicación debe ser muy breve."
                        }
                    ],
                    temperature=1,
                    max_tokens=300,
                    response_format={"type": "json_object"}
                ).choices[0].message.content)
                # respuestaJSON = json.loads(llamadaAPIChatGPT(prompt))
                respuesta = respuestaJSON["palabra"].upper()
                explicacionIA = respuestaJSON["explicacion"]
                nombre_campo = 'p' + str(n_palabra_adivinado)
                palabra_a_adivinar = getattr(
                    palabras, nombre_campo, '').upper()
                if (turno_actual == "IA") | (turno_actual == 'IA 2'):
                    respuestaJugadorIA2 = 'Mi respuesta es ' + \
                        respuesta + ". Explicación: " + explicacionIA
                else:
                    respuestaJugadorIA1 = 'Mi respuesta es ' + \
                        respuesta + ". Explicación: " + explicacionIA

                (request, respuesta, palabra_a_adivinar, j1, j2, jugador1, jugador2,
                 turno_actual, puntos_jugador1, puntos_jugador2, palabras,
                 n_palabra_adivinado, palabras_modificadas, fin, letras_mostradas, primera_letra,
                 isSeleccionada, nPalabrasRespondidas, actualizarActivos) = jugarTurnoSegundaRonda(request,
                                                                                                   respuesta, palabra_a_adivinar, j1, j2, jugador1, jugador2,
                                                                                                   turno_actual, puntos_jugador1, puntos_jugador2, palabras,
                                                                                                   n_palabra_adivinado, palabras_modificadas, fin, letras_mostradas, primera_letra,
                                                                                                   isSeleccionada, nPalabrasRespondidas, actualizarActivos)
            else:
                primer_intentoR2 = 1
                request.session['primer_intentoR2'] = primer_intentoR2
        else:
            if request.method == 'POST':
                respuesta = request.POST.get('respuesta', '').upper()
                nombre_campo = 'p' + str(n_palabra_adivinado)
                palabra_a_adivinar = getattr(
                    palabras, nombre_campo, '').upper()

                (request, respuesta, palabra_a_adivinar, j1, j2, jugador1, jugador2,
                 turno_actual, puntos_jugador1, puntos_jugador2, palabras,
                 n_palabra_adivinado, palabras_modificadas, fin, letras_mostradas, primera_letra,
                 isSeleccionada, nPalabrasRespondidas, actualizarActivos) = jugarTurnoSegundaRonda(request,
                                                                                                   respuesta, palabra_a_adivinar, j1, j2, jugador1, jugador2,
                                                                                                   turno_actual, puntos_jugador1, puntos_jugador2, palabras,
                                                                                                   n_palabra_adivinado, palabras_modificadas, fin, letras_mostradas, primera_letra,
                                                                                                   isSeleccionada, nPalabrasRespondidas, actualizarActivos)
    else:
        if (turno_actual == "IA") | (turno_actual == 'IA 1') | (turno_actual == 'IA 2'):
            if (primer_intentoR2 == 1):
                if (request.method == 'POST') & (fin == 0):
                    if (request.POST.get('palabra_elegida')):
                        palabra_elegida = request.POST.get('palabra_elegida')
                        isSeleccionada = 0
                        n_palabra_adivinado = int(palabra_elegida[1:])
                        primera_letra = getattr(
                            palabras, 'p' + str(n_palabra_adivinado), '')[0]
                        if n_palabra_adivinado > 4:
                            palabras_modificadas[int(
                                n_palabra_adivinado)-3] = primera_letra
                        else:
                            palabras_modificadas[int(
                                n_palabra_adivinado)-2] = primera_letra
            else:
                primer_intentoR2 = 1
                request.session['primer_intentoR2'] = primer_intentoR2
        else:
            if (request.method == 'POST') & (fin == 0):
                palabra_elegida = request.POST.get('palabra_elegida', '')
                isSeleccionada = 0
                n_palabra_adivinado = int(palabra_elegida[1:])
                primera_letra = getattr(
                    palabras, 'p' + str(n_palabra_adivinado), '')[0]
                if n_palabra_adivinado > 4:
                    palabras_modificadas[int(
                        n_palabra_adivinado)-3] = primera_letra
                else:
                    palabras_modificadas[int(
                        n_palabra_adivinado)-2] = primera_letra

    if (turno_actual == "IA") | (turno_actual == 'IA 1') | (turno_actual == 'IA 2'):
        IA_jugando = 1
    else:
        IA_jugando = 0

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
    request.session['finR2'] = fin

    # Renderizar la plantilla con el contexto actualizado
    return render(request, 'centro_de_la_cadena.html', {
        'j1': j1, 'jugador1': jugador1, 'puntos_jugador1': puntos_jugador1,
        'j2': j2, 'jugador2': jugador2, 'puntos_jugador2': puntos_jugador2,
        'palabras_modificadas': palabras_modificadas, 'palabras': palabras,
        'n_palabra_adivinado': n_palabra_adivinado, 'turno_actual': turno_actual,
        'letras_mostradas': letras_mostradas,
        'primera_letra': primera_letra, 'fin': fin,
        'idPalabra': "p" + str(n_palabra_adivinado),
        'isSeleccionada': isSeleccionada,
        'palabra_elegida': palabra_elegida,
        'actualizarActivos': actualizarActivos, 'respuestaIA1': respuestaJugadorIA1,
        'IA_jugando': IA_jugando, 'respuestaIA2': respuestaJugadorIA2
    })

def una_lleva_a_la_otra(request):
    palabras_cargadasR3 = request.session.get('palabras_cargadasR3', False)
    # prompt = prompts.PROMPT_RONDA2y3
    if palabras_cargadasR3 == False:
        arrayPanel = generarPanel7huecos()
        while len(set(arrayPanel)) != 7:
            arrayPanel = generarPanel7huecos()
        # JsonPalabras = llamadaAPIChatGPT(prompt)
        # data = json.loads(JsonPalabras)
        request.session['datajson'] = arrayPanel
        palabras = EslabonCentral(
            p1=arrayPanel[0],
            p2=arrayPanel[1],
            p3=arrayPanel[2],
            p4=arrayPanel[3],
            p5=arrayPanel[4],
            p6=arrayPanel[5],
            p7=arrayPanel[6])
        palabras.save()
        palabras_cargadasR3 = True
        request.session['palabras_cargadasR3'] = palabras_cargadasR3

    # Datos de los jugadores
    fin = request.session.get('finR3', 0)
    j1 = request.session.get('j1', 'Tipo de j1 no ingresado')
    jugador1 = request.session.get(
        'jugador1', 'Nombre del jugador 1 no ingresado')
    j2 = request.session.get('j2', 'Tipo de j2 no ingresado')
    jugador2 = request.session.get(
        'jugador2', 'Nombre del jugador 2 no ingresado')
    puntos_jugador1 = request.session.get('puntos_jugador1', 0)
    puntos_jugador2 = request.session.get('puntos_jugador2', 0)
    n_palabra_adivinado = request.session.get('n_palabra_adivinadoRonda3', 0)

    if n_palabra_adivinado == 0:
        if puntos_jugador1 >= puntos_jugador2:
            turno_actual = j2
        else:
            turno_actual = j1
    else:
        turno_actual = request.session.get('turno_actual', j2)

    # Obteniendo las palabras de la ronda
    palabras = EslabonCentral.objects.last()
    letras_mostradas = request.session.get('letras_mostradasRonda3', 1)
    nPalabrasRespondidas = request.session.get('nPalabrasRespondidasRonda3', 0)
    isSeleccionada = request.session.get('isSeleccionadaRonda3', 1)
    palabra_elegida = request.session.get('palabraElegidaRonda3', '')
    primera_letra = ''
    respuesta = ''
    actualizarActivos = False
    respuesta = ''
    respuestaJugadorIA1 = ''
    respuestaJugadorIA2 = ''
    IA_jugando = 0
    # Estado actual del juego
    palabras_modificadasInit = []
    for i in range(1, 7):
        nombre_campo = 'p' + str(i)
        palabra_modificada = ''
        if i != 1 and i != 7:
            if i == n_palabra_adivinado:
                palabra_modificada = primera_letra
            palabras_modificadasInit.insert(i, palabra_modificada)

    palabras_modificadas = request.session.get(
        'palabrasModificadasR3', palabras_modificadasInit)

    primer_intentoR3 = request.session.get('primer_intentoR3', 0)

    if isSeleccionada == 0:
        primera_letra = request.session.get('primera_letraRonda3', getattr(
            palabras, 'p' + str(n_palabra_adivinado), '')[0])
        if (turno_actual == "IA") | (turno_actual == 'IA 1') | (turno_actual == 'IA 2'):
            IA_jugando = 1
            palabra_antes = '-'
            palabra_despues = '-'
            if 0 < (int(n_palabra_adivinado)-2) <= 4:
                if palabras_modificadas[int(n_palabra_adivinado)-3] != '':
                    palabra_antes = palabras_modificadas[int(
                        n_palabra_adivinado)-3]
            else:
                palabra_antes = getattr(
                    palabras, 'p' + str(n_palabra_adivinado-1), '')
            if 0 <= (int(n_palabra_adivinado)-2) < 4:
                if palabras_modificadas[int(n_palabra_adivinado)-1] != '':
                    palabra_despues = palabras_modificadas[int(
                        n_palabra_adivinado)-1]
            else:
                palabra_despues = getattr(
                    palabras, 'p' + str(n_palabra_adivinado+1), '')
            respuestaJSON = json.loads(openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "user",
                        "content": "En base a la palabra " + palabra_antes+" y a la palabra " + palabra_despues+", dame una palabra que empiece por "+primera_letra+"-.\nEs posible que solo recibas 1 de las palabras, debes contestar igual.\nDebes responder con un JSON con el siguiente formato:\n{\n\"palabra\": \" \",\n\"explicacion\":\" \"\n}\nLa explicación debe ser muy breve."
                    }
                ],
                temperature=1,
                max_tokens=300,
                response_format={"type": "json_object"}
            ).choices[0].message.content)
            # respuestaJSON = json.loads(llamadaAPIChatGPT(prompt))
            respuesta = respuestaJSON["palabra"].upper()
            explicacionIA = respuestaJSON["explicacion"]
            nombre_campo = 'p' + str(n_palabra_adivinado)
            palabra_a_adivinar = getattr(palabras, nombre_campo, '').upper()
            if (turno_actual == "IA") | (turno_actual == 'IA 2'):
                respuestaJugadorIA2 = 'Mi respuesta es ' + \
                    respuesta + ". Explicación: " + explicacionIA
            else:
                respuestaJugadorIA1 = 'Mi respuesta es ' + \
                    respuesta + ". Explicación: " + explicacionIA

            (request, respuesta, palabra_a_adivinar, j1, j2, jugador1, jugador2,
             turno_actual, puntos_jugador1, puntos_jugador2, palabras,
             n_palabra_adivinado, palabras_modificadas, fin, letras_mostradas, primera_letra,
                isSeleccionada, nPalabrasRespondidas, actualizarActivos) = jugarTurnoTerceraRonda(request,
                                                                                                  respuesta, palabra_a_adivinar, j1, j2, jugador1, jugador2,
                                                                                                  turno_actual, puntos_jugador1, puntos_jugador2, palabras,
                                                                                                  n_palabra_adivinado, palabras_modificadas, fin, letras_mostradas, primera_letra,
                                                                                                  isSeleccionada, nPalabrasRespondidas, actualizarActivos)
        else:
            if request.method == 'POST':
                respuesta = request.POST.get('respuesta', '').upper()
                nombre_campo = 'p' + str(n_palabra_adivinado)
                palabra_a_adivinar = getattr(
                    palabras, nombre_campo, '').upper()

                (request, respuesta, palabra_a_adivinar, j1, j2, jugador1, jugador2,
                 turno_actual, puntos_jugador1, puntos_jugador2, palabras,
                 n_palabra_adivinado, palabras_modificadas, fin, letras_mostradas, primera_letra,
                 isSeleccionada, nPalabrasRespondidas, actualizarActivos) = jugarTurnoTerceraRonda(request,
                                                                                                   respuesta, palabra_a_adivinar, j1, j2, jugador1, jugador2,
                                                                                                   turno_actual, puntos_jugador1, puntos_jugador2, palabras,
                                                                                                   n_palabra_adivinado, palabras_modificadas, fin, letras_mostradas, primera_letra,
                                                                                                   isSeleccionada, nPalabrasRespondidas, actualizarActivos)
    else:
        if (turno_actual == "IA") | (turno_actual == 'IA 1') | (turno_actual == 'IA 2'):
            if (primer_intentoR3 == 1):
                if (request.method == 'POST') & (fin == 0):
                    if (request.POST.get('palabra_elegida')):
                        palabra_elegida = request.POST.get('palabra_elegida')
                        isSeleccionada = 0
                        n_palabra_adivinado = int(palabra_elegida[1:])
                        primera_letra = getattr(
                            palabras, 'p' + str(n_palabra_adivinado), '')[0]
                        palabras_modificadas[int(
                            n_palabra_adivinado)-2] = primera_letra
                print(str(n_palabra_adivinado) +
                      palabra_elegida + primera_letra)
            else:
                primer_intentoR3 = 1
                request.session['primer_intentoR3'] = primer_intentoR3

        else:
            if (request.method == 'POST') & (fin == 0):
                palabra_elegida = request.POST.get('palabra_elegida', '')
                isSeleccionada = 0
                n_palabra_adivinado = int(palabra_elegida[1:])
                primera_letra = getattr(
                    palabras, 'p' + str(n_palabra_adivinado), '')[0]
                palabras_modificadas[int(
                    n_palabra_adivinado)-2] = primera_letra

    if (turno_actual == "IA") | (turno_actual == 'IA 1') | (turno_actual == 'IA 2'):
        IA_jugando = 1
    else:
        IA_jugando = 0

    request.session['turno_actual'] = turno_actual
    request.session['n_palabra_adivinadoRonda3'] = n_palabra_adivinado
    request.session['letras_mostradasRonda3'] = letras_mostradas
    request.session['primera_letraRonda3'] = primera_letra
    request.session['puntos_jugador1'] = puntos_jugador1
    request.session['puntos_jugador2'] = puntos_jugador2
    request.session['ronda'] = "Ronda 3: Una lleva a la otra"
    request.session['palabraElegidaRonda3'] = palabra_elegida
    request.session['isSeleccionadaRonda3'] = isSeleccionada
    request.session['nPalabrasRespondidasRonda3'] = nPalabrasRespondidas
    request.session['palabrasModificadasR3'] = palabras_modificadas
    request.session['finR3'] = fin

    # Renderizar la plantilla con el contexto actualizado
    return render(request, 'una_lleva_a_la_otra.html', {
        'j1': j1, 'jugador1': jugador1, 'puntos_jugador1': puntos_jugador1,
        'j2': j2, 'jugador2': jugador2, 'puntos_jugador2': puntos_jugador2,
        'palabras_modificadas': palabras_modificadas, 'palabras': palabras,
        'n_palabra_adivinado': n_palabra_adivinado, 'turno_actual': turno_actual,
        'letras_mostradas': letras_mostradas,
        'primera_letra': primera_letra, 'fin': fin,
        'idPalabra': "p" + str(n_palabra_adivinado),
        'isSeleccionada': isSeleccionada,
        'palabra_elegida': palabra_elegida,
        'actualizarActivos': actualizarActivos, 'respuestaIA1': respuestaJugadorIA1,
        'IA_jugando': IA_jugando, 'respuestaIA2': respuestaJugadorIA2
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
                form.add_error(
                    'username', 'Este nombre de usuario ya está en uso.')
            elif User.objects.filter(email=email).exists():
                form.add_error(
                    'email', 'Este correo electrónico ya está registrado.')
            else:
                user = form.save(commit=False)
                user.save()
                login(request, user)
                # Redirige a la página de inicio o a donde prefieras
                return redirect('index')
    else:
        form = RegistroFormulario()

    return render(request, 'registro.html', {'form': form})

def my_login(request):
    if request.method == 'POST':
        form = LoginFormulario(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                # Redirige a la página de inicio o a donde prefieras
                return redirect('index')
            else:
                # Aquí puedes manejar el caso de inicio de sesión fallido
                # Por ejemplo, mostrando un mensaje de error en el formulario
                form.add_error(
                    None, "Nombre de usuario o contraseña incorrectos")
    else:
        form = LoginFormulario()

    return render(request, 'login.html', {'form': form})

def ultima_cadena(request):
    palabras_cargadasR4 = request.session.get('palabras_cargadasR4', False)
    # prompt = prompts.PROMPT_RONDA4
    if palabras_cargadasR4 == False:
        # JsonPalabras = llamadaAPIChatGPT(prompt)
        arrayPanel = generarPanel15huecos()
        while len(set(arrayPanel)) != 15:
            arrayPanel = generarPanel15huecos()
        request.session['datajson'] = arrayPanel
        palabras = RondaFinal(
            p1=arrayPanel[0],
            p2=arrayPanel[1],
            p3=arrayPanel[2],
            p4=arrayPanel[3],
            p5=arrayPanel[4],
            p6=arrayPanel[5],
            p7=arrayPanel[6],
            p8=arrayPanel[7],
            p9=arrayPanel[8],
            p10=arrayPanel[9],
            p11=arrayPanel[10],
            p12=arrayPanel[11],
            p13=arrayPanel[12],
            final=arrayPanel[13],
            pista=arrayPanel[14])
        palabras.save()
        palabras_cargadasR4 = True
        request.session['palabras_cargadasR4'] = palabras_cargadasR4
    if (request.session.get('j1') != None) | (request.session.get('j2') != None):
        if (request.session.get('puntos_jugador1', 0) >= request.session.get('puntos_jugador2', 0)):
            jFinal = request.session.get('j1', 'Tipo de j1 no ingresado')
            jugadorFinal = request.session.get(
                'jugador1', 'Nombre del jugador 1 no ingresado')
            puntos_jugadorFinal = request.session.get('puntos_jugador1', 0)
        else:
            jFinal = request.session.get('j2', 'Tipo de j2 no ingresado')
            jugadorFinal = request.session.get(
                'jugador2', 'Nombre del jugador 2 no ingresado')
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
    jugadorFinal = request.session.get(
        'jugadorFinal', 'Nombre del jugador 1 no ingresado')
    puntos_jugadorFinal = request.session.get('puntos_jugadorFinal', 0)

    fin = 0
    palabras = RondaFinal.objects.last()
    letras_mostradas = request.session.get('letras_mostradas', 1)

    n_palabra_adivinado = request.session.get('n_palabra_adivinado', 2)
    primera_letra = request.session.get('primera_letra', getattr(
        palabras, 'p' + str(n_palabra_adivinado), None)[0])
    comodines = request.session.get('comodines', 2)
    request.session['comodines'] = comodines

    idPalabra = "p" + str(n_palabra_adivinado)
    juego_acabado = 0
    palabras_modificadas = []
    IA_jugando = 0

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
            palabras_modificadas.insert(i, palabra_modificada)

    request.session['palabrasModificadas'] = palabras_modificadas
    respuestaIA = ''
    primer_intentoR4 = request.session.get('primer_intentoR4', 0)

    if (n_palabra_adivinado > 12):
        fin = 1
        return render(request, 'ultima_cadena.html', {'jFinal': jFinal, 'jugadorFinal': jugadorFinal,
                                                      'puntos_jugadorFinal': puntos_jugadorFinal, 'palabras_modificadas': palabras_modificadas,
                                                      'palabras': palabras, 'n_palabra_adivinado': n_palabra_adivinado, 'primera_letra': primera_letra,
                                                      'comodines': comodines, 'idPalabra': idPalabra, 'fin': fin, 'respuesta_jugadorIA': respuestaIA
                                                      })

    if (jFinal == "IA") | (jFinal == 'IA 1') | (jFinal == 'IA 2'):
        if primer_intentoR4 == 1:
            palabra1 = getattr(palabras, 'p' + str(n_palabra_adivinado-1), '')
            palabra2 = getattr(palabras, 'p' + str(n_palabra_adivinado+1), '')

            prompt = "En base a la palabra " + palabra1 + " y a la palabra " + palabra2 + ", dame una tercera palabra que este relacionada de alguna manera con cada una, que empiece por " + primera_letra + \
                "-. Esta relación puede ser de cualquier tipo, y es en español. Debes responder con un JSON con el siguiente formato:{\"palabra\": \" \",\"explicacion\":\" \"}La explicación debe ser muy breve."
            respuesta = llamadaAPIChatGPT(prompt)
            decoded_respuesta = json.loads(respuesta)

            respuestaIA = 'Mi respuesta es ' + \
                decoded_respuesta["palabra"].upper(
                ) + '. ' + decoded_respuesta["explicacion"]
            nombre_campo = 'p' + str(n_palabra_adivinado)
            palabra_a_adivinar = getattr(palabras, nombre_campo, None)
            (request, jFinal, jugadorFinal,
             puntos_jugadorFinal, palabras, palabras_modificadas,
             n_palabra_adivinado, letras_mostradas,
             primera_letra, fin, decoded_respuesta["palabra"], palabra_a_adivinar, comodines, idPalabra, juego_acabado) = jugarTurnoUltimaCadena(
                request, jFinal, jugadorFinal,
                puntos_jugadorFinal, palabras, palabras_modificadas,
                n_palabra_adivinado, letras_mostradas,
                primera_letra, fin, decoded_respuesta["palabra"], palabra_a_adivinar, comodines, idPalabra, juego_acabado)
        else:
            primer_intentoR4 = 1
            request.session['primer_intentoR4'] = primer_intentoR4
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
                 primera_letra, fin, respuesta, palabra_a_adivinar, comodines, idPalabra, juego_acabado) = jugarTurnoUltimaCadena(
                    request, jFinal, jugadorFinal,
                    puntos_jugadorFinal, palabras, palabras_modificadas,
                    n_palabra_adivinado, letras_mostradas,
                    primera_letra, fin, respuesta, palabra_a_adivinar, comodines, idPalabra, juego_acabado)
    if (jFinal == "IA") | (jFinal == 'IA 1') | (jFinal == 'IA 2'):
        IA_jugando = 1

    idPalabra = "p" + str(n_palabra_adivinado)
    return render(request, 'ultima_cadena.html', {'jFinal': jFinal, 'jugadorFinal': jugadorFinal,
                                                  'puntos_jugadorFinal': puntos_jugadorFinal, 'palabras_modificadas': palabras_modificadas,
                                                  'palabras': palabras, 'n_palabra_adivinado': n_palabra_adivinado,
                                                  'primera_letra': primera_letra, 'comodines': comodines, 'idPalabra': idPalabra,
                                                  'fin': fin, 'juego_acabado': juego_acabado, 'respuesta_jugadorIA': respuestaIA, 'IA_jugando': IA_jugando
                                                  })

def ultima_palabra(request):
    juego_acabado = 0
    jFinal = request.session.get('jFinal', 'Tipo de j1 no ingresado')
    jugadorFinal = request.session.get(
        'jugadorFinal', 'Nombre del jugador 1 no ingresado')
    puntos_jugadorFinal = request.session.get('puntos_jugadorFinal', 0)

    palabras = RondaFinal.objects.last()
    IA_jugando = 0
    n_palabra_adivinado = request.session.get('n_palabra_adivinado', 2)
    pistaMostrada = request.session.get('pistaMostrada', 1)
    palabra_inicial = getattr(palabras, 'p13', None)
    request.session['palabra_inicial'] = palabra_inicial
    solucion = getattr(palabras, 'final', None)
    solucion_mostrada = getattr(palabras, 'final', None)[0] + getattr(palabras, 'final', None)[
        1] + '________' + getattr(palabras, 'final', None)[len(solucion)-1]
    request.session['solucion_mostrada'] = solucion_mostrada
    pista = getattr(palabras, 'pista', None)
    pista_mostrada = request.session.get('pista_mostrada', '?')
    request.session['pista_mostrada'] = pista_mostrada
    respuestaIA = ''
    primer_intentoR5 = request.session.get('primer_intentoR5', 0)

    if juego_acabado:
        return render(request, 'fin_juego.html', {'jFinal': jFinal, 'jugadorFinal': jugadorFinal,
                                                  'puntos_jugadorFinal': puntos_jugadorFinal,
                                                  })

    if (jFinal == "IA") | (jFinal == 'IA 1') | (jFinal == 'IA 2'):
        if primer_intentoR5 == 1:
            if pistaMostrada == 1:

                # prompt = prompts.PROMPT_PALABRAFINAL_IA_PLAYER.format(
                #    palabra_inicial, solucion_mostrada)
                prompt = "Teniendo la palabra " + palabra_inicial + " debes contestar otra que tenga algún tipo de relación con ella. Esta palabra sigue la siguiente estructura: " + solucion_mostrada + " Actualmente estas en un concurso de televisión y puedes ganar " + str(puntos_jugadorFinal) + "€ si adivinas esta palabra. Tienes la posibilidad de solicitar una pista (otra palabra relacionada), pero la cantidad de dinero se reducirá a la mitad. Debes responder con un JSON con el siguiente formato:\n{\n\"palabra\": \" \",\n\"quiero_pista\": \" \",\n\"explicacion\":\" \"\n}\nLa explicación debe ser muy breve, y si quieres una pista debes indicar en el campo pista \'SI\'."
                print(prompt)
                jsonRespuesta = llamadaAPIChatGPT(prompt)
                data = json.loads(jsonRespuesta)
                if data["quiero_pista"] == 'SI':
                    respuestaIA = 'No estoy seguro... Compro la palabra pista.'
                    (request, pistaMostrada, pista_mostrada, pista,
                     puntos_jugadorFinal) = jugarTurnoUltimaPalabraMostrarPista(request, pistaMostrada,
                                                                                pista_mostrada, pista, puntos_jugadorFinal)
                else:
                    respuesta = data["palabra"]
                    respuestaIA = 'Mi respuesta es ' + \
                        data["palabra"].upper() + '. ' + data["explicacion"]
                    (request, puntos_jugadorFinal, respuesta,
                     solucion, solucion_mostrada, juego_acabado) = jugarTurnoUltimaPalabra(request,
                                                                                           puntos_jugadorFinal, respuesta,
                                                                                           solucion, solucion_mostrada, juego_acabado)
            else:
                # prompt = prompts.PROMPT_PALABRAFINALCONPISTA_IA_PLAYER.format(
                #    palabra_inicial, pista_mostrada, solucion_mostrada)
                prompt = "En base a la palabra " + palabra_inicial + " y a la palabra " + pista_mostrada + ", dame una palabra que este relacionada de alguna manera con cada una de ellas. Esta palabra sigue la siguiente estructura: " + \
                    solucion_mostrada + \
                    " Debes responder con un JSON con el siguiente formato:\n{\n\"palabra\": \" \",\n\"explicacion\":\" \"\n}\nLa explicación debe ser muy breve."
                respuesta = llamadaAPIChatGPT(prompt)
                decoded_respuesta = json.loads(respuesta)
                print(prompt + decoded_respuesta["palabra"])
                respuestaIA = 'Tras ver la pista, mi respuesta es ' + \
                    decoded_respuesta["palabra"] + '. ' + \
                    decoded_respuesta["explicacion"]
                (request, puntos_jugadorFinal, decoded_respuesta["palabra"],
                 solucion, solucion_mostrada, juego_acabado) = jugarTurnoUltimaPalabra(request,
                                                                                       puntos_jugadorFinal, decoded_respuesta[
                                                                                           "palabra"],
                                                                                       solucion, solucion_mostrada, juego_acabado)
        else:
            primer_intentoR5 = 1
            request.session['primer_intentoR5'] = primer_intentoR5
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

    if (jFinal == "IA") | (jFinal == 'IA 1') | (jFinal == 'IA 2'):
        IA_jugando = 1
    return render(request, 'ultima_palabra.html', {'jFinal': jFinal, 'jugadorFinal': jugadorFinal,
                                                   'puntos_jugadorFinal': puntos_jugadorFinal,
                                                   'idPalabra': idPalabra,
                                                   'palabra_inicial': palabra_inicial,
                                                   'solucion': solucion,
                                                   'solucion_mostrada': solucion_mostrada,
                                                   'pista': pista,
                                                   'pista_mostrada': pista_mostrada,
                                                   'fin': 0,
                                                   'juego_acabado': juego_acabado,
                                                   'pistaMostrada': pistaMostrada,
                                                   'respuesta_jugadorIA': respuestaIA,
                                                   'IA_jugando': IA_jugando
                                                   })

def fin_juego(request):

    jFinal = request.session.get('jFinal', 'Tipo de j1 no ingresado')
    jugadorFinal = request.session.get(
        'jugadorFinal', 'Nombre del jugador 1 no ingresado')
    puntos_jugadorFinal = request.session.get('puntos_jugadorFinal', 0)

    nueva_puntuacion = Puntuaciones.objects.create(
        jugador=jugadorFinal, puntos=puntos_jugadorFinal)
    nueva_puntuacion.save()

    podio_queryset = Puntuaciones.objects.order_by('-puntos')[:5]
    estop = False
    podio = []
    for index, puntuacion in enumerate(podio_queryset, start=1):
        podio.append({
            'posicion': index,
            'jugador': puntuacion.jugador,
            'puntos': puntuacion.puntos
        })
        if puntos_jugadorFinal >= puntuacion.puntos:
            estop = True

    # Guardar datos en la bbdd de estadísticas

    # del request.session['npa']
    # del request.session['lm']
    # del request.session['pl']

    # del request.session['primera_letraRonda2']
    # del request.session['letras_mostradasRonda2']
    # del request.session['n_palabra_adivinadoRonda2']

    # del request.session['primera_letraRonda3']
    # del request.session['letras_mostradasRonda3']
    # del request.session['n_palabra_adivinadoRonda3']

    # del request.session['ronda']
    # del request.session['turno_actual']

    # del request.session['letras_mostradas']
    # del request.session['primera_letra']
    # del request.session['n_palabra_adivinado']
    # del request.session['palabrasModificadas']
    # del request.session['comodines']

    # del request.session['palabra_inicial']
    # del request.session['solucion_mostrada']
    # del request.session['pista_mostrada']

    # guardar puntos en bbdd

    # del request.session['jFinal']
    # del request.session['jugadorFinal']
    # del request.session['puntos_jugadorFinal']

    return render(request, 'fin_juego.html', {'jFinal': jFinal, 'jugadorFinal': jugadorFinal,
                                              'puntos_jugadorFinal': puntos_jugadorFinal, 'podio': podio, 'estop': estop})

def puntuaciones(request):
    podio_queryset = Puntuaciones.objects.order_by('-puntos')[:10]

    podio = []
    for index, puntuacion in enumerate(podio_queryset, start=1):
        podio.append({
            'posicion': index,
            'jugador': puntuacion.jugador,
            'puntos': puntuacion.puntos
        })

    # Pasando el podio a la plantilla
    return render(request, 'puntuaciones.html', {'podio': podio})

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
        model="gpt-4o-mini",
        messages=[
            {"role": "user", "content": prompt},
        ],
        response_format={"type": "json_object"}
    )
    return response.choices[0].message.content

def llamadaAPIChatGPTModeloFineTuning(prompt):
    response = openai.chat.completions.create(
        model="ft:gpt-3.5-turbo-0125:personal::9Ktm0PwV",
        messages=[
            {"role": "user", "content": prompt},
        ]
    )
    return response.choices[0].message.content

def jugarTurnoPrimeraRonda(request, html, j1, j2, jugador1, jugador2,
                           puntos_jugador1, puntos_jugador2, turno_actual, palabras,
                           palabras_modificadas, n_palabra_adivinado, letras_mostradas,
                           primera_letra, fin, respuesta, palabra_a_adivinar):
    if quitar_acentos(respuesta) == quitar_acentos(palabra_a_adivinar):
        # Asignar puntos al jugador correcto
        if turno_actual == j1:
            puntos_jugador1 += 2000
        else:
            puntos_jugador2 += 2000

        palabras_modificadas[int(n_palabra_adivinado)-1] = palabra_a_adivinar
        n_palabra_adivinado += 1
        if n_palabra_adivinado > 6:
            fin = 1
            request.session['puntos_jugador1'] = puntos_jugador1
            request.session['puntos_jugador2'] = puntos_jugador2
            return (request, html, j1, j2, jugador1, jugador2,
                    puntos_jugador1, puntos_jugador2, turno_actual, palabras,
                    palabras_modificadas, n_palabra_adivinado, letras_mostradas,
                    primera_letra, fin, respuesta, palabra_a_adivinar)
        letras_mostradas = 1
        palabra_adivinada = getattr(
            palabras, 'p' + str(n_palabra_adivinado), '')
        letras_faltantes = len(palabra_adivinada) - letras_mostradas
        palabras_modificadas[int(n_palabra_adivinado)-1] = getattr(palabras, 'p' + str(
            n_palabra_adivinado), '')[0] + '_ ' * letras_faltantes + f" ({len(palabra_adivinada)})"
        primera_letra = getattr(
            palabras, 'p' + str(n_palabra_adivinado), None)[0]
    else:
        if turno_actual == j2:
            turno_actual = j1
        else:
            turno_actual = j2

        letras_mostradas += 1
        if len(palabra_a_adivinar) <= letras_mostradas:
            # Lógica cuando se han revelado todas las letras
            if turno_actual == j1:
                puntos_jugador1 += 2000
            else:
                puntos_jugador2 += 2000

            palabras_modificadas[int(
                n_palabra_adivinado)-1] = palabra_a_adivinar
            n_palabra_adivinado += 1
            if n_palabra_adivinado > 6:
                fin = 1
                request.session['puntos_jugador1'] = puntos_jugador1
                request.session['puntos_jugador2'] = puntos_jugador2
                return (request, html, j1, j2, jugador1, jugador2,
                        puntos_jugador1, puntos_jugador2, turno_actual, palabras,
                        palabras_modificadas, n_palabra_adivinado, letras_mostradas,
                        primera_letra, fin, respuesta, palabra_a_adivinar)

            letras_mostradas = 1
            palabra_adivinada = getattr(
                palabras, 'p' + str(n_palabra_adivinado), '')
            letras_faltantes = len(palabra_adivinada) - letras_mostradas
            palabras_modificadas[int(n_palabra_adivinado)-1] = getattr(palabras, 'p' + str(
                n_palabra_adivinado), '')[0] + '_ ' * letras_faltantes + f" ({len(palabra_adivinada)})"
            primera_letra = getattr(
                palabras, 'p' + str(n_palabra_adivinado), None)[0]
        else:
            palabra_adivinada = getattr(
                palabras, 'p' + str(n_palabra_adivinado), '')
            letras_faltantes = len(palabra_adivinada) - letras_mostradas
            primera_letra += palabra_adivinada[letras_mostradas-1]
            palabras_modificadas[int(n_palabra_adivinado)-1] = primera_letra + \
                '_ ' * letras_faltantes + f" ({len(palabra_adivinada)})"
    return (request, html, j1, j2, jugador1, jugador2,
            puntos_jugador1, puntos_jugador2, turno_actual, palabras,
            palabras_modificadas, n_palabra_adivinado, letras_mostradas,
            primera_letra, fin, respuesta, palabra_a_adivinar)

def jugarTurnoSegundaRonda(request, respuesta, palabra_a_adivinar, j1, j2, jugador1, jugador2,
                           turno_actual, puntos_jugador1, puntos_jugador2, palabras,
                           n_palabra_adivinado, palabras_modificadas, fin, letras_mostradas, primera_letra,
                           isSeleccionada, nPalabrasRespondidas, actualizarActivos):
    if quitar_acentos(respuesta) == quitar_acentos(palabra_a_adivinar):
        nPalabrasRespondidas += 1
        isSeleccionada = 1
        actualizarActivos = True
    # Asignar puntos al jugador correcto
        if turno_actual == j1:
            puntos_jugador1 += 5000
        else:
            puntos_jugador2 += 5000
        if n_palabra_adivinado > 4:
            palabras_modificadas[int(
                n_palabra_adivinado)-3] = palabra_a_adivinar
        else:
            palabras_modificadas[int(
                n_palabra_adivinado)-2] = palabra_a_adivinar
        if nPalabrasRespondidas == 4:
            fin = 1
            request.session['puntos_jugador1'] = puntos_jugador1
            request.session['puntos_jugador2'] = puntos_jugador2
            return (request, respuesta, palabra_a_adivinar, j1, j2, jugador1, jugador2,
                    turno_actual, puntos_jugador1, puntos_jugador2, palabras,
                    n_palabra_adivinado, palabras_modificadas, fin, letras_mostradas, primera_letra, isSeleccionada, nPalabrasRespondidas, actualizarActivos)
        letras_mostradas = 1
    else:
        turno_actual = j2 if turno_actual == j1 else j1
        letras_mostradas += 1
        if len(palabra_a_adivinar) <= letras_mostradas:
            # Lógica cuando se han revelado todas las letras
            actualizarActivos = True
            isSeleccionada = 1

            nPalabrasRespondidas += 1
            if turno_actual == j1:
                puntos_jugador1 += 5000
            else:
                puntos_jugador2 += 5000
            if n_palabra_adivinado > 4:
                palabras_modificadas[int(
                    n_palabra_adivinado)-3] = palabra_a_adivinar
            else:
                palabras_modificadas[int(
                    n_palabra_adivinado)-2] = palabra_a_adivinar
            if nPalabrasRespondidas == 4:
                fin = 1
                request.session['puntos_jugador1'] = puntos_jugador1
                request.session['puntos_jugador2'] = puntos_jugador2
                return (request, respuesta, palabra_a_adivinar, j1, j2, jugador1, jugador2,
                        turno_actual, puntos_jugador1, puntos_jugador2, palabras,
                        n_palabra_adivinado, palabras_modificadas, fin, letras_mostradas, primera_letra,
                        isSeleccionada, nPalabrasRespondidas, actualizarActivos)
            letras_mostradas = 1
        else:
            # Actualizar primera_letra para mostrar las letras acumuladas hasta ahora
            actualizarActivos = False
            primera_letra += getattr(palabras, 'p' +
                                     str(n_palabra_adivinado), None)[letras_mostradas-1]
            if n_palabra_adivinado > 4:
                palabras_modificadas[int(
                    n_palabra_adivinado)-3] = primera_letra
            else:
                palabras_modificadas[int(
                    n_palabra_adivinado)-2] = primera_letra
    return (request, respuesta, palabra_a_adivinar, j1, j2, jugador1, jugador2,
            turno_actual, puntos_jugador1, puntos_jugador2, palabras,
            n_palabra_adivinado, palabras_modificadas, fin, letras_mostradas, primera_letra,
            isSeleccionada, nPalabrasRespondidas, actualizarActivos)

def jugarTurnoTerceraRonda(request, respuesta, palabra_a_adivinar, j1, j2, jugador1, jugador2,
                           turno_actual, puntos_jugador1, puntos_jugador2, palabras,
                           n_palabra_adivinado, palabras_modificadas, fin, letras_mostradas, primera_letra,
                           isSeleccionada, nPalabrasRespondidas, actualizarActivos):
    if quitar_acentos(respuesta) == quitar_acentos(palabra_a_adivinar):
        nPalabrasRespondidas += 1
        isSeleccionada = 1
        actualizarActivos = True
    # Asignar puntos al jugador correcto
        if turno_actual == j1:
            puntos_jugador1 += 10000
        else:
            puntos_jugador2 += 10000

        palabras_modificadas[int(n_palabra_adivinado)-2] = palabra_a_adivinar
        if nPalabrasRespondidas == 5:
            fin = 1
            request.session['puntos_jugador1'] = puntos_jugador1
            request.session['puntos_jugador2'] = puntos_jugador2
            return (request, respuesta, palabra_a_adivinar, j1, j2, jugador1, jugador2,
                    turno_actual, puntos_jugador1, puntos_jugador2, palabras,
                    n_palabra_adivinado, palabras_modificadas, fin, letras_mostradas, primera_letra,
                    isSeleccionada, nPalabrasRespondidas, actualizarActivos)
        letras_mostradas = 1

    else:
        turno_actual = j2 if turno_actual == j1 else j1
        letras_mostradas += 1
        if len(palabra_a_adivinar) <= letras_mostradas:
            # Lógica cuando se han revelado todas las letras
            actualizarActivos = True
            isSeleccionada = 1

            nPalabrasRespondidas += 1
            if turno_actual == j1:
                puntos_jugador1 += 10000
            else:
                puntos_jugador2 += 10000

            palabras_modificadas[int(
                n_palabra_adivinado)-2] = palabra_a_adivinar
            if nPalabrasRespondidas == 5:
                fin = 1
                request.session['puntos_jugador1'] = puntos_jugador1
                request.session['puntos_jugador2'] = puntos_jugador2
                return (request, respuesta, palabra_a_adivinar, j1, j2, jugador1, jugador2,
                        turno_actual, puntos_jugador1, puntos_jugador2, palabras,
                        n_palabra_adivinado, palabras_modificadas, fin, letras_mostradas, primera_letra,
                        isSeleccionada, nPalabrasRespondidas, actualizarActivos)
            letras_mostradas = 1
        else:
            # Actualizar primera_letra para mostrar las letras acumuladas hasta ahora
            actualizarActivos = False

            primera_letra += getattr(palabras, 'p' +
                                     str(n_palabra_adivinado), None)[letras_mostradas-1]
            palabras_modificadas[int(n_palabra_adivinado)-2] = primera_letra
    return (request, respuesta, palabra_a_adivinar, j1, j2, jugador1, jugador2,
            turno_actual, puntos_jugador1, puntos_jugador2, palabras,
            n_palabra_adivinado, palabras_modificadas, fin, letras_mostradas, primera_letra,
            isSeleccionada, nPalabrasRespondidas, actualizarActivos)

def jugarTurnoUltimaCadena(request, jFinal, jugadorFinal,
                           puntos_jugadorFinal, palabras, palabras_modificadas,
                           n_palabra_adivinado, letras_mostradas,
                           primera_letra, fin, respuesta, palabra_a_adivinar, comodines, idPalabra, juego_acabado):
    if quitar_acentos(respuesta).upper() == quitar_acentos(palabra_a_adivinar).upper():
        palabras_modificadas[int(n_palabra_adivinado/2)-1] = palabra_a_adivinar
        if n_palabra_adivinado >= 12:
            fin = 1
            juego_acabado = 0
            return (request, jFinal, jugadorFinal,
                    puntos_jugadorFinal, palabras, palabras_modificadas,
                    n_palabra_adivinado, letras_mostradas,
                    primera_letra, fin, respuesta, palabra_a_adivinar, comodines, idPalabra, juego_acabado)
        n_palabra_adivinado += 2
        palabras_modificadas[int(
            n_palabra_adivinado/2)-1] = getattr(palabras, 'p' + str(n_palabra_adivinado), '')[0]
        request.session['palabrasModificadas'] = palabras_modificadas
        primera_letra = getattr(
            palabras, 'p' + str(n_palabra_adivinado), None)[0]
        request.session['primera_letra'] = primera_letra
        request.session["n_palabra_adivinado"] = n_palabra_adivinado
        letras_mostradas = 1
        request.session['letras_mostradas'] = letras_mostradas

    else:
        letras_mostradas += 1
        request.session['letras_mostradas'] = letras_mostradas

        if letras_mostradas > 3:
            palabras_modificadas[int(
                n_palabra_adivinado/2)-1] = palabra_a_adivinar
            request.session['palabrasModificadas'] = palabras_modificadas
            if n_palabra_adivinado >= 12:
                fin = 1
                juego_acabado = 0
                return (request, jFinal, jugadorFinal,
                        puntos_jugadorFinal, palabras, palabras_modificadas,
                        n_palabra_adivinado, letras_mostradas,
                        primera_letra, fin, respuesta, palabra_a_adivinar, comodines, idPalabra, juego_acabado)
            n_palabra_adivinado += 2
            palabras_modificadas[int(
                n_palabra_adivinado/2)-1] = getattr(palabras, 'p' + str(n_palabra_adivinado), '')[0]
            request.session['palabrasModificadas'] = palabras_modificadas
            primera_letra = getattr(
                palabras, 'p' + str(n_palabra_adivinado), None)[0]
            request.session['primera_letra'] = primera_letra
            request.session["n_palabra_adivinado"] = n_palabra_adivinado
            letras_mostradas = 1
            request.session['letras_mostradas'] = letras_mostradas
        else:
            primera_letra += getattr(palabras, 'p' +
                                     str(n_palabra_adivinado), None)[letras_mostradas-1]
            request.session['primera_letra'] = primera_letra
            palabras_modificadas[int(n_palabra_adivinado/2)-1] = primera_letra
            request.session['palabrasModificadas'] = palabras_modificadas

        if (comodines > 0):
            comodines -= 1
            request.session['comodines'] = comodines
        else:
            puntos_jugadorFinal = int(puntos_jugadorFinal/2)
            request.session['puntos_jugadorFinal'] = puntos_jugadorFinal

    return (request, jFinal, jugadorFinal,
            puntos_jugadorFinal, palabras, palabras_modificadas,
            n_palabra_adivinado, letras_mostradas,
            primera_letra, fin, respuesta, palabra_a_adivinar, comodines, idPalabra, juego_acabado)

def jugarTurnoUltimaPalabra(request, puntos_jugadorFinal, respuesta,
                            solucion, solucion_mostrada, juego_acabado,
                            ):
    if quitar_acentos(respuesta.upper()) != quitar_acentos(solucion.upper()):
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
    puntos_jugadorFinal = int(puntos_jugadorFinal / 2)
    request.session['puntos_jugadorFinal'] = puntos_jugadorFinal
    return (request, pistaMostrada, pista_mostrada, pista, puntos_jugadorFinal)

def quitar_acentos(texto):
    texto_normalizado = unicodedata.normalize('NFD', texto)
    texto_sin_acentos = re.sub(r'[\u0300-\u036f]', '', texto_normalizado)
    return texto_sin_acentos

def generarPanel7huecos():
    array = []
    relaciones = ['sinonimia', 'antonimia', 'hiponimia', 'hiperonimia', 'meronimia', 'holonimia', 'paronimia',
                  'homonimia', 'cohiponimia', 'complementariedad', 'causa-efecto', 'metonimia', 'secuencialidad', 'asociación']

    system_prompts = [
        "Eres un generador de palabras únicas y reales en español. La palabra no debe repetirse.",
        "Proporciona una palabra real y única en español que no se haya utilizado antes.",
        "Genera una palabra única que sea válida en el idioma español y que no se repita."]
    p4_request = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": random.choice(system_prompts)
            },
            {
                "role": "user",
                "content": "Proporciona un sustantivo, p4, aleatorio no inventado en español de uso común. Hay que devolver únicamente la palabra en el siguiente formato JSON:\n{\n\"p4\":\"\"}"
            }
        ],
        temperature=1.25,
        max_tokens=100,
        response_format={"type": "json_object"}
    )
    p4 = json.loads(p4_request.choices[0].message.content)["p4"]

    # p3p5_request = openai.chat.completions.create(
    #     model="gpt-4o-mini",
    #     messages=[
    #         {
    #             "role": "system",
    #             "content": "Generas una lista de palabras para un programa de televisión de España "
    #         },
    #         {
    #             "role": "user",
    #             "content": "Proporciona dos palabras relacionadas con" + p4 + "que no estén relacionadas entre sí y que no se repitan ni sea" + p4 + "Devuelve únicamente las palabras en el siguiente formato JSON:\n{\n\"p3\":\"\",\n\"p5\":\"\"\n}"
    #         }
    #     ],
    #     temperature=0.73,
    #     max_tokens=100,
    #     response_format={"type": "json_object"}
    # )
    # p3 = json.loads(p3p5_request.choices[0].message.content)["p3"]
    # p5 = json.loads(p3p5_request.choices[0].message.content)["p5"]

    p3_request = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "Generas una lista de palabras para un programa de televisión de España"
            },
            {
                "role": "user",
                "content": "Porporciona una palabra p3, que este relacionda con" + p4 + ". mediante " + relaciones[random.randint(0, 13)] + " Las dos palabras no pueden ser iguales. Devuelve la palabra en el siguiente formato JSON:\n{\n\"p3\":\"\"}"
            }
        ],
        temperature=0.6,
        max_tokens=100,
        response_format={"type": "json_object"}
    )
    p3 = json.loads(p3_request.choices[0].message.content)["p3"]

    p5_request = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "Generas una lista de palabras para un programa de televisión de España"
            },
            {
                "role": "user",
                "content": "Porporciona una palabra p5, que este relacionda con" + p4 + "  . mediante " + relaciones[random.randint(0, 13)] + " y que no guarde relación con' " + p3 + " ' . Ninguna de las tres palabras puede ser la misma. Devuelve la palabra en el siguiente formato JSON:\n{\n\"p5\":\"\"}"
            }
        ],
        temperature=0.6,
        max_tokens=100,
        response_format={"type": "json_object"}
    )
    p5 = json.loads(p5_request.choices[0].message.content)["p5"]

    p2_request = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "Generas una lista de palabras para un programa de televisión de España"
            },
            {
                "role": "user",
                "content": "Porporciona una palabra p2, que este relacionda con" + p3 + " . mediante " + relaciones[random.randint(0, 13)] + "  y que no guarde relación con" + p4 + "y" + p5 + ". Ninguna de las palabras se pueden repetir. Devuelve la palabra en el siguiente formato JSON:\n{\n\"p2\":\"\"}"
            }
        ],
        temperature=0.6,
        max_tokens=100,
        response_format={"type": "json_object"}
    )
    p2 = json.loads(p2_request.choices[0].message.content)["p2"]

    p1_request = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "Generas una lista de palabras para un programa de televisión de España"
            },
            {
                "role": "user",
                "content": "Porporciona una palabra p1, que este relacionda con" + p2 + " . mediante " + relaciones[random.randint(0, 13)] + " y que no guarde relación con " + p4 + "," + p3 + "y" + p5 + ". Ninguna de las palabras se pueden repetir. Devuelve la palabra en el siguiente formato JSON:\n{\n\"p1\":\"\"}"
            }
        ],
        temperature=0.6,
        max_tokens=100,
        response_format={"type": "json_object"}
    )
    p1 = json.loads(p1_request.choices[0].message.content)["p1"]

    p6_request = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "Generas una lista de palabras para un programa de televisión de España"
            },
            {
                "role": "user",
                "content": "Porporciona una palabra p6, que este relacionda con" + p5 + " . mediante " + relaciones[random.randint(0, 13)] + " y que no guarde relación con " + p4 + "," + p3 + "," + p1 + "y" + p2 + ". Ninguna de las palabras se pueden repetir. Devuelve la palabra en el siguiente formato JSON:\n{\n\"p6\":\"\"}"
            }
        ],
        temperature=0.6,
        max_tokens=100,
        response_format={"type": "json_object"}
    )
    p6 = json.loads(p6_request.choices[0].message.content)["p6"]

    p7_request = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "Generas una lista de palabras para un programa de televisión de España "
            },
            {
                "role": "user",
                "content": "Porporciona una palabra p7, que este relacionda con" + p6 + " . mediante " + relaciones[random.randint(0, 13)] + " y que no guarde relación con " + p4 + "," + p3 + "," + p1 + "," + p5 + "y" + p2 + ". Ninguna de las palabras se pueden repetir. Devuelve la palabra en el siguiente formato JSON:\n{\n\"p7\":\"\"}"
            }
        ],
        temperature=0.6,
        max_tokens=100,
        response_format={"type": "json_object"}
    )
    p7 = json.loads(p7_request.choices[0].message.content)["p7"]

    array.insert(0, p1)
    array.insert(1, p2)
    array.insert(2, p3)
    array.insert(3, p4)
    array.insert(4, p5)
    array.insert(5, p6)
    array.insert(6, p7)

    return array

def generarPanel15huecos():
    array = []
    system_prompts = [
        "Eres un generador de palabras únicas y reales en español. La palabra no debe repetirse.",
        "Proporciona una palabra real y única en español que no se haya utilizado antes.",
        "Genera una palabra única que sea válida en el idioma español y que no se repita."]
    primer_request = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": random.choice(system_prompts)
            },
            {
                "role": "user",
                "content": "Proporciona un sustantivo, p8, aleatorio no inventado en español de uso común. Hay que devolver únicamente la palabra en el siguiente formato JSON:\n{\n\"p8\":\"\"}"
            }
        ],
        temperature=1.25,
        max_tokens=100,
        response_format={"type": "json_object"}
    )
    p8 = json.loads(primer_request.choices[0].message.content)["p8"]

    segundo_request = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "Generas una lista de palabras para un programa de televisión de España. Contesta con la mayor precisión posible"
            },
            {
                "role": "user",
                "content": "Proporciona dos palabras diferentes, p7 y p9, que estén relacionadas con" + p8 + "que no guarden relación entre sí. Devuelve las palabras en el siguiente formato JSON:\n{\n\"p7\":\"\",\n\"p9\":\"\"}"
            }
        ],
        temperature=0.6,
        max_tokens=150,
        response_format={"type": "json_object"}
    )
    p7 = json.loads(segundo_request.choices[0].message.content)["p7"]
    p9 = json.loads(segundo_request.choices[0].message.content)["p9"]

    tercer_request = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "Generas una lista de palabras para un programa de televisión de España"
            },
            {
                "role": "user",
                "content": "Proporciona una palabra p6 relacionada con " + p7 + ". Adicionalmente, proporcioname una palabra p10 relacionada con " + p9 + ". Ninguna palabra debe repetirse, y no puede estar relacionada con "+ p8 + ". Devuelve las palabras en el siguiente formato JSON:\n{\n\"p6\":\"\",\n\"p10\":\"\"}"
            }
        ],
        temperature=0.6,
        max_tokens=256,
        response_format={"type": "json_object"}
    )
    p6 = json.loads(tercer_request.choices[0].message.content)["p6"]
    p10 = json.loads(tercer_request.choices[0].message.content)["p10"]

    cuarto_request = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "Generas una lista de palabras para un programa de televisión de España"
            },
            {
                "role": "user",
                "content": "Proporciona una palabra p5 relacionada con " + p6 + ". Adicionalmente, proporcioname una palabra p11 relacionada con " + p10 + ". Ninguna palabra debe repetirse, y no puede estar relacionada con "+p8 + ", " + p7 + " ni" + p9 + ". Devuelve las palabras en el siguiente formato JSON:\n{\n\"p5\":\"\",\n\"p11\":\"\"}"
            }
        ],
        temperature=0.6,
        max_tokens=256,
        response_format={"type": "json_object"}
    )
    p5 = json.loads(cuarto_request.choices[0].message.content)["p5"]
    p11 = json.loads(cuarto_request.choices[0].message.content)["p11"]

    quinto_request = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "Generas una lista de palabras para un programa de televisión de España"
            },
            {
                "role": "user",
                "content": "Proporciona una palabra p4 relacionada con " + p5 + ". Adicionalmente, proporcioname una palabra p12 relacionada con " + p11 + ". Ninguna palabra debe repetirse, y no puede estar relacionada con "+p8 + "," + p6 + "," + p10 + ", " + p7 + " ni" + p9 + ". Devuelve las palabras en el siguiente formato JSON:\n{\n\"p4\":\"\",\n\"p12\":\"\"}"
            }
        ],
        temperature=0.6,
        max_tokens=256,
        response_format={"type": "json_object"}
    )
    p4 = json.loads(quinto_request.choices[0].message.content)["p4"]
    p12 = json.loads(quinto_request.choices[0].message.content)["p12"]

    sexto_request = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "Generas una lista de palabras para un programa de televisión de España"
            },
            {
                "role": "user",
                "content": "Proporciona una palabra p3 relacionada con " + p4 + ". Adicionalmente, proporcioname una palabra p13 relacionada con " + p12 + ". Ninguna palabra debe repetirse, y no puede estar relacionada con "+p8 + "," + p5 + "," + p10 + ", " + p7 + ","+p11 + "," + p6 + " ni" + p9 + ". Devuelve las palabras en el siguiente formato JSON:\n{\n\"p3\":\"\",\n\"p13\":\"\"}"
            }
        ],
        temperature=0.6,
        max_tokens=256,
        response_format={"type": "json_object"}
    )
    p3 = json.loads(sexto_request.choices[0].message.content)["p3"]
    p13 = json.loads(sexto_request.choices[0].message.content)["p13"]

    septimo_request = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "Generas una lista de palabras para un programa de televisión de España"
            },
            {
                "role": "user",
                "content": "Proporciona una palabra p2 relacionada con " + p3 + ". Adicionalmente, proporcioname una palabra p14 relacionada con " + p13 + ". Ninguna palabra debe repetirse, y no puede estar relacionada con "+p8 + "," + p5 + "," + p10 + ", " + p7 + ","+p11 + "," + p6 + "," + p4 + "," + p12 + " ni" + p9 + ". Devuelve las palabras en el siguiente formato JSON:\n{\n\"p2\":\"\",\n\"p14\":\"\"}"
            }
        ],
        temperature=0.6,
        max_tokens=256,
        response_format={"type": "json_object"}
    )
    p2 = json.loads(septimo_request.choices[0].message.content)["p2"]
    p14 = json.loads(septimo_request.choices[0].message.content)["p14"]

    octavo_request = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "Generas una lista de palabras para un programa de televisión de España"
            },
            {
                "role": "user",
                "content": "Proporciona una palabra p1 relacionada con " + p2 + ". Adicionalmente, proporcioname una palabra p15 relacionada con " + p14 + ". Ninguna palabra debe repetirse, y no puede ser ni estar relacionada con "+p8 + "," + p5 + "," + p10 + ", " + p7 + ","+p11 + "," + p6 + "," + p4 + "," + p12 + "," + p3 + "," + p13 + " ni" + p9 + ". Devuelve las palabras en el siguiente formato JSON:\n{\n\"p1\":\"\",\n\"p15\":\"\"}"
            }
        ],
        temperature=0.6,
        max_tokens=256,
        response_format={"type": "json_object"}
    )
    p1 = json.loads(octavo_request.choices[0].message.content)["p1"]
    p15 = json.loads(octavo_request.choices[0].message.content)["p15"]

    array.insert(0, p1)
    array.insert(1, p2)
    array.insert(2, p3)
    array.insert(3, p4)
    array.insert(4, p5)
    array.insert(5, p6)
    array.insert(6, p7)
    array.insert(7, p8)
    array.insert(8, p9)
    array.insert(9, p10)
    array.insert(10, p11)
    array.insert(11, p12)
    array.insert(12, p13)
    array.insert(13, p14)
    array.insert(14, p15)

    return array
