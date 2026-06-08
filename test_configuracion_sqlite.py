"""
Pruebas unitarias para el módulo de configuración SQLite.
Valida la migración de JSON a SQLite.
"""

import unittest
import os
import tempfile
from datetime import datetime
from models.configuracion import ConfiguracionNomina
from models.configuracion_repository import ConfiguracionRepositorySQLite
from controllers.configuracion_controller import ConfiguracionController


class TestConfiguracionSQLite(unittest.TestCase):
    """Suite de pruebas para ConfiguracionRepositorySQLite."""

    def setUp(self):
        """Preparar cada prueba."""
        # Usar BD en memoria para pruebas
        self.repo = ConfiguracionRepositorySQLite()

    def test_obtener_configuracion_actual(self):
        """Prueba obtener configuración activa."""
        config = self.repo.obtener_configuracion_actual()
        
        self.assertIsNotNone(config)
        self.assertEqual(config.anio_vigente, 2026)
        self.assertTrue(config.activa)
        self.assertEqual(config.salario_minimo_mensual, 1315000.0)

    def test_guardar_nueva_configuracion(self):
        """Prueba guardar nueva configuración."""
        config_nueva = ConfiguracionNomina(
            id=None,
            anio_vigente=2027,
            salario_minimo_mensual=1400000.0,
            auxilio_transporte_mensual=165000.0,
            porcentaje_afp=0.04,
            porcentaje_eps=0.04,
            fecha_creacion=None,
            activa=True
        )
        
        resultado = self.repo.guardar_configuracion(config_nueva)
        
        self.assertIsNotNone(resultado)
        self.assertEqual(resultado.anio_vigente, 2027)
        self.assertTrue(resultado.activa)

    def test_historial_configuraciones(self):
        """Prueba obtener historial de configuraciones."""
        # Agregar nueva configuración
        config_nueva = ConfiguracionNomina.crear_default_2026()
        config_nueva.anio_vigente = 2027
        self.repo.guardar_configuracion(config_nueva)
        
        # Obtener historial
        historial = self.repo.obtener_historial()
        
        self.assertGreater(len(historial), 1)
        # La más reciente debe estar activa
        self.assertTrue(historial[0].activa)
        # Las anteriores deben estar inactivas
        for config in historial[1:]:
            self.assertFalse(config.activa)

    def test_historial_cambios(self):
        """Prueba que se registran los cambios."""
        config_anterior = self.repo.obtener_configuracion_actual()
        
        config_nueva = ConfiguracionNomina(
            id=None,
            anio_vigente=2027,
            salario_minimo_mensual=1400000.0,  # Cambio
            auxilio_transporte_mensual=165000.0,  # Cambio
            porcentaje_afp=0.04,
            porcentaje_eps=0.04,
            fecha_creacion=None,
            activa=True
        )
        
        self.repo.guardar_configuracion(config_nueva)
        cambios = self.repo.obtener_historial_cambios()
        
        # Debe haber al menos 2 cambios registrados
        self.assertGreater(len(cambios), 0)
        
        # Verificar que se registraron los campos correctos
        campos_cambiados = [c["campo_cambiado"] for c in cambios]
        self.assertIn("salario_minimo_mensual", campos_cambiados)
        self.assertIn("auxilio_transporte_mensual", campos_cambiados)


