from flask import Flask, render_template, request
import numpy as np
from scipy.optimize import linear_sum_assignment

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
                    [2.5, 4.0, 1.5, 2.0, 1.0, 2.0]])
}

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html', pesos_predefinidos=pesos_predefinidos)


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
        fila_indices, columna_indices = linear_sum_assignment(rutas_predefinidas_matriz)
        ruta_optima = np.argmin(total_pesos)
        rutas_optimas[year] = ruta_optima + 1

    # Calcular el total del peso de cada ruta para el último año
    total_pesos_ultimo = []
    for i in range(4):
        peso_ruta = np.sum(matriz[i] * np.array(list(pesos.values())))
        total_pesos_ultimo.append(peso_ruta)

    # Resolver el problema de asignación utilizando el método húngaro para el último año
    fila_indices_ultimo, columna_indices_ultimo = linear_sum_assignment(matriz)

    # Imprimir la ruta más óptima y su peso para el último año
    ruta_optima_ultimo = np.argmin(total_pesos_ultimo)
    peso_optimo_ultimo = total_pesos_ultimo[ruta_optima_ultimo]

    # Calcular la ruta óptima global
    rutas_optimas[2022] = ruta_optima_ultimo + 1
    rutas_optimas = dict(sorted(rutas_optimas.items()))
    peso_optimo_global = min(total_pesos_ultimo)
    ruta_optima_global = np.argmin(total_pesos_ultimo) + 1

    return render_template('results.html', rutas_optimas=rutas_optimas,
                           ruta_optima_global=ruta_optima_global, peso_optimo_global=peso_optimo_global)


if __name__ == '__main__':
    app.run(debug=True)
