"""Simulacion de colas bancarias por eventos discretos."""

from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from random import Random
from statistics import mean

import simpy
from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter


DURACION = 480
REPLICAS = 10
SEMILLA_BASE = 2026
TIPOS = ("Rapido", "Normal", "Lento", "Muy lento")
PARAMETROS = {
    "Retiro": {
        "probabilidades": (0.23, 0.40, 0.17, 0.20),
        "llegadas": (1, 2, 3, 3),
        "servicios": (1, 2, 3, 4),
    },
    "Pago": {
        "probabilidades": (0.10, 0.20, 0.30, 0.40),
        "llegadas": (1, 2, 3, 4),
        "servicios": (3, 3, 5, 7),
    },
}
ESCENARIOS = {
    "3 mixtas": ("Mixta", "Mixta", "Mixta"),
    "2 retiros y 1 pago": ("Retiro", "Retiro", "Pago"),
    "1 retiro y 2 pagos": ("Retiro", "Pago", "Pago"),
}
ARCHIVO_EXCEL = Path(__file__).resolve().parent / "resultados_banco.xlsx"


@dataclass(frozen=True)
class Cliente:
    llegada: float
    accion: str
    tipo: str
    servicio: float


@dataclass(frozen=True)
class Atencion:
    cliente: Cliente
    cajero: int
    inicio: float
    fin: float

    @property
    def espera(self):
        return self.inicio - self.cliente.llegada


def generar_clientes(semilla, duracion=DURACION):
    """Genera la misma poblacion para comparar escenarios de una replica."""
    rng = Random(semilla)
    clientes = []
    instante = 0.0
    while True:
        accion = rng.choices(("Retiro", "Pago"), weights=(0.7, 0.3))[0]
        datos = PARAMETROS[accion]
        indice = rng.choices(range(len(TIPOS)), weights=datos["probabilidades"])[0]
        instante += rng.expovariate(1 / datos["llegadas"][indice])
        if instante > duracion:
            break
        servicio = rng.expovariate(1 / datos["servicios"][indice])
        clientes.append(Cliente(instante, accion, TIPOS[indice], servicio))
    return clientes


def simular(clientes, configuracion):
    """Usa una cola FIFO por cajero y vacia las colas despues del cierre."""
    if not configuracion or any(
        not any(rol in ("Mixta", accion) for rol in configuracion)
        for accion in PARAMETROS
    ):
        raise ValueError("La configuracion debe atender retiros y pagos.")
    env = simpy.Environment()
    cajeros = [simpy.Resource(env, capacity=1) for _ in configuracion]
    atenciones = []
    siguiente = 0

    def atender(cliente, indice):
        recurso = cajeros[indice]
        with recurso.request() as solicitud:
            yield solicitud
            inicio = env.now
            yield env.timeout(cliente.servicio)
            atenciones.append(Atencion(cliente, indice + 1, inicio, env.now))

    def llegadas():
        nonlocal siguiente
        for cliente in clientes:
            yield env.timeout(cliente.llegada - env.now)
            elegibles = [
                i for i, rol in enumerate(configuracion)
                if rol in ("Mixta", cliente.accion)
            ]
            indice = min(
                elegibles,
                key=lambda i: (
                    cajeros[i].count + len(cajeros[i].queue),
                    (i - siguiente) % len(cajeros),
                ),
            )
            siguiente = (indice + 1) % len(cajeros)
            env.process(atender(cliente, indice))

    env.process(llegadas())
    env.run()
    if len(atenciones) != len(clientes):
        raise RuntimeError("No se atendieron todos los clientes registrados.")
    return atenciones


def ejecutar_replicas():
    resultados = {nombre: [] for nombre in ESCENARIOS}
    for replica in range(1, REPLICAS + 1):
        clientes = generar_clientes(SEMILLA_BASE + replica)
        for nombre, configuracion in ESCENARIOS.items():
            resultados[nombre].append(simular(clientes, configuracion))
    return resultados


def resumen(resultados):
    filas = []
    for nombre, replicas in resultados.items():
        atenciones = [atencion for replica in replicas for atencion in replica]
        if not atenciones:
            raise RuntimeError(f"No se generaron clientes para {nombre}.")
        for numero, rol in enumerate(ESCENARIOS[nombre], start=1):
            propias = [a.cliente.servicio for a in atenciones if a.cajero == numero]
            if not propias:
                raise RuntimeError(f"El cajero {numero} de {nombre} no atendio clientes.")
            filas.append((nombre, numero, rol, len(propias), mean(propias)))
    return filas


