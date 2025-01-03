#!/usr/bin/env python3

import time
import copy
import re
import colorsys
import sys
import random
import matplotlib.pyplot as plt
import argparse

from genetico import startGenetico
from aux_genetico import distanciaTotalDron, prioridadTotalDron, bateriaTotalDron, distanciaEuclidea, generar_hash_aleatorio
from gestor_ficheros import abrirFichero

# Crear un parser para manejar los argumentos
parser = argparse.ArgumentParser(description="Programa que resuelve un escenario mediante un algoritmo genético.")
parser.add_argument("ruta_drones", type=str, help="Ruta del archivo desde donde se leerán los parámetros de los drones.")  # Obligatorio
parser.add_argument("ruta_sensores", type=str, help="Ruta del archivo desde donde se leerán los parámetros de los sensores.")  # Obligatorio
parser.add_argument("ruta_seed_escenario", type=str, help="Ruta del archivo desde donde se leerá la seed del escenario.")  # Obligatorio
parser.add_argument("ruta_log", type=str, help="Ruta del archivo donde se escribirá el log.")  # Obligatorio
parser.add_argument("ruta_parametros", type=str, help="Ruta del archivo desde donde se leerán los parámetros del algoritmo genético.")  # Obligatorio
parser.add_argument("peso_distancia", type=float, help="Peso de la distancia en el cálculo del fitness.")  # Obligatorio
parser.add_argument("n_ejecuciones", type=int, help="Número de ejecuciones del algoritmo genético.")  # Obligatorio
parser.add_argument("-rs", "--random_seed", action="store_true", help="Establecer una seed aleatoria para el solucionador.") # Opcional
parser.add_argument("-s", "--seed", type=str, help="Semilla personalizada para el solucionador.") # Opcional
args = parser.parse_args()

def main():
    
    resultados = []

    # Recuperamos los argumentos de la linea de comandos
    n_ejecuciones = args.n_ejecuciones
    peso_distancia = args.peso_distancia

    # Recuperamos los parámetros del algoritmo genético
    tamano_poblacion, porcentaje_mejor, probabilidad_cruce, probabilidad_mutante, maximo_generaciones_sin_mejora = recuperaParametros()

    # Recuperamos los drones del .txt
    drones = recuperaDrones()
        
    # Recuperamos los sensores del .txt
    listaSensores = recuperaSensores()
    
    # Recuperamos la semilla del escenario y establecemos la del genetico
    seed, seed_genetico = recuperaSemilla()
    random.seed(seed_genetico)

    for _ in range(n_ejecuciones):
        
        if (n_ejecuciones > 1):
            # Imprimimos el progreso de las ejecuciones 
            printProgressBar(_, n_ejecuciones - 1, prefix = 'Progreso:', suffix = 'Completado', length = 50)
        
        # Ejecutamos el algoritmo genético con los parámetros configurados
        solucion = startGenetico(peso_distancia, tamano_poblacion, porcentaje_mejor, probabilidad_cruce, probabilidad_mutante, maximo_generaciones_sin_mejora, drones, listaSensores)
        
        # Comprobamos que la solucion cumple con las restricciones (valores dentro de lo esperado, que no se repitan sensores)
        # Si alguna solucion no es correcta, paramos la ejecucion
        if (comprobarSolucion(solucion, listaSensores, drones) == False):
            sys.exit("\nSolución incorrecta encontrada, deteniendo ejecución.")
        
        # Guardamos la solución obtenida en la lista de resultados
        resultados.append(solucion)
    

    # Ordenamos los resultados por valor fitness
    resultados.sort(key=lambda x: x[1])

    # Obtenemos el índice central de la lista de resultados
    middle_index = len(resultados) // 2

    # Obtenemos la solución central
    solucion_central = resultados[middle_index]
    
    # Escribimos los resultados obtenidos por el algoritmo genético en un fichero de log
    escribirResultados(solucion_central, tamano_poblacion, porcentaje_mejor, probabilidad_cruce, probabilidad_mutante, maximo_generaciones_sin_mejora, solucion_central[2], drones, peso_distancia, listaSensores, seed, seed_genetico)
    
    # Dibujamos los caminos de la solución central
    dibujarCaminos(solucion_central, listaSensores, drones)
    
    # Dibujamos el diagrama de caja y bigotes
    cajaBigotes(resultados)

    # Mantener el programa vivo para que las ventanas no se cierren
    print("Cierra ambas ventanas para terminar.")
    while plt.fignum_exists(1) or plt.fignum_exists(2):
        plt.pause(0.1)  # Procesar eventos de la GUI
    


