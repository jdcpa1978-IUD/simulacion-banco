# Simulacion del problema bancario

Proyecto en Python con SimPy. Compara 3 cajas mixtas, 2 cajas de retiro y 1 de pago, y 1 de retiro y 2 de pago, con 10 replicas independientes de 480 minutos.

## Ejecucion en Windows

Desde esta carpeta, en PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe simulacion_banco.py
.\.venv\Scripts\python.exe analisis_adicional.py
.\.venv\Scripts\python.exe -m unittest -v
```

La ejecucion imprime los indicadores solicitados y genera `resultados_banco.xlsx` con hojas de escenarios, replicas, cajeros y promedios por tipo. El archivo se sobrescribe en cada ejecucion.

El analisis adicional conserva los resultados originales y genera `anexo_30_replicas.xlsx`: compara los tres escenarios originales con cuatro cajas mixtas en 30 replicas nuevas y pareadas (semillas 10001 a 10030). La media de espera del anexo es el promedio de los promedios diarios; los intervalos t del 95 % utilizan las 30 replicas independientes y 29 grados de libertad. El intervalo de la diferencia compara cada par de replicas del mismo dia simulado. Los intervalos son aproximados y no sustituyen un criterio de espera aceptable ni un analisis de costos.

## Modelo y supuestos

- En cada llegada se eligen la accion (70 % retiro, 30 % pago) y el tipo de usuario segun las probabilidades condicionales de la tabla. El intervalo hasta esa llegada y su servicio se generan con las respectivas medias exponenciales, como en el ejemplo de la guia.
- Cada cajero tiene su propia cola FIFO. Al llegar, el cliente se asigna a una caja compatible con la menor cantidad de usuarios ocupando o esperando; los empates se distribuyen rotativamente.
- Se admiten llegadas hasta el minuto 480 inclusive; se termina de atender a todos los que llegaron dentro del horario, aunque la atencion termine despues del cierre. Los conteos incluyen a todos ellos.
- Se usan distintas semillas para las 10 replicas y los mismos clientes, llegadas y tiempos de servicio en los tres escenarios de cada replica. Esto permite comparaciones pareadas y reproducibles.
- El tiempo promedio de atencion de un cajero es el promedio de la duracion efectiva del servicio de todos los usuarios que atendio, sin incluir espera. El promedio global de espera pondera por usuario; el promedio por tipo es la cantidad total dividida entre 10 dias.
- Aunque las distribuciones condicionales son exponenciales, su mezcla no es en general exponencial. Ademas, la asignacion a la cola mas corta no genera necesariamente llegadas Poisson a cada cajero. Por ello, esta simulacion no es un M/M/1 estricto y no aplica directamente sus formulas de estado estable.