def mostrar_resultados(resultados, resumen_cajeros):
    for nombre, replicas in resultados.items():
        filas = [fila for fila in resumen_cajeros if fila[0] == nombre]
        menor = min(filas, key=lambda fila: fila[4])
        mayor = max(filas, key=lambda fila: fila[4])
        atenciones = [a for replica in replicas for a in replica]
        conteo = Counter((a.cliente.accion, a.cliente.tipo) for a in atenciones)
        print(f"\n=== {nombre} ===")
        for _, cajero, rol, cantidad, promedio in filas:
            print(f"Cajero {cajero} ({rol}): servicio {promedio:.2f} min; {cantidad} usuarios.")
        print(f"Menor tiempo promedio: cajero {menor[1]} ({menor[4]:.2f} min).")
        print(f"Mayor tiempo promedio: cajero {mayor[1]} ({mayor[4]:.2f} min).")
        print(f"Espera global por usuario: {mean(a.espera for a in atenciones):.2f} min.")
        print("Promedio diario de usuarios por accion y tipo:")
        for accion in PARAMETROS:
            print(f"  {accion}: " + ", ".join(
                f"{tipo}: {conteo[(accion, tipo)] / len(replicas):.2f}"
                for tipo in TIPOS
            ))
        print("Usuarios por replica (rapido / normal / lento / muy lento / total):")
        for numero, replica in enumerate(replicas, start=1):
            tipos = Counter(a.cliente.tipo for a in replica)
            valores = " / ".join(str(tipos[tipo]) for tipo in TIPOS)
            print(f"  {numero:2}: {valores} / {len(replica)}")


def exportar_excel(resultados, resumen_cajeros, ruta=ARCHIVO_EXCEL):
    libro = Workbook()
    resumen_hoja = libro.active
    resumen_hoja.title = "Escenarios"
    resumen_hoja.append(["Escenario", "Usuarios", "Espera global por usuario (min)"])
    replica_hoja = libro.create_sheet("Replicas")
    replica_hoja.append([
        "Escenario", "Replica", "Retiro rapido", "Retiro normal", "Retiro lento",
        "Retiro muy lento", "Pago rapido", "Pago normal", "Pago lento",
        "Pago muy lento", "Total usuarios", "Espera media (min)",
    ])
    cajero_hoja = libro.create_sheet("Cajeros")
    cajero_hoja.append([
        "Escenario", "Cajero", "Tipo de caja", "Usuarios atendidos",
        "Servicio medio (min)",
    ])
    tipo_hoja = libro.create_sheet("Promedios por tipo")
    tipo_hoja.append(["Escenario", "Accion", "Tipo", "Promedio diario de usuarios"])

    for nombre, replicas in resultados.items():
        todos = [a for replica in replicas for a in replica]
        resumen_hoja.append([nombre, len(todos), mean(a.espera for a in todos)])
        total_tipos = Counter((a.cliente.accion, a.cliente.tipo) for a in todos)
        for accion in PARAMETROS:
            for tipo in TIPOS:
                tipo_hoja.append([nombre, accion, tipo, total_tipos[(accion, tipo)] / len(replicas)])
        for numero, replica in enumerate(replicas, start=1):
            conteo = Counter((a.cliente.accion, a.cliente.tipo) for a in replica)
            replica_hoja.append(
                [nombre, numero]
                + [conteo[(accion, tipo)] for accion in PARAMETROS for tipo in TIPOS]
                + [len(replica), mean(a.espera for a in replica) if replica else None]
            )
    for fila in resumen_cajeros:
        cajero_hoja.append(list(fila))

    for hoja in libro:
        hoja.freeze_panes = "A2"
        hoja.auto_filter.ref = hoja.dimensions
        for celda in hoja[1]:
            celda.font = Font(bold=True, color="FFFFFF")
            celda.fill = PatternFill("solid", fgColor="17365D")
            celda.alignment = Alignment(wrap_text=True)
        hoja.row_dimensions[1].height = 30
        for columna in hoja.columns:
            ancho = min(36, max(len(str(c.value or "")) for c in columna) + 2)
            hoja.column_dimensions[get_column_letter(columna[0].column)].width = ancho
            for celda in columna[1:]:
                if isinstance(celda.value, float):
                    celda.number_format = "0.00"
    libro.save(ruta)


def main():
    resultados = ejecutar_replicas()
    resumen_cajeros = resumen(resultados)
    mostrar_resultados(resultados, resumen_cajeros)
    exportar_excel(resultados, resumen_cajeros)
    print(f"\nTablas guardadas en: {ARCHIVO_EXCEL}")


if __name__ == "__main__":
    main()