# Funcion que lee el contenido de el fichero scenary_drones.txt y devuelve la lista de drones con sus capacidades
def recuperaDrones():
    # lista de drones
    drones = []

    try:
        f = abrirFichero(args.ruta_drones, 'r')
    except FileNotFoundError as e:
        print(f"Error: {e}")
        exit(1)
    
    s = f.read()
        
    # recuperamos los elementos del string tal que asi: {'distance_capacity': 137, 'battery_capacity': 1158}, {'distance_capacity': 108, 'battery_capacity': 1690}, ...
    drones = [eval(drone) for drone in re.findall(r'\{.*?\}', s)]

    # cerramos el fichero
    f.close()
    
    return drones

  
# Funcion que lee el contenido de el fichero scenary_sensores.txt y devuelve la lista de sensores con sus coordenadas
def recuperaSensores():
    
    # lista de sensores
    sensores = []

    # abrimos el fichero en modo lectura
    try:
        f = abrirFichero(args.ruta_sensores, 'r')
    except FileNotFoundError as e:
        print(f"Error: {e}")
        exit(1)
    
    s = f.read()

    # desechamos todo lo que no son numeros y lo convertimos en una lista de elementos
    s = [float(s) for s in re.findall(r'\d+\.?\d*', s)]

    # guardamos los elementos en las listas correspondientes
    for i in range(0, len(s), 4):
        x = s[i]
        y = s[i+1]
        p = s[i+2]
        b = s[i+3]
        sensores.append(((x, y), p, b))

    f.close()

    return sensores

def recuperaSemilla():
    try:
        f = abrirFichero(args.ruta_seed_escenario, 'r')
    except FileNotFoundError as e:
        print(f"Error: {e}")
        exit(1)
    seed = f.read()
    f.close()
    
    # Verificamos si se ha establecido la semilla aleatoria y una semilla personalizada al mismo tiempo
    if args.random_seed and args.seed is not None:
        sys.exit("Error: No se puede establecer una semilla aleatoria y una semilla personalizada al mismo tiempo.")
        
    # Establecemos la semilla para la generación de números aleatorios
    if args.random_seed:
        seed_genetico = generar_hash_aleatorio()
    else:
        if args.seed is None or args.seed == "":    
            seed_genetico = seed
        else:
            seed_genetico = args.seed
    
    return seed, seed_genetico

def recuperaParametros():
    # Variables importantes configurables para el algoritmo genetico
    try:
        f = abrirFichero(args.ruta_parametros, 'r')
    except FileNotFoundError as e:
        print(f"Error: {e}")
        exit(1)
    
    parametros = f.read().splitlines()
    f.close()
    
    tamano_poblacion = int(parametros[0].split('=')[1].strip())
    porcentaje_mejor = int(parametros[1].split('=')[1].strip())
    probabilidad_cruce = float(parametros[2].split('=')[1].strip())
    probabilidad_mutante = float(parametros[3].split('=')[1].strip())
    maximo_generaciones_sin_mejora = int(parametros[4].split('=')[1].strip())
    
    return tamano_poblacion, porcentaje_mejor, probabilidad_cruce, probabilidad_mutante, maximo_generaciones_sin_mejora
    

