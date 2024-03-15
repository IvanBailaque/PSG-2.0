''' Módulo encargado de los metodos de consulta del menu'''
from datetime import datetime
import re
import json
import string
from nltk.corpus import stopwords
from exceptions import FechaNoValida,HoraNoValida
import recopilador
import indice_invertido

TWEETS_PATH     = './src/tweets/tweets_persistidos'
DOCUMENTOS_PATH = './src/salida/diccionario_documentos.json'
TERMINOS_PATH   = './src/salida/diccionario_terminos.json'
POSTINGS_PATH   = './src/salida/postings.json'
FINAL_PATH      = './src/salida'

def menu_consultas_por_fechas():
    ''' Consulta tweets por fechas'''
    cantidad_buscada = int(input("Indique la cantidad de tweets a recopilar: "))
    usuario_buscado = input("Indique el nombre del usuario buscado,\
presione ENTER sin escribir nada para buscar sin un usuario determinado: ")
    rango_fecha_inicio = input("Indique la fecha de inicio de busqueda (AAAA-MM-DD): ")
    verificar_fecha(rango_fecha_inicio)
    rango_hora_inicio = input("Indique la hora de inicio de busqueda (HH:MM:SS): ")
    verificar_hora(rango_hora_inicio)
    rango_fecha_final = input("Indique la fecha de final de busqueda (AAAA-MM-DD): ")
    verificar_fecha(rango_fecha_final)
    rango_hora_final = input("Indique la hora de inicio de busqueda (HH:MM:SS): ")
    verificar_hora(rango_hora_final)

    fecha_inicio_sin_format = (f'{rango_fecha_inicio}T{rango_hora_inicio}.000Z')
    fecha_final_sin_format = (f'{rango_fecha_final}T{rango_hora_final}.000Z')

    fecha_formateada_inicio = datetime.strptime(fecha_inicio_sin_format,'%Y-%m-%dT%H:%M:%S.%f%z')
    fecha_formateada_final = datetime.strptime(fecha_final_sin_format,'%Y-%m-%dT%H:%M:%S.%f%z')

    if usuario_buscado.strip() == "":
        consultar_por_fecha(cantidad_buscada, fecha_formateada_inicio, fecha_formateada_final)
    else: consultar_por_fecha_y_usuario(
        cantidad_buscada,fecha_formateada_inicio, fecha_formateada_final, usuario_buscado)

def consultar_por_fecha(cantidad, fecha_inicio, fecha_final):
    '''Busca tweets por fechas únicamente'''
    with open (TWEETS_PATH, "r", encoding="utf8") as archivo:
        try:
            tweets_mostrados = 0
            for linea in archivo:
                if tweets_mostrados == cantidad:
                    print('Fin de búsqueda. Si no visualizo ningun tweet,\
ninguno coincide con los elementos especificados')
                    tweet = None
                    break
                tweet = json.loads(linea)
                data_tweet = tweet["data"]
                fecha_tweet = data_tweet["created_at"]
                fecha_tweet_formateada = datetime.strptime(fecha_tweet,'%Y-%m-%dT%H:%M:%S.%f%z')
                if fecha_tweet_formateada >= fecha_inicio and fecha_tweet_formateada <= fecha_final:
                    dic_author_id_hydrate = data_tweet["author_id_hydrate"]
                    usuario = dic_author_id_hydrate["username"]
                    texto = data_tweet["text"]
                    print(f'\n--------------------------------------------------------------\n@{usuario}, Fecha: {fecha_tweet_formateada}\n\n{texto}\n\
--------------------------------------------------------------\n')
                    print()
                    tweets_mostrados +=1
            return tweet
        except KeyError:
            print('Final de la búsqueda. Si ningún tweet es visualizado,\
ninguno coincide con los elementos especificados')
            return

def consultar_por_fecha_y_usuario(cantidad, fecha_inicio, fecha_final, usuario_buscado):
    '''Busca tweets por fecha y un usuario determinado'''
    with open (TWEETS_PATH, "r", encoding="utf8") as archivo:
        try:
            tweets_mostrados = 0
            for linea in archivo:
                if tweets_mostrados == cantidad:
                    print('Fin de búsqueda. Si no visualizo ningun tweet,\
ninguno coincide con los elementos especificados')
                    tweet = None
                    break
                tweet = json.loads(linea)
                data_tweet = tweet["data"]
                fecha_tweet = data_tweet["created_at"]
                fecha_tweet_formateada = datetime.strptime(fecha_tweet,'%Y-%m-%dT%H:%M:%S.%f%z')
                dic_author_id_hydrate = data_tweet["author_id_hydrate"]
                usuario = dic_author_id_hydrate["username"]
                if (fecha_tweet_formateada >= fecha_inicio\
                    and fecha_tweet_formateada <= fecha_final) \
                    and (usuario.strip() == usuario_buscado.strip()):
                    texto = data_tweet["text"]
                    print(f'\n--------------------------------------------------------------\n@{usuario}, Fecha: {fecha_tweet_formateada}\n\n{texto}\n\
--------------------------------------------------------------\n')
        except KeyError:
            print('Final de la búsqueda. Si ningún tweet es visualizado\
, ninguno coincide con los elementos especificados')
            return