class TestConfiguracionController(unittest.TestCase):
    """Suite de pruebas para ConfiguracionController."""

    def setUp(self):
        """Preparar cada prueba."""
        self.controller = ConfiguracionController()

    def test_cargar_configuracion(self):
        """Prueba cargar configuración actual."""
        resultado = self.controller.cargar_configuracion()
        
        self.assertTrue(resultado["success"])
        self.assertIn("config", resultado)
        config = resultado["config"]
        self.assertEqual(config["anio_vigente"], 2026)

    def test_guardar_configuracion_valida(self):
        """Prueba guardar configuración válida."""
        resultado = self.controller.guardar_configuracion(
            anio=2027,
            salario_minimo=1400000,
            auxilio_transporte=165000,
            porcentaje_afp=0.04,
            porcentaje_eps=0.04
        )
        
        self.assertTrue(resultado["success"])
        self.assertIn("mensaje", resultado)

    def test_guardar_configuracion_invalida_anio(self):
        """Prueba guardar configuración con año inválido."""
        resultado = self.controller.guardar_configuracion(
            anio=2000,  # Inválido (< 2020)
            salario_minimo=1400000,
            auxilio_transporte=165000,
            porcentaje_afp=0.04,
            porcentaje_eps=0.04
        )
        
        self.assertFalse(resultado["success"])
        self.assertIn("error", resultado)

    def test_guardar_configuracion_invalida_salario(self):
        """Prueba guardar configuración con salario negativo."""
        resultado = self.controller.guardar_configuracion(
            anio=2027,
            salario_minimo=-1400000,  # Inválido
            auxilio_transporte=165000,
            porcentaje_afp=0.04,
            porcentaje_eps=0.04
        )
        
        self.assertFalse(resultado["success"])

    def test_convertir_porcentajes(self):
        """Prueba que convierte porcentajes correctamente."""
        # Si usuario ingresa 4 en lugar de 0.04, debe convertir
        resultado = self.controller.guardar_configuracion(
            anio=2027,
            salario_minimo=1400000,
            auxilio_transporte=165000,
            porcentaje_afp=4,  # Se debe convertir a 0.04
            porcentaje_eps=4
        )
        
        self.assertTrue(resultado["success"])

    def test_obtener_historial(self):
        """Prueba obtener historial de configuraciones."""
        historial = self.controller.obtener_historial_configuraciones()
        
        self.assertIsInstance(historial, list)
        self.assertGreater(len(historial), 0)

    def test_obtener_cambios(self):
        """Prueba obtener historial de cambios."""
        cambios = self.controller.obtener_historial_cambios()
        
        self.assertIsInstance(cambios, list)

    def test_restaurar_defaults(self):
        """Prueba restaurar valores por defecto."""
        resultado = self.controller.restaurar_defaults_2026()
        
        self.assertTrue(resultado["success"])
        config = resultado["config"]
        self.assertEqual(config["anio_vigente"], 2026)
        self.assertEqual(config["salario_minimo_mensual"], 1315000.0)


class TestConfiguracionNomina(unittest.TestCase):
    """Pruebas para el modelo ConfiguracionNomina."""

    def test_crear_default_2026(self):
        """Prueba crear configuración por defecto."""
        config = ConfiguracionNomina.crear_default_2026()
        
        self.assertEqual(config.anio_vigente, 2026)
        self.assertEqual(config.salario_minimo_mensual, 1315000.0)
        self.assertEqual(config.auxilio_transporte_mensual, 161916.0)
        self.assertEqual(config.porcentaje_afp, 0.04)
        self.assertEqual(config.porcentaje_eps, 0.04)

    def test_validar_configuracion_valida(self):
        """Prueba validar configuración válida."""
        config = ConfiguracionNomina.crear_default_2026()
        es_valida, mensaje = config.validar()
        
        self.assertTrue(es_valida)

    def test_validar_configuracion_salario_negativo(self):
        """Prueba validar configuración con salario negativo."""
        config = ConfiguracionNomina(
            anio_vigente=2026,
            salario_minimo_mensual=-1000000,  # Inválido
            auxilio_transporte_mensual=161916,
            porcentaje_afp=0.04,
            porcentaje_eps=0.04
        )
        
        es_valida, mensaje = config.validar()
        self.assertFalse(es_valida)

    def test_validar_configuracion_afp_invalida(self):
        """Prueba validar configuración con AFP fuera de rango."""
        config = ConfiguracionNomina(
            anio_vigente=2026,
            salario_minimo_mensual=1315000,
            auxilio_transporte_mensual=161916,
            porcentaje_afp=0.50,  # Inválido (> 0.1)
            porcentaje_eps=0.04
        )
        
        es_valida, mensaje = config.validar()
        self.assertFalse(es_valida)


if __name__ == "__main__":
    # Ejecutar pruebas
    suite = unittest.TestLoader().loadTestsFromModule(__import__(__name__))
    runner = unittest.TextTestRunner(verbosity=2)
    resultado = runner.run(suite)
    
    # Imprimir resumen
    print("\n" + "="*60)
    if resultado.wasSuccessful():
        print("✓ TODAS LAS PRUEBAS PASARON")
    else:
        print(f"✗ {len(resultado.failures)} fallos, {len(resultado.errors)} errores")
    print("="*60)
