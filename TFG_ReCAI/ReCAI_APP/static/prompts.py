
#Aqui van los prompts de cada ronda

PROMPT_RONDA1 = """
                Genera una lista con 6 palabras que cumplan obligatoriamente los siguientes requisitos: 
                1. Tienen que estar todas relacionadas con el mismo tema 
                2. Las palabras tienen que estar encadenadas, es decir, todas, exceptuando la primera, tienen que empezar por la última letra de la palabra estrictamente anterior. Por ejemplo: si la primera palabra es rollitos, la segunda palabra deberá OBLIGATORIAMENTE empezar por la letra S (ya que es la última letra de rollitos)
                3. No vale poner palabras de más de una palabra como "nueva york" o "nueva zelanda", es decir que no vale poner espacios, "nueva" sería una palabra y "york" otra
                4. La misma palabra no puede estar dos veces, es decir no se puede repetir

                Todos estos requisitos se deben cumplir al pie de la letra, en caso de que uno no se cumpla se deberá buscar otra palabra u otro tema.

                Opcionalmente, sería preferible que no todas las palabras empezaran por la misma letra
                Proporciono este ejemplo con el formato deseado para que lo entiendas mejor:
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
                En base a la palabra {}, dame una palabra que se relacione con el tema {} y que empiece por {}.
                Devuélveme únicamente esa palabra en mayúsculas y sin tildes.
                """
#PROMPT_RONDA2y3 = 

#PROMPT_RONDA4 = 



