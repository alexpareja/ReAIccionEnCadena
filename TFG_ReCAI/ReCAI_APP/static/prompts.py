#Aqui van los prompts de cada ronda

#Ronda 1
PROMPT_RONDA1 = """
                Genera una lista con 6 palabras.
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
#Rondas 2 y 3 
PROMPT_RONDA2Y3_IA_PLAYER_ELEGIRPALABRA = """
                                        Dame el id de una de las siguientes combinaciones, te dare primero el id que me tienes que devolver, luego una primera palabra y una segunda palabra:
                                        {} """

PROMPT_RONDA2y3_IA_PLAYER_JUGARTURNO ="""
                        En base a la palabra {} y a la palabra {}, dame una palabra que empiece por {}.
                        Devuélveme únicamente esa palabra en mayúsculas.
                        """

#ronda 4 
PROMPT_RONDAFINAL_IA_PLAYER = """"""

#ronda 5
PROMPT_PALABRAFINAL_IA_PLAYER = """"""
#Este decide si quiere la pista o no y lo devuelve en un json
#                {
#                "quiero_pista": "SI",
#                "respuesta": ""
#                }

PROMPT_PALABRAFINALCONPISTA_IA_PLAYER = """"""
#Este recibe la pista tambien y solo devuelve la palabra

