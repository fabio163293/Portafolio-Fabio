import simpy
import numpy as np
import pandas as pd

RANDOM_SEED = 42
TIEMPO_SIMULACION = 480  # 8 horas por jornada (minutos)
LAMBDA_PICO = 40.0 / 60.0  # 40 órdenes/hora

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

def tiempo_servicio_segun_tipo(tipo, rng):
    if tipo == 'Baja':
        return rng.triangular(3.0, 3.5, 4.0)
    elif tipo == 'Media':
        return rng.triangular(6.0, 7.0, 8.0)
    else:
        return rng.triangular(10.0, 12.0, 14.0)

def proceso_orden(env, orden_id, analistas, metricas, rng, con_filtro=False):
    t_llegada = env.now
    r = rng.random()
    if r < 0.60:
        tipo = 'Baja'
    elif r < 0.85:
        tipo = 'Media'
    else:
        tipo = 'Alta'

    # 40% de todas las órdenes (provenientes del segmento de baja complejidad)
    if con_filtro and tipo == 'Baja' and rng.random() < (0.40 / 0.60):
        t_filtro = rng.uniform(0.05, 0.083) # 3 a 5 seg
        yield env.timeout(t_filtro)
        metricas.registrar(orden_id, tipo, t_llegada, t_llegada, env.now, True)
        return

    with analistas.request() as req:
        yield req
        t_inicio = env.now
        duracion = tiempo_servicio_segun_tipo(tipo, rng)
        yield env.timeout(duracion)
        t_fin = env.now
        metricas.registrar(orden_id, tipo, t_llegada, t_inicio, t_fin, False)

def generador_llegadas(env, analistas, metricas, tasa, rng, con_filtro=False):
    orden_id = 0
    while True:
        intervalo = rng.exponential(1.0 / tasa)
        yield env.timeout(intervalo)
        orden_id += 1
        env.process(proceso_orden(env, orden_id, analistas, metricas, rng, con_filtro))

def ejecutar_simulacion(con_filtro=False, num_analistas=3, seed=RANDOM_SEED):
    rng = np.random.default_rng(seed)
    env = simpy.Environment()
    analistas = simpy.Resource(env, capacity=num_analistas)
    metricas = RegistroMetricas()
    
    env.process(generador_llegadas(env, analistas, metricas, LAMBDA_PICO, rng, con_filtro))
    env.run(until=TIEMPO_SIMULACION)
    
    df = pd.DataFrame(metricas.datos)
    return df

if __name__ == '__main__':
    # Ejecución de los 3 escenarios usando la misma semilla base para paridad
    df_e1 = ejecutar_simulacion(con_filtro=False, num_analistas=3, seed=42)
    df_e2 = ejecutar_simulacion(con_filtro=False, num_analistas=4, seed=42)
    df_e3 = ejecutar_simulacion(con_filtro=True, num_analistas=3, seed=42)

    resumen = pd.DataFrame({
        "Métrica": [
            "Total Órdenes Llegadas",
            "Órdenes Aprobadas por Filtro",
            "Órdenes Atendidas por Analistas",
            "Espera Media en Cola (min)",
            "Espera Máxima en Cola (min)",
            "Lead Time Promedio Total (min)",
            "¿Cumple SLA Espera < 15 min?"
        ],
        "Escenario 1 (Actual: 3 Analistas)": [
            len(df_e1),
            int(df_e1['aprobada_automatica'].sum()),
            int((~df_e1['aprobada_automatica']).sum()),
            round(df_e1['t_espera_cola'].mean(), 2),
            round(df_e1['t_espera_cola'].max(), 2),
            round(df_e1['t_total_sistema'].mean(), 2),
            "NO" if df_e1['t_espera_cola'].mean() > 15 else "SÍ"
        ],
        "Escenario 2 (+1 Analista = 4)": [
            len(df_e2),
            int(df_e2['aprobada_automatica'].sum()),
            int((~df_e2['aprobada_automatica']).sum()),
            round(df_e2['t_espera_cola'].mean(), 2),
            round(df_e2['t_espera_cola'].max(), 2),
            round(df_e2['t_total_sistema'].mean(), 2),
            "NO" if df_e2['t_espera_cola'].mean() > 15 else "SÍ"
        ],
        "Escenario 3 (Filtro Auto + 3 Analistas)": [
            len(df_e3),
            int(df_e3['aprobada_automatica'].sum()),
            int((~df_e3['aprobada_automatica']).sum()),
            round(df_e3['t_espera_cola'].mean(), 2),
            round(df_e3['t_espera_cola'].max(), 2),
            round(df_e3['t_total_sistema'].mean(), 2),
            "NO" if df_e3['t_espera_cola'].mean() > 15 else "SÍ"
        ]
    })

    print("\n" + "="*80)
    print("ANÁLISIS COMPARATIVO MULTI-ESCENARIO DE SIMULACIÓN")
    print("="*80)
    print(resumen.to_string(index=False))