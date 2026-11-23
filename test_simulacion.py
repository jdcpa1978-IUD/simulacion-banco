import unittest

from simulacion_banco import Cliente, ESCENARIOS, generar_clientes, simular
from analisis_adicional import ESCENARIOS_ANEXO, estadisticas


class PruebasSimulacion(unittest.TestCase):
    def test_llegadas_reproducibles_y_dentro_del_horario(self):
        clientes = generar_clientes(2027)
        self.assertEqual(clientes, generar_clientes(2027))
        self.assertTrue(clientes)
        self.assertTrue(all(0 <= c.llegada <= 480 for c in clientes))
        self.assertEqual(sorted(c.llegada for c in clientes), [c.llegada for c in clientes])

    def test_cola_fifo_y_atencion_posterior_al_cierre(self):
        clientes = [
            Cliente(479, "Retiro", "Rapido", 5),
            Cliente(479.5, "Retiro", "Normal", 2),
        ]
        atendidos = simular(clientes, ("Retiro", "Pago"))
        self.assertEqual([a.inicio for a in atendidos], [479, 484])
        self.assertEqual(atendidos[1].espera, 4.5)
        self.assertEqual(atendidos[1].fin, 486)

    def test_cajas_exclusivas_y_conservacion_de_clientes(self):
        clientes = generar_clientes(2027)
        for configuracion in ESCENARIOS.values():
            atendidos = simular(clientes, configuracion)
            self.assertEqual(len(atendidos), len(clientes))
            for atencion in atendidos:
                rol = configuracion[atencion.cajero - 1]
                self.assertIn(rol, ("Mixta", atencion.cliente.accion))
                self.assertGreaterEqual(atencion.espera, 0)

    def test_rechaza_configuracion_sin_pagos(self):
        with self.assertRaises(ValueError):
            simular([], ("Retiro",))

    def test_cuatro_cajas_mixtas_conservan_los_clientes(self):
        clientes = generar_clientes(10001)
        atenciones = simular(clientes, ESCENARIOS_ANEXO["4 mixtas"])
        self.assertEqual(len(clientes), len(atenciones))
        self.assertTrue(all(1 <= a.cajero <= 4 for a in atenciones))

    def test_intervalo_confianza_con_valores_constantes(self):
        self.assertEqual(estadisticas([2.0] * 30), (2.0, 0.0, 2.0, 2.0))
        with self.assertRaises(ValueError):
            estadisticas([2.0] * 10)


if __name__ == "__main__":
    unittest.main()
