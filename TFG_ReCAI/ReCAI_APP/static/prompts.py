#Aqui van los prompts de cada ronda

#Ronda 1
PROMPT_RONDA1 = """
Genera una lista con 6 palabras que cumplan obligatoriamente los siguientes requisitos: 
1. Tienen que estar todas relacionadas con el mismo tema 
2. Las palabras tienen que estar encadenadas, es decir, todas, exceptuando la primera, tienen que empezar por la última letra de la palabra estrictamente anterior. Por ejemplo: si la primera palabra es rollitos, la segunda palabra deberá OBLIGATORIAMENTE empezar por la letra S (ya que es la última letra de rollitos)
3. No vale poner palabras de más de una palabra como "nueva york" o "nueva zelanda", es decir que no vale poner espacios, "nueva" sería una palabra y "york" otra
4. La misma palabra no puede estar dos veces, es decir no se puede repetir

Todos estos requisitos se deben cumplir al pie de la letra, en caso de que uno no se cumpla se deberá buscar otra palabra u otro tema.

Opcionalmente, sería preferible que no todas las palabras empezaran por la misma letra. 

Proporciono este ejemplo para que lo entiendas mejor, devuélvelo en el mismo formato JSON:
{
  "tema": "China",
  "p1": "rollitos",
  "p2": "shanghai",
  "p3": "imprenta",
  "p4": "acupuntura",
  "p5": "arrozales",
  "p6": "sopa"
}

                """
PROMPT_RONDA1_IA_PLAYER = """
                        Dame una palabra que se relacione con el tema {} y que empiece por '{}'.
                        La palabra debe tener {} letras en español
                        Devuélveme únicamente esa palabra.
                        """
#Rondas 2 y 3 
PROMPT_RONDA2Y3 = """
                Genera una lista de 7 palabras en español, donde cada palabra esté directamente relacionada con la palabra que esta antes y despues suya en la lista.
                Las palabras deben ser únicas dentro de la lista, es decir, no pueden repetirse. 
                Asegúrate de que las palabras no tengan relación con sus palabras no adyacentes. 
                El formato de salida debe ser en JSON, despues da las explicaciones de las relaciones.
                Formato:
                {"p1": "","p2": "","p3": "","p4": "","p5": "","p6": "","p7": ""}
"""
PROMPT_RONDA2Y3_IA_PLAYER_ELEGIRPALABRA = """
                                        Dame el id de una de las siguientes combinaciones, te dare primero el id que me tienes que devolver, luego una primera palabra y una segunda palabra:
                                        {} 
                                        """

PROMPT_RONDA2y3_IA_PLAYER_JUGARTURNO = """
                                        En base a la palabra {} y a la palabra {}, dame una palabra que empiece por {}.
                                        Devuélveme únicamente esa palabra en mayúsculas.
                                        """

#ronda 4 
PROMPT_RONDAFINAL_IA_PLAYER = """Teniendo la palabra {} y la palabra {} dame otra que este relacionada de alguna manera con cada una.
                                Esta palabra empieza por {}. Devuelve únicamente esa palabra en mayúsculas"""

#ronda 5
PROMPT_PALABRAFINAL_IA_PLAYER = """Teniendo la palabra {} dame otra que este relacionada con ella.
                                Esta palabra sigue la siguiente estructura: {}
                                Devuelve únicamente esa palabra en mayúsculas"""
#Este decide si quiere la pista o no y lo devuelve en un json
#                {
#                "quiero_pista": "SI",
#                "respuesta": ""
#                }

PROMPT_PALABRAFINALCONPISTA_IA_PLAYER = """Teniendo la palabra {} y la palabra {} dame otra que ete relacionada con ella.
                                Esta palabra sigue la siguiente estructura: {}
                                Devuelve únicamente esa palabra en mayúsculas
                                """
#Este recibe la pista tambien y solo devuelve la palabra

