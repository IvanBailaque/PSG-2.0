import sys
import os
from datetime import datetime
import pytest
import exceptions
current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)
from consultas import consultar_por_fecha, verificar_fecha, verificar_hora,resolver_lista_aparicion,buscar_lista_apariciones,menu_consultas_por_palabras,resolver_query


def test_verificar_fecha():
    """
    Probamos metodo verificar_fecha, el cual captura la excepcion FechaNoValida
    """
    rango_fecha_inicio = "2022-20-20"
    rango_fecha_final = "2022-10-31"

    with pytest.raises(exceptions.FechaNoValida) as fecha_invalida:
        verificar_fecha(rango_fecha_inicio)
        verificar_fecha(rango_fecha_final)
        assert fecha_invalida == Exception

def test_verificar_hora():
    """
    Probamos metodo verificar_hora, el cual captura la excepcion HoraNoValida   
    """
    rango_hora_inicio = "22:330:50"
    rango_hora_final = "22:30:50"

    with pytest.raises(exceptions.HoraNoValida) as hora_invalida:
        verificar_hora(rango_hora_inicio)
        verificar_hora(rango_hora_final)
        assert hora_invalida == Exception   

def test_encuentro_tweet():
    """
    Encontramos un tweet pedido en rango de fecha y hora
    """
    #2022-10-14T14:07:04.000Z   fecha del tweet
    #"que ciegos hemos estado todo este tiempo...... ya nos advert\u00eda el bueno de juan garrido del talento del canadiense https://t.co/ry6pYZ8s30" text del tweet
    
    rango_fecha_inicio= "2022-10-14T14:05:04.000Z"
    rango_fecha_final="2022-10-14T14:08:04.000Z"

    fecha_formateada_inicio = datetime.strptime(rango_fecha_inicio,'%Y-%m-%dT%H:%M:%S.%f%z')
    fecha_formateada_final = datetime.strptime(rango_fecha_final,'%Y-%m-%dT%H:%M:%S.%f%z')

    text_tweet ="@juanky16bm\nque ciegos hemos estado todo este tiempo...... ya nos advertía el bueno de juan garrido del talento del canadiense https://t.co/ry6pYZ8s30"
    assert text_tweet == consultar_por_fecha(1,fecha_formateada_inicio,fecha_formateada_final)

def test_no_encuentro_tweet_capturo_except():
    """
    Comprobamos que el metodo captura correctamente la excepcion y el tweet no se encuentra
    """
    rango_fecha_inicio= "2022-10-14T14:05:04.000Z"
    rango_fecha_final="2022-10-14T14:08:04.000Z"

    fecha_formateada_inicio = datetime.strptime(rango_fecha_inicio,'%Y-%m-%dT%H:%M:%S.%f%z')
    fecha_formateada_final = datetime.strptime(rango_fecha_final,'%Y-%m-%dT%H:%M:%S.%f%z')

    text_tweet ="@fandemessi\ntodo el mundo deberia amar a messi"
    with pytest.raises(Exception):
        assert text_tweet == consultar_por_fecha(1,fecha_formateada_inicio,fecha_formateada_final)

    


def test_buscar_posting_de_palabra():
    """
    Buscamos en que posting esta la palabra pasada por parametro
    """
    palabra_posting = {0, 1715, 1354, 1740, 1580}  #posting de la palabra "tiempo"

    assert palabra_posting == buscar_lista_apariciones("tiempo") #comprobamos que el método devuelve el posting correcto

def test_palabra_sin_posting_capturo_except():
    """
    Comprobamos que la palabra no se encuentra en ningún posting ya que es un stopword \
    y la excepcion se captura correctamente
    """
    palabra_posting = {0,24,6512,54356}

    with pytest.raises(Exception):
        assert palabra_posting == buscar_lista_apariciones("ante")

def test_buscar_por_palabras():
    """
    Probamos nuestra metodologia para buscar por\
    palabras con: resolver query y resolver lista aparición
    """
    cantidad = 1
    entrada = "'f1' and 'max33verstappen'"
    tweet = "@hotsideofSaturn @lucsmfarias @F1 @Max33Verstappen nope you see the number 1 here that is maxs number that he has on the car this year checo has 11 https://t.co/0dLPloZW5g"
    posting = resolver_query(entrada,[])
    consulta = resolver_lista_aparicion(posting, cantidad)
    assert tweet == consulta

def test_no_encuentro_tweet_por_palabras_excep():
    """
    Comprobamos que el metodo de buscar por palabras mediante query captura correctamente la excepcion
    """
    cantidad = 1
    entrada = "'matecocido' and 'max33verstappen'"
    tweet = "@hotsideofSaturn @lucsmfarias @F1 @Max33Verstappen nope you see the number 1 here that is maxs number that he has on the car this year checo has 11 https://t.co/0dLPloZW5g"
    posting = resolver_query(entrada,[])
    with pytest.raises(Exception):
        assert tweet == resolver_lista_aparicion(posting,cantidad)



def test_buscar_frases():
    """
    Probamos nuestra metodologia para buscar por frases con: resolver query y \
    resolver lista aparición e internamente con: es_frase y reformular_frase
    """
    cantidad = 1
    entrada = "'que ciegos' and 'hemos estado todo este tiempo'"
    tweet = "que ciegos hemos estado todo este tiempo...... ya nos advert\u00eda el bueno de juan garrido del talento del canadiense https://t.co/ry6pYZ8s30"
    posting = resolver_query(entrada,[])
    consulta = resolver_lista_aparicion(posting, cantidad)
    assert tweet == consulta

def test_no_encuentro_tweet_por_frases_excep():
    cantidad = 1
    entrada = "'copa mundial' and 'hemos estado todo este tiempo'"    
    tweet = "que ciegos hemos estado todo este tiempo...... ya nos advert\u00eda el bueno de juan garrido del talento del canadiense https://t.co/ry6pYZ8s30"
    posting = resolver_query(entrada,[])
    with pytest.raises(Exception):
        assert tweet == resolver_lista_aparicion(posting,cantidad)

def test_buscar_palabra_y_frase():
    """
    Probamos nuestra metodologia para buscar por palabra y frase con: resolver query y \
    resolver lista aparición e internamente con: es_frase y reformular_frase
    """
    cantidad = 1
    entrada = "'meses' and 'guardando secreto'"
    tweet = "RT @mariaarciam: ¡Touchdown en físico! 🏈✨\n\nNo puedo creer que se llegó el día 🥹. Luego de meses guardando este secreto, al fin puedo contar…"
    posting = resolver_query(entrada,[])
    consulta = resolver_lista_aparicion(posting, cantidad)
    assert tweet == consulta

def test_buscar_frase_y_palabra():
    """
    Probamos nuestra metodologia para buscar por frase y palabra con: resolver query y \
    resolver lista aparición e internamente con: es_frase y reformular_frase
    """
    cantidad = 1
    entrada = "'meses guardando' and 'secreto'"
    tweet = "RT @mariaarciam: ¡Touchdown en físico! 🏈✨\n\nNo puedo creer que se llegó el día 🥹. Luego de meses guardando este secreto, al fin puedo contar…"
    posting = resolver_query(entrada,[])
    consulta = resolver_lista_aparicion(posting, cantidad)
    assert tweet == consulta