def verificar_fecha(fecha):
    """
    Método para verificar la fecha indicada por el usuario
    """
    fecha_pattern = r'^(19|20)(((([02468][048])|([13579][26]))-02-29)|(\d{2})-((02-((0[1-9])|1\d|2[0-8]))|((((0[13456789])|1[012]))-((0[1-9])|((1|2)\d)|30))|(((0[13578])|(1[02]))-31)))$'
    fecha_checker = re.compile(fecha_pattern)
    if not fecha_checker.match(fecha):
        raise FechaNoValida()

def verificar_hora(hora):
    """
    Método para verificar la hora indicada por el usuario
    """
    hora_pattern = r'^(?:[01]?\d|2[0-3]):[0-5]\d:[0-5]\d$'
    hora_checker = re.compile(hora_pattern)
    if not hora_checker.match(hora):
        raise HoraNoValida()

def menu_consultas_por_palabras():
    '''Recibe inputs de palabras y cantidad para realizar las búsquedas por frase y palabras'''
    entrada = input("Indique elementos a buscar entre comillas (ej. 'f1' and 'max33verstappen'):\t")
    lista_aparicion_palabra = resolver_query(entrada, [])

    if len(lista_aparicion_palabra) == 0:
        print(f"Se encontraron {len(lista_aparicion_palabra)} tweets.")
    else:
        cant = int(input(f"=========================\nSe encontraron {len(lista_aparicion_palabra)}\
tweets.  \n=========================\n => Indique la cantidad de Tweets a mostrar:\t "))
        if cant > 0:
            resolver_lista_aparicion(lista_aparicion_palabra, cant)

def resolver_lista_aparicion(lista_aparicion_palabra, cantidad):
    '''Realiza la búsqueda de los tweets en función de la lista de aparición
    pasada por parámetro y los muestra por pantalla'''
    with open (TWEETS_PATH, "r", encoding="utf8") as archivo:
        try:
            tweets_mostrados = 0
            todos_los_tweets = archivo.readlines()
            for linea_tweet in lista_aparicion_palabra:
                if tweets_mostrados == cantidad:
                    break

                linea = todos_los_tweets[linea_tweet]

                tweet = json.loads(linea)
                texto = tweet["data"]["text"]
                data_tweet = tweet["data"]
                fecha_tweet = data_tweet["created_at"]
                fecha_tweet_formateada = datetime.strptime(fecha_tweet,'%Y-%m-%dT%H:%M:%S.%f%z')
                dic_author_id_hydrate = data_tweet["author_id_hydrate"]
                usuario = dic_author_id_hydrate["username"]
                print(f'\n==============================================================\nUsuario: @{usuario}, Fecha: {fecha_tweet_formateada}\n--------------------------------------------------------------\n\n{texto}\n\
==============================================================\n')
                tweets_mostrados +=1
            return texto
        except KeyError:
            return
def reformular_frase(frase):
    '''Funcion que reformula la frase para operar con ella'''
    stop_words = frozenset(stopwords.words('spanish'))
    palabras = frase.split()
    nueva_frase = ''
    for palabra in palabras:
        if palabra not in stop_words:
            palabra = palabra.strip("'")
            nueva_frase += f"'{palabra}' and "
    return nueva_frase

def es_frase(frase):
    '''Funcion que determina si un string dado es una frase o no'''
    return len(frase.split())>1

