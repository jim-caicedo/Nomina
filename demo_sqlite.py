"""
Script de demostración de la migración a SQLite.
Muestra cómo usar el sistema de configuración con persistencia.
"""

from datetime import datetime
from controllers.configuracion_controller import ConfiguracionController
from controllers.main_controller import MainController
from models.configuracion import ConfiguracionNomina

def demo_configuracion_sqlite():
    """Demostración completa del sistema de configuración con SQLite."""
    
    print("\n" + "="*60)
    print("DEMOSTRACIÓN: Sistema de Configuración SQLite")
    print("="*60 + "\n")
    
    # 1. Crear controlador de configuración
    config_ctrl = ConfiguracionController()
    print("✓ Controlador de configuración inicializado")
    
    # 2. Obtener configuración actual
    config_actual = config_ctrl.obtener_configuracion_obj()
    print(f"\n✓ Configuración Actual (2026):")
    print(f"  - SMMLV: ${config_actual.salario_minimo_mensual:,.0f}")
    print(f"  - Auxilio Transporte: ${config_actual.auxilio_transporte_mensual:,.0f}")
    print(f"  - AFP: {config_actual.porcentaje_afp * 100}%")
    print(f"  - EPS: {config_actual.porcentaje_eps * 100}%")
    print(f"  - Activa: {'Sí' if config_actual.activa else 'No'}")
    print(f"  - ID BD: {config_actual.id}")
    
    # 3. Guardar nueva configuración (simulando año siguiente)
    print("\n✓ Guardando nueva configuración para 2027...")
    resultado = config_ctrl.guardar_configuracion(
        anio=2027,
        salario_minimo=1400000,
        auxilio_transporte=170000,
        porcentaje_afp=0.04,
        porcentaje_eps=0.04
    )
    
    if resultado["success"]:
        print(f"  ✓ {resultado['mensaje']}")
    else:
        print(f"  ✗ Error: {resultado['error']}")
    
    # 4. Obtener nueva configuración activa
    config_nueva = config_ctrl.obtener_configuracion_obj()
    print(f"\n✓ Nueva Configuración Activa:")
    print(f"  - SMMLV: ${config_nueva.salario_minimo_mensual:,.0f}")
    print(f"  - Auxilio Transporte: ${config_nueva.auxilio_transporte_mensual:,.0f}")
    print(f"  - ID BD: {config_nueva.id}")
    
    # 5. Ver historial de configuraciones
    historial = config_ctrl.obtener_historial_configuraciones()
    print(f"\n✓ Historial de Configuraciones ({len(historial)} registros):")
    for i, config in enumerate(historial, 1):
        estado = "Activa" if config["activa"] else "Inactiva"
        print(f"  {i}. Año {config['anio_vigente']} - {estado}")
        print(f"     SMMLV: ${config['salario_minimo_mensual']:,.0f}")
        print(f"     Fecha: {config['fecha_creacion']}")
    
    # 6. Ver historial de cambios
    cambios = config_ctrl.obtener_historial_cambios()
    print(f"\n✓ Historial de Cambios ({len(cambios)} registros):")
    for cambio in cambios:
        print(f"  - Campo: {cambio['campo_cambiado']}")
        print(f"    Anterior: {cambio['valor_anterior']}")
        print(f"    Nuevo: {cambio['valor_nuevo']}")
        print(f"    Fecha: {cambio['fecha_cambio']}")
        print()
    
    # 7. Demostrar integración con MainController
    print("\n" + "="*60)
    print("INTEGRACIÓN CON NÓMINA")
    print("="*60 + "\n")
    
    main_ctrl = MainController()
    print("✓ MainController inicializado")
    
    # Obtener configuración desde MainController
    config_en_nomina = main_ctrl.config_controller.obtener_configuracion_obj()
    print(f"\n✓ Configuración disponible en liquidación de nómina:")
    print(f"  - SMMLV: ${config_en_nomina.salario_minimo_mensual:,.0f}")
    print(f"  - Se usa en cálculos de nómina automáticamente")
    
    print("\n" + "="*60)
    print("✓ DEMOSTRACIÓN COMPLETADA")
    print("="*60 + "\n")

if __name__ == "__main__":
    demo_configuracion_sqlite()