# Funcion auxiliar que genera una lista de colores unicos para los caminos de los drones
def generarColoresUnicos(n):
    listaColores = []
    pasoHue = 1.0 / n
    for i in range(n):
        hue = i * pasoHue
        rgb = colorsys.hsv_to_rgb(hue, 1.0, 1.0)
        rgbInt = tuple(int(x * 255) for x in rgb)
        hexColor = '#{:02x}{:02x}{:02x}'.format(*rgbInt)
        listaColores.append(hexColor)
    return listaColores


# Funcion auxiliar para generar un grafico que muestre los caminos de los drones
def dibujarCaminos(mejorSolucion, listaSensores, drones):
    
    nTotalSensores = 0
    nCaminos = 0
    listaColores = generarColoresUnicos(len(drones))
    
    # Le asignamos un ID a la figura para luego identificarla
    plt.figure(1)
    
    for dron in mejorSolucion[0]:
        nTotalSensores += len(dron) - 1
        x = []
        y = []
        for sensor in dron:
            x.append(sensor[0][0])
            y.append(sensor[0][1])
        x.append(dron[0][0][0])
        y.append(dron[0][0][1])
        plt.plot(x,y,":o",color=listaColores[nCaminos])
        nCaminos += 1
        
    # Obtenemos la lista de sensores no visitados por ningun dron comparando sus coordenadas
    sensoresNoVisitados = []
    for sensor in listaSensores:
        visitado = False
        for dron in mejorSolucion[0]:
            for sensorDron in dron:
                if sensor[0] == sensorDron[0]:
                    visitado = True
                    break
        if not visitado:
            sensoresNoVisitados.append(sensor)
    
    # Imprimimos los sensores no visitados en gris
    x = []
    y = []
    for sensor in sensoresNoVisitados:
        x.append(sensor[0][0])
        y.append(sensor[0][1])
    plt.scatter(x, y, color='gray')
    
    plt.xlabel('Eje X')
    plt.ylabel('Eje Y')
    plt.title('Genetico')
    plt.text(mejorSolucion[0][0][0][0][0],mejorSolucion[0][0][0][0][1], " sensor origen")
    print("Mostrando caminos de los drones.")
    plt.show(block=False)
    
# Funcion que genera grafico de caja y bigotes para el conjunto de soluciones obtenidas
def cajaBigotes(resultados):
    # Extraemos los valores de fitness de los resultados
    valores_fitness = [resultado[1] for resultado in resultados]

    # Le asignamos un ID a la figura para luego identificarla
    plt.figure(2)

    # Creamos el gráfico de caja y bigotes
    plt.boxplot(valores_fitness)

    # Añadimos etiquetas y título
    plt.ylabel('Fitness')
    plt.title('Diagrama de Caja y Bigotes de los Valores de Fitness')

    # Mostramos el gráfico
    print("Mostrando diagrama de caja y bigotes.")
    plt.show(block=False)


