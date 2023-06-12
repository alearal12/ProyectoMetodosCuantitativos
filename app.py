from flask import Flask, render_template, request, jsonify
import numpy as np
from scipy.optimize import linear_sum_assignment
import json

app = Flask(__name__)

pesos_predefinidos = {
    'derrumbes': 1.0,
    'gravedad de accidente': 2.0,
    'duración': 1.5,
    'estado del tiempo': 1.0,
    'congestión vial': 1.0,
    'estado de la carretera': 1.0
}

rutas_predefinidas = {
    2020: np.array([[1.0, 2.0, 3.0, 4.0, 2.5, 3.0],
                    [3.0, 1.5, 2.5, 1.0, 4.0, 2.0],
                    [2.5, 3.0, 1.0, 2.0, 1.5, 2.5],
                    [1.5, 2.0, 1.5, 3.0, 2.0, 4.0]]),
    2021: np.array([[2.0, 1.5, 3.0, 2.5, 1.0, 4.0],
                    [3.0, 2.0, 1.0, 2.5, 3.0, 1.5],
                    [1.0, 3.0, 2.5, 1.5, 2.5, 3.0],
                    [2.5, 4.0, 1.5, 2.0, 1.0, 2.0]]),
    2022: np.array([[1.5, 2.5, 3.0, 1.0, 2.0, 4.0],
                    [3.0, 1.0, 2.0, 2.5, 1.5, 3.0],
                    [2.0, 3.0, 1.5, 2.5, 1.0, 2.5],
                    [1.5, 2.0, 3.0, 1.0, 4.0, 2.5]])
}

def get_chart_data():
    labels = ['2020', '2021', '2022']
    global_data = [10, 20, 30]
    ultimo_data = [5, 15, 25]

    return labels, global_data, ultimo_data


def calcular_ruta_optima_global(rutas_predefinidas):
    pesos = np.array(list(pesos_predefinidos.values()))

    total_pesos_rutas = []
    for rutas_predefinidas_matriz in rutas_predefinidas.values():
        cost_matrix = rutas_predefinidas_matriz.copy()
        for i in range(cost_matrix.shape[0]):
            cost_matrix[i] *= pesos
        row_indices, col_indices = linear_sum_assignment(cost_matrix)
        total_pesos_rutas.append(cost_matrix[row_indices, col_indices].sum())

    ruta_optima_global = np.argmin(total_pesos_rutas) + 1
    peso_optimo_global = total_pesos_rutas[ruta_optima_global - 1]

    return ruta_optima_global, peso_optimo_global, total_pesos_rutas


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html', pesos_predefinidos=pesos_predefinidos)


@app.route('/charts', methods=['GET'])
def charts():
    labels, global_data, ultimo_data = get_chart_data()

    return render_template('charts.html', labels=json.dumps(labels),
                           global_data=json.dumps(global_data), ultimo_data=json.dumps(ultimo_data))


@app.route('/results', methods=['POST'])
def results():
    pesos = {}

    # Obtener los pesos para el último año ingresados por el usuario
    for entrada in pesos_predefinidos:
        try:
            peso = float(request.form[entrada])
            if peso < 0:
                return render_template('error.html', message="El peso no puede ser negativo. Intente nuevamente.")
            if entrada == 'estado de la carretera' and peso > 3:
                return render_template('error.html',
                                       message="El valor del estado de la carretera no puede ser mayor a 3. Intente nuevamente.")
            if entrada == 'congestión vial' and peso > 3:
                return render_template('error.html',
                                       message="El valor de la congestión vial no puede ser mayor a 3. Intente nuevamente.")
            pesos[entrada] = peso
        except ValueError:
            return render_template('error.html', message="Valor inválido. Intente nuevamente.")

    # Generar la matriz de entrada para el último año
    matriz = np.zeros((4, 6))
    for i in range(4):
        for j, entrada in enumerate(pesos_predefinidos):
            try:
                valor = float(request.form[f"ruta{i + 1}_{entrada}"])
                if valor < 0:
                    return render_template('error.html', message="El valor no puede ser negativo. Intente nuevamente.")
                if entrada in ['estado de la carretera', 'congestión vial'] and valor > 3:
                    return render_template('error.html',
                                           message=f"El valor de {entrada} no puede ser mayor a 3. Intente nuevamente.")
                matriz[i, j] = valor
            except ValueError:
                return render_template('error.html', message="Valor inválido. Intente nuevamente.")

    # Calcular el total del peso de cada ruta por año
    rutas_optimas = {}
    for year, rutas_predefinidas_matriz in rutas_predefinidas.items():
        total_pesos = []
        for i in range(4):
            peso_ruta = np.sum(rutas_predefinidas_matriz[i] * np.array(list(pesos.values())))
            total_pesos.append(peso_ruta)
        ruta_optima = np.argmin(total_pesos)
        rutas_optimas[year] = ruta_optima + 1

    # Calcular el total del peso de cada ruta para el último año
    total_pesos_ultimo = []
    for i in range(4):
        peso_ruta = np.sum(matriz[i] * np.array(list(pesos.values())))
        total_pesos_ultimo.append(peso_ruta)

    # Calcular la ruta óptima global
    ruta_optima_global, peso_optimo_global, total_pesos_rutas = calcular_ruta_optima_global(rutas_predefinidas)

    # Obtener la ruta óptima del último año
    ruta_optima_ultimo, peso_optimo_ultimo, _ = calcular_ruta_optima_global({2023: matriz})

    return render_template('results.html', rutas_optimas=rutas_optimas,
                           ruta_optima_global=ruta_optima_global, peso_optimo_global=peso_optimo_global,
                           ruta_optima_ultimo=ruta_optima_ultimo, peso_optimo_ultimo=peso_optimo_ultimo,
                           total_pesos_rutas=total_pesos_rutas, total_pesos = total_pesos)


if __name__ == '__main__':
    app.run(debug=True)
