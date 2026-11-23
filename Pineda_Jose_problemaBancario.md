## 1. Introducción

El Banco de Colombia requiere evaluar la atención de sus usuarios para decidir cómo distribuir sus tres cajas entre operaciones de retiro y pago. El objetivo de este laboratorio es comparar las configuraciones propuestas mediante simulación y determinar cuál presenta el menor tiempo promedio de espera.

## 2. Metodología

Se utilizó Python con la biblioteca SimPy para simular diez jornadas independientes de ocho horas cada una. Se evaluaron tres escenarios: tres cajas mixtas, dos cajas para retiros y una para pagos, y una caja para retiros y dos para pagos.

En cada llegada se seleccionó una operación: retiro con probabilidad del 70 % o pago con probabilidad del 30 %. El tipo de usuario se seleccionó según las probabilidades del enunciado. Los intervalos entre llegadas y los tiempos de servicio se generaron mediante distribuciones exponenciales con las medias correspondientes a cada tipo.

Cada cajero dispone de una cola FIFO. El usuario se asigna a una caja compatible con la menor cantidad de personas en atención o espera. Se admiten llegadas hasta el minuto 480 y se completa la atención de quienes llegaron durante la jornada. Para facilitar la comparación, cada réplica utiliza las mismas llegadas y tiempos de servicio en los tres escenarios.

El modelo M/M/1 teórico supone llegadas Poisson, tiempos de servicio exponenciales y un servidor. Aunque en esta simulación las distribuciones son exponenciales para cada tipo de usuario, su mezcla no es necesariamente exponencial y la asignación a la cola más corta no garantiza llegadas Poisson a cada caja. Por ello, los resultados no representan un M/M/1 estricto.

## 3. Resultados

**Cajeros con menor y mayor tiempo promedio de atención**

El tiempo de atención corresponde a la duración del servicio, sin incluir la espera.

| Escenario | Menor tiempo promedio | Mayor tiempo promedio |
|---|---:|---:|
| Tres cajas mixtas | Cajero 3: 3,31 min | Cajero 1: 3,54 min |
| Dos retiros y un pago | Cajero 2: 2,44 min | Cajero 3: 5,43 min |
| Un retiro y dos pagos | Cajero 1: 2,50 min | Cajero 2: 5,57 min |

Las diferencias dependen de las operaciones asignadas y de la variabilidad de los tiempos simulados; no demuestran que un cajero sea intrínsecamente más eficiente.

**Promedio diario de usuarios por tipo**

| Operación | Rápido | Normal | Lento | Muy lento |
|---|---:|---:|---:|---:|
| Retiro | 31,40 | 52,10 | 22,70 | 27,60 |
| Pago | 6,70 | 11,40 | 17,20 | 23,90 |
| **Total** | **38,10** | **63,50** | **39,90** | **51,50** |

El promedio fue de 193 usuarios por jornada. Los conteos son iguales en los tres escenarios porque se emplearon las mismas llegadas para compararlos.

**Total de usuarios por réplica**

| Réplica | Rápido | Normal | Lento | Muy lento | Total |
|---:|---:|---:|---:|---:|---:|
| 1 | 42 | 81 | 42 | 51 | 216 |
| 2 | 42 | 68 | 48 | 49 | 207 |
| 3 | 33 | 75 | 34 | 48 | 190 |
| 4 | 53 | 69 | 27 | 57 | 206 |
| 5 | 36 | 53 | 39 | 58 | 186 |
| 6 | 28 | 59 | 37 | 50 | 174 |
| 7 | 31 | 48 | 40 | 46 | 165 |
| 8 | 39 | 52 | 41 | 59 | 191 |
| 9 | 36 | 57 | 51 | 52 | 196 |
| 10 | 41 | 73 | 40 | 45 | 199 |

La réplica 7 tuvo el menor total, con 165 usuarios. Los mínimos por tipo fueron: 28 rápidos en la réplica 6, 48 normales en la 7, 27 lentos en la 4 y 45 muy lentos en la 10.

