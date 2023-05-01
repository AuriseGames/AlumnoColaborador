# Programa que resuelve el problema de los viajantes de ciudades mediante enfriamiento simulado

# importamos librerias
import re
import random
import math
import time
import matplotlib.pyplot as plt
from random import randint

# Funcion main
def main():

    # Variables importantes configurables para el algoritmo de enfriamiento simulado

    maximo_iteraciones = 100000

    # definimos el numero de viajantes, en este caso 3

    num_viajantes = 3

    print("\n\n\n[Comenzando la ejecución del enfriamiento simulado]\n\n")

    # Arrancamos el cronometro

    inicio = time.time()

    # Llamamos al algoritmo de enfriamiento simulado

    mejorSolucion = simulado(maximo_iteraciones, num_viajantes)

    # Paramos el cronometro y medimos el tiempo total

    fin = time.time()

    tiempo_total = fin - inicio

    print("\nEl algoritmo tardó [{}] segundos en ejecutarse.".format(
        tiempo_total))

    # Escribimos en el fichero de log los resultados obtenidos por el algoritmo de enfriamiento simulado y cerramos el fichero

    f = open("log.txt", "a")

    string = "############# RESULTADO ##############"

    string += "\n\n---ENTRADAS---"

    string += "\nMaximo de iteraciones: " + str(maximo_iteraciones)

    string += "\nNumero de viajantes: " + str(num_viajantes)

    string += "\n\n---SALIDAS---"

    string += "\nTiempo: " + str(tiempo_total)

    string += "\nDistancia: " + str(mejorSolucion[1])

    string += "\n\n---CAMINOS---\n"

    for viajante in mejorSolucion[0]:

        string = string + str(viajante) + "\n"

    string += "\n\n\n"

    f.write(string)

    f.close()

    # Imprimimos la mejor solucion con una grafica

    imprimirCaminos(mejorSolucion)

def simulado(maximo_iteraciones, num_viajantes):

    # Recuperamos las ciudades del .txt
    listaCiudades = recuperaCiudades()

    # hacemos una copia de la lista de ciudades
    copiaListaCiudades = listaCiudades[:]

    # aleatorizamos la lista de las ciudades
    random.shuffle(copiaListaCiudades)

    # generamos una solucion aleatoria valida
    solucion_mejor = generaSolucion(copiaListaCiudades, num_viajantes)

    # inicializamos el contador de iteraciones
    iteracion = 1
    
    # inicializamos la temperatura
    temperatura = maximo_iteraciones / iteracion

    # bucle principal

    while iteracion < maximo_iteraciones:
        
        solucion_candidata = mutante(solucion_mejor)

        fit_mejor = fitness(solucion_mejor)
        fit_candidato = fitness(solucion_candidata)
        
        print("it: ", iteracion, "temp: ", temperatura, "fit_candidato: ", fit_candidato, "fit_mejor: ", fit_mejor)

        if fit_candidato < fit_mejor:
            solucion_mejor = solucion_candidata

        else:
            if random.random() <= math.exp(-(fit_mejor - fit_candidato) / temperatura) - 1:
                solucion_mejor = solucion_candidata

        iteracion = iteracion + 1
        temperatura = maximo_iteraciones / iteracion

    solucion = [solucion_mejor, fitness(solucion_mejor)]

    return solucion

# Funcion que recibe una posible solución, calcula las distancias euclídeas de todos los caminos, y devuelve el fitness de la solución
def fitness(listaViajantes):

    # definimos una variable para el fitness

    f = 0.0

    # para cada viajante de la lista de viajantes

    for viajante in listaViajantes:

        # para cada ciudad del camino

        for i in range(len(viajante) - 1):

            # obtenemos las coordenadas de las dos ciudades contiguas en el camino

            x1, y1 = viajante[i]

            x2, y2 = viajante[i + 1]

            # distancia euclidea

            distancia = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)

            # la sumamos al total

            f += distancia

        # agregamos la distancia de retorno a la primera ciudad

        x1, y1 = viajante[-1]

        x2, y2 = viajante[0]

        # distancia euclidea

        distancia = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)

        # la sumamos al total

        f += distancia

    # devolvemos el fitness de la solución

    return f

