'''Este modulo recopila tweets y los guarda en disco'''
import json
import os
from datetime import datetime
from TwitterAPI import TwitterAPI, TwitterOAuth, TwitterRequestError, \
TwitterConnectionError, HydrateType, OAuthType

RECOPILADOR_PATH = './src/tweets/tweets_persistidos'

def stream_tweets(query, expansions, tweet_fields, user_fields):
    '''Funcion para recopilar tweets del stream en vivo y guardarlos en disco'''
    with open(RECOPILADOR_PATH, mode="a", encoding="utf8") as archivo, \
        open("log_recopilador.txt", mode="a", encoding="utf8") as log:
        tiempo_inicio = (f'Fecha y hora de incio de recopilacion: {datetime.now()}\n')
        print(tiempo_inicio)
        log.write(tiempo_inicio)
        contador_tamanio_archivo = 0
        try:
            lector = TwitterOAuth.read_file()
            api = TwitterAPI(lector.consumer_key, lector.consumer_secret,\
            auth_type=OAuthType.OAUTH2, api_version='2')

            # AÑADO LA QUERY A STREAM RULES
            request = api.request('tweets/search/stream/rules', {'add': [{'value':query}]})
            if request.status_code != 201:
                exit()

            #RECUPERO STREAM RULES
            request = api.request('tweets/search/stream/rules', method_override='GET')

            if request.status_code != 200:
                exit()

            # INICIO DE STREAM DE TWEETS
            request = api.request('tweets/search/stream', {
                    'expansions': expansions,
                    'tweet.fields': tweet_fields,
                    'user.fields': user_fields,
                },
                hydrate_type=HydrateType.APPEND)

            print(f'[{request.status_code}] START...')
            if request.status_code != 200:
                exit()

            # GUARDADO DE TWEETS EN DISCO
            for item in request:
                json.dump(item,archivo,ensure_ascii=True,indent=None)
                archivo.write("\n")
                if contador_tamanio_archivo % 10 == 0:
                    print(f'Cantidad de tweets recopilados: {contador_tamanio_archivo}')
                    tamanio_en_megas = os.stat(RECOPILADOR_PATH).st_size / 10000000
                    print(f'Tamaño del archivo en Mb: {tamanio_en_megas}')
                contador_tamanio_archivo +=1

        except KeyboardInterrupt:
            tiempo_fin = (f'Fecha y hora de final de recopilacion: {datetime.now()}\n')
            cantidad_tweets= (f'Cantidad total de tweets recopilados: {contador_tamanio_archivo}\n')
            tamanio_final = (f'Tamaño total del archivo en Mb: {tamanio_en_megas} \n')
            print(tiempo_fin)
            print(tamanio_final)
            print(cantidad_tweets)
            log.write(f'{tiempo_fin}')
            log.write(f'{tamanio_final}')
            log.write(f'{cantidad_tweets}')
            log.write('-----------------------------------------------------------------\n')

        except TwitterRequestError as ex1:
            print(f'\n{ex1.status_code}')
            for msg in iter(ex1):
                print(msg)

        except TwitterConnectionError as ex2:
            print(ex2)

        except Exception as ex3:
            print(ex3)