# Funcion auxiliar que escribe los resultados obtenidos por el algoritmo genetico en un fichero de log y por pantalla
def escribirResultados(mejorSolucion, tamano_poblacion, porcentaje_mejor, probabilidad_cruce, probabilidad_mutante, maximo_generaciones_sin_mejora, tiempo_total, drones, peso_distancia, listaSensores, seed, seed_genetico):
    
    copiaListaSensores = copy.deepcopy(listaSensores)
    
    # Establecemos a 0 la prioridad y la bateria del sensor de origen
    # Se hace para que al imprimir el escenario se vea que el sensor de origen tiene prioridad y bateria 0
    copiaListaSensores[0] = (copiaListaSensores[0][0], 0, 0)
    
    # Calculamos la distancia total, la bateria recargada y la prioridad acumulada por los drones
    distanciaTotal = 0
    bateriaTotal = 0
    prioridadTotal = 0
    resultadosDrones = []
    for i, dron in enumerate(mejorSolucion[0]):
        # Calculamos la distancia, prioridad y bateria total
        distanciaDron = distanciaTotalDron(dron)
        distanciaTotal += distanciaDron
        prioridadDron = prioridadTotalDron(dron)
        prioridadTotal += prioridadDron
        bateriaDron = bateriaTotalDron(dron)
        bateriaTotal += bateriaDron
        
        # Generamos el resultado del dron
        resultadoDron = f"\nDron {i+1} (C = {drones[i]['distance_capacity']:.2f}, B = {drones[i]['battery_capacity']:.2f}):"
        
        if len(dron) == 1:
            resultadoDron += f"\n- No hace ningun viaje"
        else:
            # recorremos los sensores del camino hasta el penultimo
            for j, sensor in enumerate(dron[:-1]):
                # Buscamos en la lista de sensores el index de los sensores con las mismas coordenadas que los sensores del camino
                # solo miramos las coordenadas, ya que la prioridad y la bateria de los sensores pueden diferir
                origen = copiaListaSensores.index([s for s in copiaListaSensores if s[0] == sensor[0]][0])
                destino = copiaListaSensores.index([s for s in copiaListaSensores if s[0] == dron[j+1][0]][0])
                resultadoDron += f"\n- Viaja de {origen + 1} a {destino + 1} (D += {distanciaEuclidea(sensor[0],dron[j+1][0]):.2f}, F += {dron[j+1][2]:.2f}, P += {dron[j+1][1]:.2f})"
            # Incluimos el regreso al sensor de origen
            origen = copiaListaSensores.index([s for s in copiaListaSensores if s[0] == dron[-1][0]][0])
            destino = copiaListaSensores.index([s for s in copiaListaSensores if s[0] == dron[0][0]][0])
            resultadoDron += f"\n- Viaja de {origen + 1} a {destino + 1} (D += {distanciaEuclidea(dron[-1][0],dron[0][0]):.2f})"
            resultadoDron += f"\n- Total del dron (D = {distanciaDron:.2f}, F = {bateriaDron:.2f}, P = {prioridadDron:.2f})"
        
        resultadosDrones.append(resultadoDron)
    
    # Calculamos la distancia maxima y bateria maxima recargable por los drones
    distanciaMaxima = sum(dron['distance_capacity'] for dron in drones)
    bateriaMaxima = sum(dron['battery_capacity'] for dron in drones)
    
    # Calculamos la prioridad maxima acumulable por los drones (sin contar el sensor de origen)  
    prioridadMaxima = sum(sensor[1] for sensor in copiaListaSensores[1:])
    
    # Calculamos los porcentajes de distancia, bateria y prioridad, evitando divisiones entre 0
    if distanciaMaxima > 0:
        porcentajeDistancia = (distanciaTotal / distanciaMaxima) * 100
    else:
        porcentajeDistancia = 100
    if bateriaMaxima > 0:
        porcentajeBateria = (bateriaTotal / bateriaMaxima) * 100
    else:
        porcentajeBateria = 100
    if prioridadMaxima > 0:
        porcentajePrioridad = (prioridadTotal / prioridadMaxima) * 100
    else:
        porcentajePrioridad = 100
    
    string = f"{time.strftime('%d/%m/%Y, %H:%M:%S')}"
    string += "\n\n## RESULTADO ##" 
    string += f"\n\nFitness = {mejorSolucion[1]:.2f}"
    string += f"\nTiempo = {tiempo_total:.2f}"
    string += "\n" + "\n".join(resultadosDrones)
    string += f"\n\nDistancia (D) = {distanciaTotal:.2f} / {distanciaMaxima:.2f} ( {porcentajeDistancia:.2f}% )"
    string += f"\nBateria   (F) = {bateriaTotal:.2f} / {bateriaMaxima:.2f} ( {porcentajeBateria:.2f}% )"
    string += f"\nPrioridad (P) = {prioridadTotal:.2f} / {prioridadMaxima:.2f} ( {porcentajePrioridad:.2f}% )"
    string += "\n\n## PARAMETROS ##"
    string += f"\n\nPeso Distancia = {peso_distancia}"
    string += f"\nTamano Poblacion = {tamano_poblacion}"
    string += f"\nPorcentaje Mejor = {porcentaje_mejor}"
    string += f"\nProbabilidad Cruce = {probabilidad_cruce}"
    string += f"\nProbabilidad Mutante = {probabilidad_mutante}"
    string += f"\nMaximo Generaciones sin Mejora = {maximo_generaciones_sin_mejora}"
    string += "\n\n## ESCENARIO ##"
    string += f"\n\n- Semilla del escenario\n{seed}"
    string += f"\n\n- Semilla del algoritmo genetico\n{seed_genetico}"
    string += f"\n\n- Drones\nn = {len(drones)}\nC = [{', '.join(str(dron['distance_capacity']) for dron in drones)}]\nB = [{', '.join(str(dron['battery_capacity']) for dron in drones)}]"
    string += f"\n\n- Sensores\nm = {len(copiaListaSensores)}\ncoordSensor = [{', '.join(str(sensor[0]) for sensor in copiaListaSensores)}]\nF = [{', '.join(str(sensor[2]) for sensor in copiaListaSensores)}]\nP = [{', '.join(str(sensor[1]) for sensor in copiaListaSensores)}]"
    string += "\n\n\n\n\n"
    
    # Escribimos en el fichero de log los resultados obtenidos por el algoritmo genetico y cerramos el fichero
    try:
        f = abrirFichero(args.ruta_log, 'a')
    except FileNotFoundError as e:
        print(f"Error: {e}")
        exit(1)
    
    f.write(string)
    f.close()
    
    # Imprimimos lo mismo por pantalla
    print(string)
    