# Funcion que lee el contenido de el fichero scenary.txt y devuelve la lista de ciudades con sus coordenadas
def recuperaCiudades():

    # definimos lista de posiciones

    posiciones = []

    # abrimos el fichero en modo lectura

    f = open("scenary.txt", "r")

    # pasamos el contenido a un string

    s = f.read()

    # cerramos el fichero

    f.close()

    # desechamos todo lo que no son numeros y lo convertimos en una lista de elementos

    s = [float(s) for s in re.findall(r'\d+\.?\d*', s)]

    # para cada elemento de la lista, si su index es par lo guardamos en 'x' y si es impar,

    # lo guardamos en 'y' y agregamos la tupla a la lista de posiciones

    contador = 0

    for element in s:

        if contador % 2:

            y = element

            posiciones.append((x, y))

        else:

            x = element

        contador = contador + 1

    return posiciones

# Funcion que genera una solucion aleatoria valida a partir de una lista de ciudades (con orden previamente aleatorizado)
# para N viajantes, devuelve una lista que contiene N listas con sus respectivos caminos
def generaSolucion(listaCiudades, num_viajantes):

    # Crear la lista de vectores vacíos

    lista_viajantes = []

    for i in range(num_viajantes):

        lista_viajantes.append([])

    # Repartir los elementos de la lista entre los viajantes

    for ciudad in listaCiudades[1:]:

        # Verificamos si todos los viajantes tienen al menos una ciudad

        todos_tienen_elemento = True

        for viajante in lista_viajantes:

            if len(viajante) == 0:

                todos_tienen_elemento = False

                viajante.append(ciudad)

                break

        # Si todos los viajantes tienen al menos una ciudad, se asigna aleatoriamente

        if todos_tienen_elemento:

            # Elegir al azar a qué vector se añade el elemento

            viajante = random.choice(lista_viajantes)

            # añadimos el elemento al viajante seleccionado

            viajante.append(ciudad)

    # Añadir el primer elemento a los vectores

    for v in lista_viajantes:

        v.insert(0, listaCiudades[0])

    # Devolver los vectores como una tupla

    return lista_viajantes

# Funcion que recibe una lista de viajantes y la devuelve intercambiando dos ciudades aleatoriamente
def mutante(listaViajantes):
    
    copiaListaViajantes = listaViajantes.copy()
    
    # Seleccionamos aleatoriamente una de las N listas
    lista_seleccionada = random.choice(copiaListaViajantes)
    
    # Excluimos la primera tupla de la lista seleccionada
    lista_sin_primera_tupla = lista_seleccionada[1:]
    
    # Seleccionamos aleatoriamente dos tuplas de la lista
    if len(lista_sin_primera_tupla) > 1:
        tupla_1, tupla_2 = random.sample(lista_sin_primera_tupla, 2)
    
        # Intercambiamos las posiciones de las tuplas
        indice_tupla_1 = lista_seleccionada.index(tupla_1)
        indice_tupla_2 = lista_seleccionada.index(tupla_2)
        aux = lista_seleccionada[indice_tupla_1]
        lista_seleccionada[indice_tupla_1] = lista_seleccionada[indice_tupla_2]
        lista_seleccionada[indice_tupla_2] = aux
    
    lista_sin_primera_tupla.insert(0, lista_seleccionada[0])
    
    copiaListaViajantes[copiaListaViajantes.index(lista_seleccionada)] = lista_sin_primera_tupla

    return copiaListaViajantes

# Funcion auxiliar para generar un grafico que muestre los caminos de los viajantes
def imprimirCaminos(mejorSolucion):

    totalCiudades = 0

    # Imprimimos la solución

    nCaminos = 0

    for viajante in mejorSolucion[0]:

        nCaminos += 1

        print("\n\nCamino del viajante [", nCaminos, "]: \n\n", viajante)

        print("\nNúmero de ciudades recorridas: ", len(viajante) - 1, "\n\n")

        totalCiudades += len(viajante) - 1

        x = []

        y = []

        for ciudad in viajante:

            x.append(ciudad[0])

            y.append(ciudad[1])

        x.append(viajante[0][0])

        y.append(viajante[0][1])

        plt.plot(x, y, ":o", color=random_hex_color())

        plt.xlabel('Eje X')

        plt.ylabel('Eje Y')

        plt.title('Gráfico de Caminos')

    print("\n\nNúmero total de ciudades recorridas: ", totalCiudades + 1)

    plt.text(mejorSolucion[0][0][0][0], mejorSolucion[0]
             [0][0][1], " Ciudad origen")

    print("\nLa mínima distancia recorrida es: ", mejorSolucion[1], "\n\n\n")

    plt.show()

# Funcion auxiliar para generar un color aleatorio
def random_hex_color():
    red = format(random.randint(0, 255), '02x')
    green = format(random.randint(0, 255), '02x')
    blue = format(random.randint(0, 255), '02x')
    return '#' + red + green + blue

# Se ejecuta el programa
main()
