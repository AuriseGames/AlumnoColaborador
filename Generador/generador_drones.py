# Programa que genera un fichero con los drones que se van a utilizar en el escenario.

import random

# definimos el numero de drones, en este caso 3
num_drones = 3
    
# Definimos los valores minimos y maximos para las capacidades de los drones
min_distance = 100
max_distance = 150
min_battery = 100
max_battery = 250

# Definimos las listas donde se almacenaran las capacidades de los drones
B = []
C = []
n = 0

# Fichero de salida para algoritmo genetico
f = open("Escenario/scenary_drones.txt", "w")

for _ in range(num_drones):
    n += 1
    B.append(random.randint(min_battery, max_battery))
    C.append(random.randint(min_distance, max_distance))
    dron = {
        'dron_n': n,  # drone number
        'battery_capacity': B[n - 1],  # battery capacity variable
        'distance_capacity': C[n - 1]  # distance capacity variable
    }
    f.write(str(dron) + '\n')
    
f.close()

# Fichero de salida para CPLEX
f2 = open("CPLEX/Drones/Drones.dat", "w")

f2.write('// Numero de drones' + '\n' + 'n = ' + str(num_drones) + ';\n')
f2.write('// Capacidad de carga' + '\n' + 'B = ' + str(B) + ';\n')
f2.write('// Distancia de vuelo' + '\n' + 'C = ' + str(C) + ';\n')

f2.close()