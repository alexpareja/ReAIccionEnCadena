from django.shortcuts import render, redirect
from .forms import RegistroFormulario, LoginFormulario, CambiarContraseñaFormulario, FormNombresJugadores, TurnFormulario
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
import openai
from django.templatetags.static import static
import random
from django.contrib.auth import update_session_auth_hash, login
from django.contrib.auth.models import User
from .forms import OpcionForm
from .models import PalabrasEncadenadas, EslabonCentral, RondaFinal
from django import template
from django.urls import reverse
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

            palabras_modificadas[int(n_palabra_adivinado)-1] = palabra_a_adivinar
            n_palabra_adivinado += 1
            if n_palabra_adivinado > 6:
                    fin=1
                    request.session['puntos_jugador1'] = puntos_jugador1
                    request.session['puntos_jugador2'] = puntos_jugador2
                    return render(request, 'palabras_encadenadas.html', {
        'j1': j1, 'j2' : j2, 'jugador1': jugador1, 'jugador2' :jugador2,
        'puntos_jugador1' :puntos_jugador1, 'puntos_jugador2': puntos_jugador2,
        'turno_actual': turno_actual, 'palabras': palabras, 'palabras_modificadas': palabras_modificadas,
        'n_palabra_adivinado': n_palabra_adivinado, 'turno_actual': turno_actual,
        'letras_mostradas': letras_mostradas, 'primera_letra': primera_letra, 'fin' : fin,
        'idPalabra': "p" + str(n_palabra_adivinado)
    })
            
            palabra_adivinada = getattr(palabras, 'p' + str(n_palabra_adivinado), '')
            letras_faltantes = len(palabra_adivinada) - letras_mostradas
            palabras_modificadas[int(n_palabra_adivinado)-1] = getattr(palabras, 'p' + str(n_palabra_adivinado), '')[0] +'_ ' * letras_faltantes + f" ({len(palabra_adivinada)})"
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

                palabras_modificadas[int(n_palabra_adivinado)-1] = palabra_a_adivinar
                n_palabra_adivinado += 1
                if n_palabra_adivinado > 6:
                    fin=1
                    request.session['puntos_jugador1'] = puntos_jugador1
                    request.session['puntos_jugador2'] = puntos_jugador2
                    return render(request, 'palabras_encadenadas.html', {
        'j1': j1, 'j2' : j2, 'jugador1': jugador1, 'jugador2' :jugador2,
        'puntos_jugador1' :puntos_jugador1, 'puntos_jugador2': puntos_jugador2,
        'turno_actual': turno_actual, 'palabras': palabras, 'palabras_modificadas': palabras_modificadas,
        'n_palabra_adivinado': n_palabra_adivinado, 'turno_actual': turno_actual,
        'letras_mostradas': letras_mostradas, 'primera_letra': primera_letra, 'fin' : fin,
        'idPalabra': "p" + str(n_palabra_adivinado)
    })

                palabras_modificadas[int(n_palabra_adivinado)-1] = getattr(palabras, 'p' + str(n_palabra_adivinado), '')[0]
                primera_letra = getattr(palabras, 'p' + str(n_palabra_adivinado), None)[0]
                letras_mostradas = 1 
            else:

                palabra_adivinada = getattr(palabras, 'p' + str(n_palabra_adivinado), '')
                letras_faltantes = len(palabra_adivinada) - letras_mostradas
                primera_letra += palabra_adivinada[letras_mostradas-1] 
                palabras_modificadas[int(n_palabra_adivinado)-1] = primera_letra +'_ ' * letras_faltantes + f" ({len(palabra_adivinada)})"
                    

    request.session['turno_actual'] = turno_actual
    request.session['npa'] = n_palabra_adivinado
    request.session['lm'] = letras_mostradas
    request.session['pl'] = primera_letra
    request.session['puntos_jugador1'] = puntos_jugador1
    request.session['puntos_jugador2'] = puntos_jugador2
    request.session['ronda'] = 'Ronda 1: Palabras encadenadas'

    return render(request, 'palabras_encadenadas.html', {
        'j1': j1, 'j2' : j2, 'jugador1': jugador1, 'jugador2' :jugador2,
        'puntos_jugador1' :puntos_jugador1, 'puntos_jugador2': puntos_jugador2,
        'turno_actual': turno_actual, 'palabras': palabras, 'palabras_modificadas': palabras_modificadas,
        'n_palabra_adivinado': n_palabra_adivinado, 'turno_actual': turno_actual,
        'letras_mostradas': letras_mostradas, 'primera_letra': primera_letra, 'fin' : fin,
        'idPalabra': "p" + str(n_palabra_adivinado)
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
    # Datos de los jugadores
    fin=0
    j1 = request.session.get('j1', 'Tipo de j1 no ingresado')
    jugador1 = request.session.get('jugador1', 'Nombre del jugador 1 no ingresado')
    j2 = request.session.get('j2', 'Tipo de j2 no ingresado')
    jugador2 = request.session.get('jugador2', 'Nombre del jugador 2 no ingresado')

    # Obteniendo las palabras de la ronda
    palabras = EslabonCentral.objects.first()
    letras_mostradas = request.session.get('letras_mostradasRonda2', 1)

    # Estado actual del juego
    turno_actual = request.session.get('turno_actual', j1)
    n_palabra_adivinado = request.session.get('n_palabra_adivinadoRonda2', 2)
    primera_letra = request.session.get('primera_letraRonda2', getattr(palabras, 'p' + str(n_palabra_adivinado), '')[0])
    puntos_jugador1 = request.session.get('puntos_jugador1', 0)
    puntos_jugador2 = request.session.get('puntos_jugador2', 0)
  

    palabras_modificadas = []

    for i in range(1, 7): 
        nombre_campo = 'p' + str(i)
        palabra = getattr(palabras, nombre_campo, '')
        palabra_modificada = ''
        if i != 1 and i != 7 and i != 4:
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
            if n_palabra_adivinado > 6:
                fin=1
                request.session['puntos_jugador1'] = puntos_jugador1
                request.session['puntos_jugador2'] = puntos_jugador2
                return render(request, 'centro_de_la_cadena.html', {
        'j1': j1, 'jugador1': jugador1, 'puntos_jugador1': puntos_jugador1,
        'j2': j2, 'jugador2': jugador2, 'puntos_jugador2': puntos_jugador2,
        'palabras_modificadas': palabras_modificadas, 'palabras': palabras,
        'n_palabra_adivinado': n_palabra_adivinado, 'turno_actual': turno_actual,
        'letras_mostradas': letras_mostradas,
        'primera_letra': primera_letra, 'fin':fin,
        'idPalabra': "p" + str(n_palabra_adivinado)
    })
            if n_palabra_adivinado > 4:
                palabras_modificadas[int(n_palabra_adivinado)-3] = getattr(palabras, 'p' + str(n_palabra_adivinado), '')[0]
            else:
                palabras_modificadas[int(n_palabra_adivinado)-2] = getattr(palabras, 'p' + str(n_palabra_adivinado), '')[0]
            primera_letra = getattr(palabras, 'p' + str(n_palabra_adivinado), None)[0]
            letras_mostradas = 1  
        else:
            turno_actual = j2 if turno_actual == j1 else j1
            letras_mostradas += 1
            if len(palabra_a_adivinar) <= letras_mostradas:
                # Lógica cuando se han revelado todas las letras
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
                if n_palabra_adivinado > 6:
                    fin=1
                    request.session['puntos_jugador1'] = puntos_jugador1
                    request.session['puntos_jugador2'] = puntos_jugador2
                    return render(request, 'centro_de_la_cadena.html', {
        'j1': j1, 'jugador1': jugador1, 'puntos_jugador1': puntos_jugador1,
        'j2': j2, 'jugador2': jugador2, 'puntos_jugador2': puntos_jugador2,
        'palabras_modificadas': palabras_modificadas, 'palabras': palabras,
        'n_palabra_adivinado': n_palabra_adivinado, 'turno_actual': turno_actual,
        'letras_mostradas': letras_mostradas,
        'primera_letra': primera_letra, 'fin':fin,
        'idPalabra': "p" + str(n_palabra_adivinado)
                        })
                if n_palabra_adivinado > 4:
                    palabras_modificadas[int(n_palabra_adivinado)-3] = getattr(palabras, 'p' + str(n_palabra_adivinado), '')[0]
                else:
                    palabras_modificadas[int(n_palabra_adivinado)-2] = getattr(palabras, 'p' + str(n_palabra_adivinado), '')[0]
                primera_letra = getattr(palabras, 'p' + str(n_palabra_adivinado), None)[0]
                letras_mostradas = 1  
            else:
                # Actualizar primera_letra para mostrar las letras acumuladas hasta ahora
                primera_letra += getattr(palabras, 'p' + str(n_palabra_adivinado), None)[letras_mostradas-1] 
                if n_palabra_adivinado > 4:
                    palabras_modificadas[int(n_palabra_adivinado)-3] = primera_letra
                else:
                    palabras_modificadas[int(n_palabra_adivinado)-2] = primera_letra
         
        request.session['turno_actual'] = turno_actual
        request.session['n_palabra_adivinadoRonda2'] = n_palabra_adivinado
        request.session['letras_mostradasRonda2'] = letras_mostradas
        request.session['primera_letraRonda2'] = primera_letra
        request.session['puntos_jugador1'] = puntos_jugador1
        request.session['puntos_jugador2'] = puntos_jugador2
        request.session['ronda'] = "Ronda 2: Centro de la cadena"


    

    # Renderizar la plantilla con el contexto actualizado
    return render(request, 'centro_de_la_cadena.html', {
        'j1': j1, 'jugador1': jugador1, 'puntos_jugador1': puntos_jugador1,
        'j2': j2, 'jugador2': jugador2, 'puntos_jugador2': puntos_jugador2,
        'palabras_modificadas': palabras_modificadas, 'palabras': palabras,
        'n_palabra_adivinado': n_palabra_adivinado, 'turno_actual': turno_actual,
        'letras_mostradas': letras_mostradas,
        'primera_letra': primera_letra, 'fin':fin,
        'idPalabra': "p" + str(n_palabra_adivinado)
    })

def una_lleva_a_la_otra(request):
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
    j1 = request.session.get('j1', 'Tipo de j1 no ingresado')
    jugador1 = request.session.get('jugador1', 'Nombre del jugador 1 no ingresado')
    fin = 0

    palabras = RondaFinal.objects.first()
    letras_mostradas = request.session.get('letras_mostradas', 1)

    n_palabra_adivinado = request.session.get('n_palabra_adivinado', 2)
    primera_letra = request.session.get('primera_letra', getattr(palabras, 'p' + str(n_palabra_adivinado), None)[0])
    puntos_jugador1 = request.session.get('puntos_jugador1', 80000)
    comodines = request.session.get('comodines', 2)
    idPalabra = "p" + str(n_palabra_adivinado)


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

    if (n_palabra_adivinado > 12):
        fin=1
        return render(request, 'ultima_cadena.html', {'j1': j1, 'jugador1': jugador1, 
                                                'puntos_jugador1' :puntos_jugador1, 'palabras_modificadas': palabras_modificadas,
                                                'palabras': palabras,
                                                'n_palabra_adivinado': n_palabra_adivinado,
                                                'primera_letra': primera_letra,
                                                'comodines': comodines,
                                                'idPalabra': idPalabra,
                                                'fin': fin
                                                })

    if request.method == 'POST':
        print(n_palabra_adivinado)
        form = TurnFormulario(request.POST)
        if form.is_valid():
            respuesta = form.cleaned_data['respuesta']
            nombre_campo = 'p' + str(n_palabra_adivinado)
            palabra_a_adivinar = getattr(palabras, nombre_campo, None)

            if respuesta.upper() == palabra_a_adivinar:
                print("Acertaste!! La solución era " + palabra_a_adivinar)
                palabras_modificadas[int(n_palabra_adivinado/2)-1] = palabra_a_adivinar
                if n_palabra_adivinado >= 12:
                    fin=1
                    return render(request, 'ultima_cadena.html', {'j1': j1, 'jugador1': jugador1, 
                                                'puntos_jugador1' :puntos_jugador1, 'palabras_modificadas': palabras_modificadas,
                                                'palabras': palabras,
                                                'n_palabra_adivinado': n_palabra_adivinado,
                                                'primera_letra': primera_letra,
                                                'comodines': comodines,
                                                'idPalabra': idPalabra,
                                                'fin': fin,
                                                'juego_acabado' : 0
                                                })
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
                        return render(request, 'ultima_cadena.html', {'j1': j1, 'jugador1': jugador1, 
                                                'puntos_jugador1' :puntos_jugador1, 'palabras_modificadas': palabras_modificadas,
                                                'palabras': palabras,
                                                'n_palabra_adivinado': n_palabra_adivinado,
                                                'primera_letra': primera_letra,
                                                'comodines': comodines,
                                                'idPalabra': idPalabra,
                                                'fin': fin,
                                                'juego_acabado' : 0
                                                })
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
    return render(request, 'ultima_cadena.html', {'j1': j1, 'jugador1': jugador1, 
                                                'puntos_jugador1' :puntos_jugador1, 'palabras_modificadas': palabras_modificadas,
                                                'palabras': palabras,
                                                'n_palabra_adivinado': n_palabra_adivinado,
                                                'primera_letra': primera_letra,
                                                'comodines': comodines,
                                                'idPalabra': idPalabra,
                                                'fin': fin,
                                                'juego_acabado' : 0
                                                })

def ultima_palabra(request):
    juego_acabado=0  
    j1 = request.session.get('j1', 'Tipo de j1 no ingresado')
    jugador1 = request.session.get('jugador1', 'Nombre del jugador 1 no ingresado')
    puntos_jugador1 = request.session.get('puntos_jugador1', 80000)

    palabras = RondaFinal.objects.first()

    n_palabra_adivinado = request.session.get('n_palabra_adivinado', 2)

    palabra_inicial = getattr(palabras, 'p13', None)
    request.session['palabra_inicial'] = palabra_inicial
    solucion = getattr(palabras, 'final', None)
    solucion_mostrada = getattr(palabras, 'final', None)[0] + getattr(palabras, 'final', None)[1] + '________' + getattr(palabras, 'final', None)[len(solucion)-1]
    request.session['solucion_mostrada'] = solucion_mostrada
    pista = getattr(palabras, 'pista', None)
    pista_mostrada = request.session.get('pista_mostrada', '?')
    request.session['pista_mostrada'] = pista_mostrada



    if request.method == 'POST':
        form = TurnFormulario(request.POST)
        if form.is_valid():
            respuesta = form.cleaned_data['respuesta']
            if respuesta.upper() == solucion.upper():
                print("Ganas")
                solucion_mostrada = solucion

            else:
                puntos_jugador1 = 0
                request.session['puntos_jugador1'] = puntos_jugador1
                solucion_mostrada = solucion
            request.session['solucion_mostrada'] = solucion_mostrada
            juego_acabado = 1
        else:
            pista_mostrada = pista
            request.session['pista_mostrada'] = pista_mostrada
            puntos_jugador1 = puntos_jugador1 / 2
            request.session['puntos_jugador1'] = puntos_jugador1



    idPalabra = "p" + str(n_palabra_adivinado)

    
    return render(request, 'ultima_palabra.html', {'j1': j1, 'jugador1': jugador1, 
                                                'puntos_jugador1' :puntos_jugador1,
                                                'idPalabra': idPalabra,
                                                'palabra_inicial': palabra_inicial,
                                                'solucion': solucion,
                                                'solucion_mostrada':solucion_mostrada,
                                                'pista': pista,
                                                'pista_mostrada': pista_mostrada,
                                                'fin': 0,
                                                'juego_acabado' : juego_acabado
                                                })

def fin_juego(request):

    j1 = request.session.get('j1', 'Tipo de j1 no ingresado')
    jugador1 = request.session.get('jugador1', 'Nombre del jugador 1 no ingresado')
    puntos_jugador1 = request.session.get('puntos_jugador1', 0)
    ronda = request.session.get('ronda', 'Juego no empezado') 
    


    return render(request, 'fin_juego.html', {'j1': j1, 'jugador1': jugador1,
        'puntos_jugador1' :puntos_jugador1, 'ronda': ronda})


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