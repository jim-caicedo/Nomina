"""
Controlador de liquidación de nómina.
Maneja el cálculo y persistencia de liquidaciones de nómina.
"""
from typing import Dict, Optional
from datetime import date
from models.domain.empleado import Empleado
from models.domain.nomina import RegistroNomina
from models.domain.configuracion import ConfiguracionNomina
from models.domain.conceptos.registro_concepto import RegistroConceptoNomina
from models.repositories.sqlite.empleado_repository_sqlite import EmpleadoRepositorySQLite
from models.repositories.sqlite.nomina_repository_sqlite import NominaRepositorySQLite
from models.repositories.sqlite.concepto_repository_sqlite import RegistroConceptoRepositorySQLite
from models.services.calculadora_nomina import CalculadoraNomina
from controllers.configuracion_controller import ConfiguracionController
from database.db_manager import DBManager


class NominaController:
    """Controlador para liquidación de nómina quincenal."""
    
    def __init__(self):
        """Inicializa el controlador con repositorios y servicios."""
        db = DBManager()
        self.repo_empleados = EmpleadoRepositorySQLite(db)
        self.repo_nomina = NominaRepositorySQLite(db)
        self.repo_registro_conceptos = RegistroConceptoRepositorySQLite(db)
        self.config_controller = ConfiguracionController()

    def liquidar_nomina_periodo(
        self,
        fecha_inicio: date,
        fecha_cierre: date,
        dias_laborados: int,
        horas_extras: int = 0,
    ) -> Dict[str, object]:
        """
        Liquida nómina para todos los empleados activos en un período.
        Guarda los registros en SQLite para persistencia.
        """
        try:
            # Validar período
            if not CalculadoraNomina.validar_periodo(fecha_inicio, fecha_cierre):
                return {
                    "success": False,
                    "error": "La fecha de inicio debe ser anterior a la fecha de cierre.",
                }

            # Obtener todos los empleados
            empleados = self.repo_empleados.obtener_todos()
            if not empleados:
                return {"success": False, "error": "No hay empleados registrados."}

            # Obtener configuración actual
            config_actual = self.config_controller.obtener_configuracion_obj()

            # Calcular nómina para cada empleado
            registros_liquidados = []
            total_devengado = 0.0
            total_deducciones = 0.0
            total_neto = 0.0

            for empleado in empleados:
                try:
                    # Calcular nómina usando el servicio con configuración actual
                    calculadora = CalculadoraNomina(config_actual)
                    calculos = calculadora.liquidar(
                        empleado=empleado,
                        fecha_inicio=fecha_inicio,
                        fecha_cierre=fecha_cierre,
                        dias_laborados=dias_laborados,
                        horas_extras=horas_extras,
                    )
                    calculos_dict = calculos.to_dict()

                    # Crear registro de nómina
                    registro = RegistroNomina(
                        id=0,  # Se asigna en el repositorio
                        empleado_id=empleado.id,
                        periodo_inicio=fecha_inicio,
                        periodo_cierre=fecha_cierre,
                        dias_laborados=dias_laborados,
                        salario_base_periodo=calculos_dict["salario_base_periodo"],
                        auxilio_transporte_periodo=calculos_dict["auxilio_transporte"],
                        horas_extras=horas_extras,
                        valor_horas_extras=calculos_dict["horas_extras"],
                        total_devengado=calculos_dict["total_devengado"],
                        descuento_afp=calculos_dict["descuento_afp"],
                        descuento_eps=calculos_dict["descuento_eps"],
                        otros_descuentos=calculos_dict["otros_descuentos"],
                        total_deducciones=calculos_dict["total_deducciones"],
                        salario_neto=calculos_dict["salario_neto"],
                    )

                    # Guardar registro en SQLite
                    registro_guardado = self.repo_nomina.guardar_registro(registro)
                    registros_liquidados.append(registro_guardado)

                    # Guardar desglose de conceptos aplicados (si los hay)
                    conceptos_aplicados = calculos_dict.get("conceptos_aplicados", [])
                    for c in conceptos_aplicados:
                        try:
                            reg_c = RegistroConceptoNomina(
                                id=0,
                                registro_nomina_id=registro_guardado.id,
                                concepto_nombre=c.get("nombre", ""),
                                tipo=c.get("tipo", ""),
                                naturaleza=c.get("naturaleza", "devengado"),
                                valor_calculado=c.get("valor", 0.0),
                                metadata=None,
                            )
                            self.repo_registro_conceptos.crear(reg_c)
                        except Exception as e:
                            print(f"Error guardando registro de concepto: {e}")
                    
                    # Acumular totales
                    total_devengado += calculos_dict["total_devengado"]
                    total_deducciones += calculos_dict["total_deducciones"]
                    total_neto += calculos_dict["salario_neto"]

                except ValueError as e:
                    return {
                        "success": False,
                        "error": f"Error al calcular nómina de {empleado.get_nombre_completo()}: {str(e)}",
                    }

            # Retornar resultado exitoso
            return {
                "success": True,
                "registros": [r.to_dict() for r in registros_liquidados],
                "cantidad_empleados": len(registros_liquidados),
                "total_devengado": round(total_devengado, 2),
                "total_deducciones": round(total_deducciones, 2),
                "total_neto": round(total_neto, 2),
            }

        except Exception as e:
            return {"success": False, "error": f"Error general: {str(e)}"}
