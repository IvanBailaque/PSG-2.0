"""
Módulo con las excepciones propias de la aplicación
"""
class FechaNoValida(Exception):
    """
    Excepción que se lanza cuando la fecha indicada no es valida
    """
    pass

class HoraNoValida(Exception):
    """
    Excepción que se lanza cuando la hora indicada no es valida
    """
    pass