# Print iterations progress (fuente: https://stackoverflow.com/questions/3173320/text-progress-bar-in-terminal-with-block-characters)
def printProgressBar (iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█', printEnd = "\r"):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print(f'\r{prefix} |{bar}| {percent}% {suffix}', end = printEnd)
    # Print New Line on Complete
    if iteration == total: 
        print("\n")

# Funcion que devuelve true si la solucion es correcta (no significa que sea una buena solucion)      
def comprobarSolucion(solucion, listaSensores, drones):
    
    correcta = True
    
    # Comprobamos que la distancia recorrida por cada dron no supere su capacidad
    for dron in solucion[0]:
        if distanciaTotalDron(dron) > drones[solucion[0].index(dron)]['distance_capacity']:
            print("Error: La distancia recorrida por un dron supera su capacidad de distancia")
            correcta = False
            return
        
    # Comprobamos que la bateria recargada por cada dron no supere su capacidad
    for dron in solucion[0]:
        if bateriaTotalDron(dron) > drones[solucion[0].index(dron)]['battery_capacity']:
            print("Error: La bateria recargada por un dron supera su capacidad de bateria")
            correcta = False
            return
        
    # Comprobamos que la prioridad acumulada por los drones no supera el total de prioridad de los sensores
    for dron in solucion[0]:
        if prioridadTotalDron(dron) > sum(sensor[1] for sensor in listaSensores):
            print("Error: La prioridad acumulada por los drones supera el total de prioridad de los sensores")
            correcta = False
            return

    # Comprobamos que un sensor no se visita dos veces (excepto el inicial)
    visited_sensors = set()
    for dron in solucion[0]:
        for i, sensor in enumerate(dron):
            if i != 0 and sensor[0] in visited_sensors:
                print("Error: El sensor", sensor[0], "se visita dos veces")
                correcta = False
                return
            visited_sensors.add(sensor[0])
            
    return correcta
    
# Ejecutamos la funcion main
main()