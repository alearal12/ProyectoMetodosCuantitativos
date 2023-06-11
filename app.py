from flask import Flask, render_template, request
import numpy as np
from scipy.optimize import linear_sum_assignment
import matplotlib.pyplot as plt

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():

    # Hardcoded values for the first two years
    derrumbes_first_year = 10.0
    gravedad_first_year = 5.0
    duracion_first_year = 20.0
    tiempo_first_year = 2.0
    congestion_first_year = 1.0
    estado_first_year = 2.0

    derrumbes_second_year = 15.0
    gravedad_second_year = 8.0
    duracion_second_year = 18.0
    tiempo_second_year = 3.0
    congestion_second_year = 2.0
    estado_second_year = 1.0

    peso_value = request.form.get('peso')

    if peso_value is not None:
        peso = float(peso_value)
    else:
        peso = 0.0  # Default value if input is not provided

    derrumbes_last_year = request.form.get('derrumbes_last_year')
    if derrumbes_last_year:
        derrumbes = float(derrumbes_last_year)
    else:
        derrumbes = 0.0  # Default value if input is not provided

    gravedad_last_year = request.form.get('gravedad_last_year')
    if gravedad_last_year:
        gravedad = float(gravedad_last_year)
    else:
        gravedad = 0.0  # Default value if input is not provided

    duracion_last_year = request.form.get('duracion_last_year')
    if duracion_last_year:
        duracion = float(duracion_last_year)
    else:
        duracion = 0.0  # Default value if input is not provided

    tiempo_last_year = request.form.get('tiempo_last_year')
    if tiempo_last_year:
        tiempo = float(tiempo_last_year)
    else:
        tiempo = 0.0  # Default value if input is not provided

    congestion_last_year = request.form.get('congestion_last_year')
    if congestion_last_year:
        congestion = float(congestion_last_year)
    else:
        congestion = 0.0  # Default value if input is not provided

    estado_last_year = request.form.get('estado_last_year')
    if estado_last_year:
        estado = float(estado_last_year)
    else:
        estado = 0.0  # Default value if input is not provided

    pesos = {}
    entradas = ['derrumbes', 'gravedad de accidente', 'duración', 'estado del tiempo', 'congestión vial', 'estado de la carretera']

    pesos_globales = np.zeros(len(entradas))

    for entrada in entradas:
        peso_value = request.form.get(entrada)
        peso = float(peso_value)
        pesos[entrada] = peso
        pesos_globales += peso

    matriz = np.zeros((4, 6))

    for i in range(4):
        for j, entrada in enumerate(entradas):
            valor_value = request.form.get(f'ruta_{i+1}_{entrada}')
            valor = float(valor_value)
            matriz[i, j] = valor

    # Hardcoded values for the first two years
    matriz[0] = [10.0, 5.0, 20.0, 2.0, 1.0, 2.0]
    matriz[1] = [15.0, 8.0, 18.0, 3.0, 2.0, 1.0]

    total_pesos = []
    for i in range(4):
        peso_ruta = np.sum(matriz[i] * np.array(list(pesos.values())))
        total_pesos.append(peso_ruta)

    ruta_optima = np.argmin(total_pesos)
    peso_optimo = total_pesos[ruta_optima]

    # Create a bar chart of the weights
    plt.bar(list(pesos.keys()), list(pesos.values()))
    plt.xlabel('Entradas')
    plt.ylabel('Pesos')
    plt.title('Pesos de las entradas')
    plt.savefig('static/chart.png')  # Save the chart as an image file
    plt.close()

    return render_template('results.html', ruta_optima=ruta_optima+1, peso_optimo=peso_optimo)


if __name__ == '__main__':
    app.run()
