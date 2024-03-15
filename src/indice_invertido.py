''' Clase índice invertido '''
import json
import os
import sys
import string
import time
from nltk.stem import SnowballStemmer #Stemmer
from nltk.corpus import stopwords #Stopwords


current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)

class IndiceInvertido:
    '''Genera un índice invertido de tweets persistidos'''

    def __init__(self, documento, salida, temp="./src/temp", blocksize=10240000, language='spanish'):
        ''' documentos: carpeta con archivos a indexar
            salida: carpeta donde se guardará el índice invertido'''
        self.documento = documento
        self.salida = salida
        self._blocksize = blocksize
        self._temp = temp
        self._stop_words = frozenset(stopwords.words(language))  # lista de stop words
        self._stemmer = SnowballStemmer(language, ignore_stopwords=False)
        self._term_to_termid = {}
        self.__generar_tweet_id()
        self.__indexar()

    def __generar_tweet_id(self):
        tweet_to_tweetid = {}
        lista_tweets = []

        with open(self.documento, 'r', encoding='utf-8') as archivo:
            for linea in archivo:
                lista_tweets.append(linea)

        for i in range(len(lista_tweets)):
            try:
                tweet_json = json.loads(lista_tweets[i])
                tweet_to_tweetid[tweet_json['data']['id']] = i
            except KeyError:
                print(f"Error al cargar la línea {i}")
                continue

        self._lista_tweets = lista_tweets
        self._tweet_to_tweetID = tweet_to_tweetid

    def __lematizar_palabra(self,palabra):
        '''Se acondiciona la palabra, pasando todo a mínuscula, eliminando tildes y signos
        de puntuación'''
        reemplazos=(("á", "a"), ("é","e"), ("ó","o"), ("ú","u"), ("í","i"))
        palabra=palabra.lower()
        palabra=palabra.strip(string.punctuation+"»"+"\x97"+"¿"+"¡" + "\u201c" + "\u201d" + "\u2014" + "\u2014l" + "\u00bf")
        for a, b in reemplazos:
            palabra = palabra.replace(a,b)
        return palabra

    def __indexar(self):
        n = 0
        lista_bloques = []

        start_invertir_bloques = time.process_time()
        for bloque in self.__parse_next_block():
            bloque_invertido = self.__invertir_bloque(bloque)
            lista_bloques.append(self.__guardar_bloque_intermedio(bloque_invertido, n))
            n += 1
        end_invertir_bloques = time.process_time()
        print("\n\t=> Invertir Bloques Elapsed time: ", end_invertir_bloques-start_invertir_bloques)

        start = time.process_time()
        self.__intercalar_bloques(lista_bloques)
        end = time.process_time()
        print("\n\t=> Intercalar Bloques Elapsed time: ", end-start)

        self.__guardar_diccionario_terminos()
        self.__guardar_diccionario_documentos()

    def __invertir_bloque(self, bloque):
        bloque_invertido={}
        bloque_ordenado = sorted(bloque,key = lambda tupla: (tupla[0], tupla[1]))
        for par in bloque_ordenado:
            posting = bloque_invertido.setdefault(par[0],set())
            posting.add(par[1]) 
        return bloque_invertido
    
    def __guardar_bloque_intermedio(self, bloque, nro_bloque):
        archivo_salida = "b"+str(nro_bloque)+".json"
        archivo_salida = os.path.join(self._temp, archivo_salida)
        for clave in bloque:
            bloque[clave]=list(bloque[clave])
        with open(archivo_salida, "w", encoding='utf-8') as contenedor:
            json.dump(bloque, contenedor)
        return archivo_salida

    def __intercalar_bloques(self, temp_files):
        start = time.process_time()
        lista_term_id=[str(i) for i in range(len(self._term_to_termid))]
        end = time.process_time()
        print("\n\t=> Tiempo en recorrer la lista de termID: ", end-start)
        posting_file = os.path.join(self.salida,"postings.json")
        start = time.process_time()
        open_files = [open(f, "r", encoding='utf-8') for f in temp_files]
        end = time.process_time()
        print("\n\t=> Tiempo en abrir todos los bloques: ", end-start)

        with open(posting_file,"w", encoding='utf-8') as salida:
            hay_mas_terminos = True
            lista_term_iterador = iter(lista_term_id)
            dic_term_id_set = dict()

            while hay_mas_terminos:
                for i in range(98304):
                    try:
                        dic_term_id_set.setdefault(next(lista_term_iterador), set())
                    except StopIteration:
                        hay_mas_terminos = False
                start = time.process_time()

                for data in open_files:
                    data.seek(0)
                    bloque = json.load(data)
                    for termino, conjunto in dic_term_id_set.items():
                        try:
                            dic_term_id_set[termino] = conjunto.union(set(bloque[termino]))
                        except:
                            pass

                for termino, conjunto in dic_term_id_set.items():
                    json.dump(list(conjunto), salida)
                    salida.write("\n")

                end = time.process_time()

    def __guardar_diccionario_terminos(self):
        path = os.path.join(self.salida, "diccionario_terminos.json")
        with open(path, "w", encoding='utf-8') as contenedor:
            json.dump(self._term_to_termid, contenedor)

    def __guardar_diccionario_documentos(self):
        path = os.path.join(self.salida, "diccionario_documentos.json")
        with open(path, "w", encoding='utf-8') as contenedor:
            json.dump(self._tweet_to_tweetID, contenedor)

    def __parse_next_block(self):
        _n = self._blocksize #espacio libre en el bloque actual
        term_id = 0 #inicializamos el diccionario de términos
        bloque = [] #lista de pares (termID, tweetID)

        for linea in self._lista_tweets:
            _n -= len(linea.encode('utf-8'))
            tweet = json.loads(linea)
            data_tweet = tweet["data"]
            tweet_text = data_tweet["text"]
            conv_id    = data_tweet["id"]
            palabras = tweet_text.split()

            for pal in palabras:
                if pal not in self._stop_words:
                    pal = self.__lematizar_palabra(pal)
                    if pal not in self._term_to_termid:
                        self._term_to_termid[pal] = term_id
                        term_id += 1
                    bloque.append((self._term_to_termid[pal], self._tweet_to_tweetID[conv_id]))
            if _n <=0:
                yield bloque
                _n = self._blocksize
                bloque = []
        yield bloque