**Necesidad de un cajero adicional**

| Escenario | Espera promedio por usuario |
|---|---:|
| Tres cajas mixtas | 0,97 min |
| Dos retiros y un pago | 4,98 min |
| Un retiro y dos pagos | 5,21 min |

La media combinada entre llegadas es de 2,398 minutos, equivalente a una tasa estimada de 0,417 usuarios por minuto. La media combinada de servicio es de 3,198 minutos, equivalente a 0,313 usuarios por minuto por cajero. Para tres cajeros, la capacidad equivalente conjunta es de aproximadamente 0,938 usuarios por minuto.

Si la carga se distribuyera uniformemente, el factor de utilización aproximado sería: ρ ≈ λ / (3μ) = 0,417 / (3 × 0,313) ≈ 0,445 (44,5 %).

En estas diez réplicas iniciales no se simuló la alternativa de cuatro cajas; el anexo presenta una comparación adicional con 30 réplicas. No se ha establecido un límite aceptable de espera. Además, el factor calculado es una aproximación y no una utilización M/M/1 exacta por cajero.

**Configuración de cajas exclusivas**

Si se exige elegir entre las configuraciones exclusivas, la alternativa de dos cajas para retiros y una para pagos presentó la menor espera: 4,98 minutos frente a 5,21 minutos. La diferencia es pequeña y no debe considerarse estadísticamente concluyente con estas diez réplicas.

Entre los tres escenarios evaluados, las tres cajas mixtas presentaron la menor espera, aproximadamente un 81 % inferior a la de cada alternativa exclusiva.

## 4. Conclusiones

Bajo los datos y supuestos de la simulación, se recomienda conservar las tres cajas mixtas, pues ofrecieron la menor espera promedio observada: 0,97 minutos por usuario. Su flexibilidad permite atender ambos tipos de operación sin reservar capacidad para una sola finalidad.

Si el banco debe establecer cajas exclusivas, la alternativa de dos para retiros y una para pagos obtuvo el mejor resultado de las dos opciones especializadas. Las 30 réplicas adicionales documentadas en el anexo también presentan un promedio diario menor para esa alternativa que para una caja de retiros y dos de pagos.

En el análisis adicional, la espera media diaria pasó de 0,815 minutos con tres cajas mixtas a 0,225 minutos con cuatro. La reducción media pareada fue de 0,590 minutos por usuario. Aunque la cuarta caja disminuyó la espera simulada, su incorporación no puede justificarse definitivamente sin conocer su costo y el nivel de servicio aceptable. Las 30 réplicas mejoran la precisión de las estimaciones, pero no corrigen los supuestos ni sustituyen datos reales.

## Anexo. Treinta réplicas y evaluación de una cuarta caja

Se realizaron 30 réplicas adicionales e independientes de las diez iniciales, con semillas de 10001 a 10030. En cada réplica se compararon los tres escenarios originales con un cuarto escenario de cuatro cajas mixtas atendidas por personal. Se utilizaron las mismas llegadas y tiempos de servicio en los cuatro escenarios de cada réplica; las llegadas se reciben durante 480 minutos y se completa su atención después del cierre si es necesario.

Las siguientes esperas están expresadas en minutos por usuario de cada réplica. «2R + 1P» indica dos cajas de retiro y una de pago; «1R + 2P» indica una de retiro y dos de pago. La columna de usuarios corresponde a las llegadas compartidas entre los escenarios.

