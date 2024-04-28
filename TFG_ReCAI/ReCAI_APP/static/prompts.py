
#Aqui van los prompts de cada ronda

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
#PROMPT_RONDA2y3 = 

#PROMPT_RONDA4 = 

#PROMPT_RONDAFINAL_IA_PLAYER =

#Este decide si quiere la pista o no y lo devuelve en un json
#                {
#                "quiero_pista": "SI",
#                "respuesta": ""
#                }
#PROMPT_PALABRAFINAL_IA_PLAYER =

#Este recibe la pista tambien y solo devuelve la palabra
#PROMPT_PALABRAFINALCONPISTA_IA_PLAYER =

