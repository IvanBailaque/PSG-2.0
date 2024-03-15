'''
Implementacion main.
'''

import os
import sys
from exceptions import FechaNoValida
from exceptions import HoraNoValida
from consultas import menu_consultas_por_fechas, menu_consultas_por_palabras, menu_buscar_mas_tweets
current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)

if __name__ == '__main__':
    switcher={"1":menu_consultas_por_fechas, "2": menu_consultas_por_palabras, "3":menu_buscar_mas_tweets}
    while True:
        try:
            print("\n\t.: Bienvenido a TP PSG :.\n")
            print("\t1: Consultas por fecha y hora ")
            print("\t2: Consultas por palabras y/o frases")
            print("\t3: Buscar más tweets")
            print("\t4: Salir del sistema")

            op=input("\nElija una opción: ")
            if op == "4":
                break
            resultado_menu = switcher[op]()
            continuar=input("Continuar usando el menu [s/n] ")
            if continuar[0].lower() != "s":
                break
        except KeyError:
            print("Entrada no valida, intente nuevamente")
            continuar=input("Continuar usando el menu [s/n] ")
            if continuar[0].lower() != "s":
                break
        except ValueError:
            print("Error en el formato de entrada")
            continuar=input("Continuar usando el menu [s/n] ")
            if continuar[0].lower() != "s":
                break
        except FechaNoValida:
            print("La fecha indicada no es valida, revise el formato pedido")
            continuar=input("Continuar usando el menu [s/n] ")
            if continuar[0].lower() != "s":
                break
        except HoraNoValida:
            print("La hora indicada no es valida")
            continuar=input("Continuar usando el menu [s/n] ")
            if continuar[0].lower() != "s":
                break