| Réplica | Semilla | Usuarios | 3 mixtas | 2R + 1P | 1R + 2P | 4 mixtas |
|---:|---:|---:|---:|---:|---:|---:|
| 1 | 10001 | 198 | 0,65 | 2,59 | 3,25 | 0,20 |
| 2 | 10002 | 198 | 0,66 | 3,49 | 3,06 | 0,05 |
| 3 | 10003 | 208 | 1,55 | 7,36 | 6,55 | 0,63 |
| 4 | 10004 | 198 | 0,83 | 4,28 | 1,61 | 0,17 |
| 5 | 10005 | 203 | 0,21 | 1,67 | 2,83 | 0,01 |
| 6 | 10006 | 163 | 0,45 | 1,37 | 3,59 | 0,09 |
| 7 | 10007 | 201 | 0,49 | 2,11 | 4,54 | 0,22 |
| 8 | 10008 | 215 | 0,93 | 2,30 | 6,29 | 0,19 |
| 9 | 10009 | 187 | 0,88 | 2,92 | 5,58 | 0,15 |
| 10 | 10010 | 222 | 0,88 | 1,91 | 5,24 | 0,33 |
| 11 | 10011 | 221 | 0,73 | 2,09 | 2,91 | 0,11 |
| 12 | 10012 | 231 | 0,33 | 1,45 | 8,04 | 0,18 |
| 13 | 10013 | 208 | 0,70 | 2,06 | 6,49 | 0,13 |
| 14 | 10014 | 210 | 1,42 | 4,05 | 7,00 | 0,48 |
| 15 | 10015 | 200 | 0,31 | 0,82 | 2,49 | 0,08 |
| 16 | 10016 | 208 | 0,67 | 5,91 | 5,63 | 0,10 |
| 17 | 10017 | 223 | 1,01 | 2,98 | 7,36 | 0,19 |
| 18 | 10018 | 198 | 0,33 | 0,80 | 3,39 | 0,10 |
| 19 | 10019 | 201 | 0,81 | 2,44 | 7,05 | 0,21 |
| 20 | 10020 | 212 | 1,05 | 5,19 | 6,04 | 0,16 |
| 21 | 10021 | 199 | 0,61 | 2,05 | 3,84 | 0,07 |
| 22 | 10022 | 190 | 0,60 | 1,72 | 3,29 | 0,12 |
| 23 | 10023 | 203 | 1,42 | 4,02 | 11,41 | 0,64 |
| 24 | 10024 | 202 | 0,92 | 1,78 | 9,04 | 0,19 |
| 25 | 10025 | 214 | 1,59 | 7,23 | 3,38 | 0,73 |
| 26 | 10026 | 201 | 0,39 | 1,02 | 2,60 | 0,05 |
| 27 | 10027 | 184 | 0,69 | 7,78 | 2,23 | 0,20 |
| 28 | 10028 | 183 | 0,56 | 1,30 | 7,43 | 0,03 |
| 29 | 10029 | 213 | 1,75 | 4,42 | 16,20 | 0,57 |
| 30 | 10030 | 207 | 1,03 | 2,22 | 3,32 | 0,37 |

| Escenario | Espera media diaria (min) | Desviación estándar (min) | Intervalo de confianza aproximado del 95 % (min) |
|---|---:|---:|---:|
| 3 cajas mixtas | 0,815 | 0,402 | 0,665 a 0,965 |
| 2R + 1P | 3,044 | 1,961 | 2,311 a 3,776 |
| 1R + 2P | 5,389 | 3,091 | 4,235 a 6,543 |
| 4 cajas mixtas | 0,225 | 0,195 | 0,152 a 0,298 |

El resumen es el promedio de los 30 promedios diarios, con igual peso para cada jornada; por ello no debe confundirse con el promedio global ponderado por usuario de las diez réplicas iniciales. Los intervalos aproximados usan la distribución t de Student con 29 grados de libertad y la variabilidad entre réplicas. La tabla muestra valores redondeados; los cálculos emplean la precisión completa.

La diferencia pareada entre tres y cuatro cajas mixtas fue de 0,590 minutos por usuario en promedio, con un intervalo aproximado del 95 % de 0,498 a 0,682 minutos. Esa reducción equivale aproximadamente al 72 % de la espera media diaria con tres cajas. Se trata de un resultado para el modelo y las condiciones simuladas; no es una evaluación de costos ni una simulación de cajero electrónico.