def resolver_query(query, lista_apariciones):
    ''' Método recursivo que recibe una query por input del usuario,
    y resuelve buscando los matchs'''
    if query == "*" or query == "* and ":
        return lista_apariciones
    try:
        primer_palabra = re.findall("^('((\w+\s?)*)'|(\*\s?))", query)[0][0]
        primer_palabra = primer_palabra.strip().strip("'")
    except IndexError:
        print("Debe indicar al menos una palabra a buscar")
        return []
    try:
        operador = re.findall("(and|or|not)", query)[0]
        forma = (f"{operador} '((?:.\w*\s*\w+)*)'")
        segunda_palabra = re.findall(forma, query)[0]
        segunda_palabra = segunda_palabra.strip().strip("'")
    except IndexError:
        print("No indico operador y/o 2da palabra, buscando unicamente la aparicion de la primera")
        operador = ""
        segunda_palabra=""
        if es_frase(primer_palabra):
            frase_reformulada = reformular_frase(primer_palabra)
            return resolver_query(frase_reformulada, [])
        else:
            return buscar_lista_apariciones(primer_palabra)

    if es_frase(primer_palabra):
        frase_reformulada = reformular_frase(primer_palabra)
        lista_apariciones = resolver_query(frase_reformulada,[])
    elif primer_palabra != "*":
        lista_apariciones = buscar_lista_apariciones(primer_palabra.strip().strip("'"))

    if es_frase(segunda_palabra):
        resultado = reformular_frase(segunda_palabra)
        lista_apariciones_segunda_palabra = resolver_query(resultado,[])
    else: lista_apariciones_segunda_palabra = buscar_lista_apariciones(\
        segunda_palabra.strip().strip("'"))

    if operador == "and":
        nueva_lista_aparicion = lista_apariciones.intersection(lista_apariciones_segunda_palabra)
    elif operador == "or":
        nueva_lista_aparicion = lista_apariciones.union(lista_apariciones_segunda_palabra)
    elif operador == "not":
        nueva_lista_aparicion = lista_apariciones.difference(lista_apariciones_segunda_palabra)

    if primer_palabra != "*":
        if operador == "" or segunda_palabra == "":
            return nueva_lista_aparicion
        else :
            parte_a_remplazar=(f"'{primer_palabra.strip()}' {operador} '{segunda_palabra}'")
    else:
        parte_a_remplazar=(f"* {operador} '{segunda_palabra}'")

    nueva_query = query.replace(parte_a_remplazar, "*")
    return resolver_query(nueva_query, nueva_lista_aparicion)

def devolver_key(id_buscado):
    ''' Devuelve la key en diccionario_terminos a partir del value indicado '''
    json_documentos = open(DOCUMENTOS_PATH, "r", encoding="utf-8")
    archivo_documento = json.loads(json_documentos.read())
    for id_del_tweet, id_inventado in archivo_documento.items():
        if id_buscado == id_inventado:
            return id_del_tweet

def buscar_lista_apariciones(palabra):
    ''' Busca la palabra pasada por parámetro'''
    lista_apariciones=[]
    palabra_lematizada = __lematizar_palabra(palabra)

    with open (POSTINGS_PATH, "r", encoding="utf-8") as postings,\
            open (TERMINOS_PATH, "r", encoding="utf-8") as dic_terminos:
        archivo_terminos = json.loads(dic_terminos.read())
        try:
            lista_apariciones = postings.readlines()[int(archivo_terminos[palabra_lematizada])]
        except KeyError:
            print(f"La palabra {palabra} no se encuentra en el diccionario de terminos")
            return set()
        
        return set(json.loads(lista_apariciones))

def __lematizar_palabra(palabra):
    '''Se acondiciona la palabra, pasando todo a mínuscula, eliminando tildes y signos
    de puntuación'''
    reemplazos=(("á", "a"), ("é","e"), ("ó","o"), ("ú","u"), ("í","i"))
    palabra=palabra.lower()
    palabra=palabra.strip(string.punctuation+"»" \
+"\x97"+"¿"+"¡" + "\u201c" + "\u201d" + "\u2014" + "\u2014l" + "\u00bf")
    for elemento_a, elemento_b in reemplazos:
        palabra = palabra.replace(elemento_a,elemento_b)
    return palabra

def  menu_buscar_mas_tweets():
    '''Funcion que busca mas tweets, y una vez buscados, genera un nuevo indice invertido'''
    print("Comenzando busqueda, presione CTRL + C para detenerla \n")
    QUERY = 'verstappen OR hamilton OR alonso OR vettel OR checo perez OR leclerc OR carlos sainz OR russel OR ocon OR stroll OR gasly OR tsunoda OR fia OR formula 1 OR formula one OR formula uno OR from:victorabadf1(-is:retweet) (lang:es)'
    EXPANSIONS = 'author_id,referenced_tweets.id,referenced_tweets.id.author_id,in_reply_to_user_id,attachments.media_keys,attachments.poll_ids,geo.place_id,entities.mentions.username'
    TWEET_FIELDS='author_id,conversation_id,created_at,entities,geo,id,lang,public_metrics,source,text'
    USER_FIELDS='created_at,description,entities,location,name,profile_image_url,public_metrics,url,username'

    recopilador.stream_tweets(QUERY, EXPANSIONS, TWEET_FIELDS, USER_FIELDS)
    print("\n Busqueda finalizada. Generando un nuevo Indice Invertido\n")

    indice_inv = indice_invertido.IndiceInvertido(TWEETS_PATH, FINAL_PATH)
    print("\n\t=> Cantidad de tweets leídos: ", len(indice_inv._lista_tweets)) 

