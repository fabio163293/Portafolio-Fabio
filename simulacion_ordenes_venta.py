import simpy
import numpy as np
import pandas as pd

# ==============================================================================
# PARÁMETROS DE CONFIGURACIÓN DEL SISTEMA
# ==============================================================================
RANDOM_SEED = 42
TIEMPO_SIMULACION = 480  # Jornada laboral de 8 horas (en minutos)
NUM_ANALISTAS = 3

# Tasas de llegada (órdenes por hora convertidas a órdenes por minuto)
# Escenario Crítico / Hora Pico: lambda = 40 ordenes/h -> 40/60 ordenes/min
LAMBDA_PICO = 40.0 / 60.0 

class RegistroMetricas:
    def __init__(self):
        self.datos = []

    def registrar(self, id_orden, tipo, t_llegada, t_inicio_rev, t_fin_rev, paso_por_filtro):
        t_espera = t_inicio_rev - t_llegada
        t_servicio = t_fin_rev - t_inicio_rev
        t_total = t_fin_rev - t_llegada
        self.datos.append({
            'orden_id': id_orden,
            'tipo_complejidad': tipo,
            't_llegada': t_llegada,
            't_espera_cola': t_espera,
            't_servicio': t_servicio,
            't_total_sistema': t_total,
            'aprobada_automatica': paso_por_filtro
        })

def tiempo_servicio_segun_tipo(tipo):
    """Genera tiempos de servicio estocásticos mediante distribución Triangular"""
    if tipo == 'Baja':
        return np.random.triangular(3.0, 3.5, 4.0)
    elif tipo == 'Media':
        return np.random.triangular(6.0, 7.0, 8.0)
    else:  # Alta
        return np.random.triangular(10.0, 12.0, 14.0)

def proceso_orden(env, orden_id, analistas, metricas, con_filtro=False):
    t_llegada = env.now
    
    # Asignación estocástica de complejidad
    r = np.random.random()
    if r < 0.60:
        tipo = 'Baja'
    elif r < 0.85:
        tipo = 'Media'
    else:
        tipo = 'Alta'

    # Evaluación del Filtro Automático (Escenario de Mejora)
    if con_filtro and tipo == 'Baja' and np.random.random() < (0.40 / 0.60):
        # 40% del total de órdenes son aprobadas por el filtro automático
        t_filtro = np.random.uniform(0.05, 0.083) # 3 a 5 segundos
        yield env.timeout(t_filtro)
        metricas.registrar(orden_id, tipo, t_llegada, t_llegada, env.now, True)
        return

    # Proceso de Atención Manual por Analistas
    with analistas.request() as req:
        yield req  # Espera en cola (FIFO)
        t_inicio_servicio = env.now
        duracion_servicio = tiempo_servicio_segun_tipo(tipo)
        yield env.timeout(duracion_servicio)
        t_fin_servicio = env.now
        
        metricas.registrar(orden_id, tipo, t_llegada, t_inicio_servicio, t_fin_servicio, False)

def generador_llegadas(env, analistas, metricas, tasa_llegada, con_filtro=False):
    orden_id = 0
    while True:
        # Tiempo entre llegadas distribuido exponencialmente
        intervalo = np.random.exponential(1.0 / tasa_llegada)
        yield env.timeout(intervalo)
        orden_id += 1
        env.process(proceso_orden(env, orden_id, analistas, metricas, con_filtro))

def ejecutar_simulacion(con_filtro=False, num_analistas=NUM_ANALISTAS):
    np.random.seed(RANDOM_SEED)
    env = simpy.Environment()
    analistas = simpy.Resource(env, capacity=num_analistas)
    metricas = RegistroMetricas()
    
    env.process(generador_llegadas(env, analistas, metricas, LAMBDA_PICO, con_filtro))
    env.run(until=TIEMPO_SIMULACION)
    
    df = pd.DataFrame(metricas.datos)
    return df

if __name__ == '__main__':
    print("--- Ejecutando Escenario Actual (3 analistas, sin filtro) ---")
    df_actual = ejecutar_simulacion(con_filtro=False, num_analistas=3)
    
    print("\n--- Ejecutando Escenario Propuesto (3 analistas + Filtro Automático) ---")
    df_propuesto = ejecutar_simulacion(con_filtro=True, num_analistas=3)

    # Resumen comparativo de métricas
    resumen = {
        "Métrica": [
            "Total Órdenes Llegadas",
            "Órdenes Aprobadas por Filtro",
            "Tiempo Medio de Espera en Cola (min)",
            "Tiempo Máximo de Espera en Cola (min)",
            "Tiempo Total en Sistema (Lead Time) (min)"
        ],
        "Escenario Actual (As-Is)": [
            len(df_actual),
            df_actual['aprobada_automatica'].sum(),
            round(df_actual['t_espera_cola'].mean(), 2),
            round(df_actual['t_espera_cola'].max(), 2),
            round(df_actual['t_total_sistema'].mean(), 2)
        ],
        "Escenario Propuesto (To-Be)": [
            len(df_propuesto),
            df_propuesto['aprobada_automatica'].sum(),
            round(df_propuesto['t_espera_cola'].mean(), 2),
            round(df_propuesto['t_espera_cola'].max(), 2),
            round(df_propuesto['t_total_sistema'].mean(), 2)
        ]
    }

    df_resumen = pd.DataFrame(resumen)
    print("\n" + "="*60)
    print("COMPARATIVA DE RESULTADOS (FASE III)")
    print("="*60)
    print(df_resumen.to_string(index=False))