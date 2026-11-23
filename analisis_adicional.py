"""Compara cuatro escenarios con 30 replicas independientes y pareadas."""

from math import sqrt
from pathlib import Path
from statistics import mean, stdev

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter

from simulacion_banco import ESCENARIOS, generar_clientes, simular


REPLICAS = 30
SEMILLA_BASE = 10000
T_95_GL_29 = 2.045229642132703
ESCENARIOS_ANEXO = {
    **ESCENARIOS,
    "4 mixtas": ("Mixta", "Mixta", "Mixta", "Mixta"),
}
ARCHIVO_EXCEL = Path(__file__).resolve().parent / "anexo_30_replicas.xlsx"


def ejecutar():
    filas = []
    for replica in range(1, REPLICAS + 1):
        semilla = SEMILLA_BASE + replica
        clientes = generar_clientes(semilla)
        if not clientes:
            raise RuntimeError(f"No hay llegadas en la replica {replica}.")
        esperas = {}
        for nombre, configuracion in ESCENARIOS_ANEXO.items():
            atenciones = simular(clientes, configuracion)
            esperas[nombre] = mean(atencion.espera for atencion in atenciones)
        filas.append((replica, semilla, len(clientes), esperas))
    return filas


def estadisticas(valores):
    if len(valores) != REPLICAS:
        raise ValueError(f"Se esperaban {REPLICAS} replicas.")
    promedio = mean(valores)
    desviacion = stdev(valores)
    margen = T_95_GL_29 * desviacion / sqrt(REPLICAS)
    return promedio, desviacion, promedio - margen, promedio + margen


def exportar(filas, ruta=ARCHIVO_EXCEL):
    libro = Workbook()
    hoja = libro.active
    hoja.title = "30 replicas"
    hoja.append(["Replica", "Semilla", "Usuarios"] + list(ESCENARIOS_ANEXO))
    for numero, semilla, cantidad, esperas in filas:
        hoja.append([numero, semilla, cantidad] + [esperas[nombre] for nombre in ESCENARIOS_ANEXO])

    resumen = libro.create_sheet("Resumen")
    resumen.append(["Escenario", "Espera media diaria (min)", "Desviacion", "IC 95% inferior", "IC 95% superior"])
    for nombre in ESCENARIOS_ANEXO:
        resumen.append([nombre, *estadisticas([fila[3][nombre] for fila in filas])])
    diferencias = libro.create_sheet("Comparacion pareada")
    diferencias.append(["Comparacion", "Reduccion media (min)", "Desviacion", "IC 95% inferior", "IC 95% superior"])
    reducciones = [fila[3]["3 mixtas"] - fila[3]["4 mixtas"] for fila in filas]
    diferencias.append(["3 mixtas menos 4 mixtas", *estadisticas(reducciones)])

    for hoja in libro:
        hoja.freeze_panes = "A2"
        hoja.auto_filter.ref = hoja.dimensions
        for celda in hoja[1]:
            celda.font = Font(bold=True, color="FFFFFF")
            celda.fill = PatternFill("solid", fgColor="17365D")
            celda.alignment = Alignment(wrap_text=True)
        hoja.row_dimensions[1].height = 30
        for columna in hoja.columns:
            hoja.column_dimensions[get_column_letter(columna[0].column)].width = min(
                36, max(len(str(c.value or "")) for c in columna) + 2
            )
            for celda in columna[1:]:
                if isinstance(celda.value, float):
                    celda.number_format = "0.00"
    libro.save(ruta)


def main():
    filas = ejecutar()
    exportar(filas)
    for nombre in ESCENARIOS_ANEXO:
        promedio, desviacion, inferior, superior = estadisticas([fila[3][nombre] for fila in filas])
        print(f"{nombre}: media diaria={promedio:.4f}, desviacion={desviacion:.4f}, IC95%=[{inferior:.4f}, {superior:.4f}]")
    reduccion = estadisticas([fila[3]["3 mixtas"] - fila[3]["4 mixtas"] for fila in filas])
    print(f"Reduccion pareada 3 - 4 mixtas: media={reduccion[0]:.4f}, IC95%=[{reduccion[2]:.4f}, {reduccion[3]:.4f}]")
    print(f"Resultados: {ARCHIVO_EXCEL}")


if __name__ == "__main__":
    main()
