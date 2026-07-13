"""
Controlador de liquidación de nómina.
Maneja el cálculo y persistencia de liquidaciones de nómina enlazado a Períodos.
"""
from typing import Dict, Optional, List
from datetime import date, datetime
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
    """Controlador para liquidación de nómina quincenal enlazado a Periodos."""

    def __init__(self):
        """Inicializa el controlador con repositorios y servicios."""
        db = DBManager()
        self.db = db
        self.repo_empleados = EmpleadoRepositorySQLite(db)
        self.repo_nomina = NominaRepositorySQLite(db)
        self.repo_registro_conceptos = RegistroConceptoRepositorySQLite(db)
        self.config_controller = ConfiguracionController()

    def obtener_periodo_por_id(self, periodo_id: object) -> Optional[Dict[str, object]]:
        """Obtiene un período por su ID o fecha."""
        try:
            cursor = self.db.get_connection().cursor()

            # Caso 1: La interfaz envió una fecha en formato string o un objeto date/datetime
            if isinstance(periodo_id, (date, str)):
                fecha_str = periodo_id.strftime("%Y-%m-%d") if isinstance(periodo_id, date) else str(periodo_id)
                # Intentamos buscar el periodo que contenga o coincida con esta fecha de inicio
                cursor.execute(
                    "SELECT id, fecha_inicio, fecha_fin, estado FROM periodos_nomina WHERE fecha_inicio = ? OR ? BETWEEN fecha_inicio AND fecha_fin",
                    (fecha_str, fecha_str)
                )
            else:
                # Caso 2: Recibió el ID numérico clásico esperado
                cursor.execute(
                    "SELECT id, fecha_inicio, fecha_fin, estado FROM periodos_nomina WHERE id = ?", 
                    (periodo_id,)
                )

            row = cursor.fetchone()
            if row:
                f_inicio = datetime.strptime(row[1], "%Y-%m-%d").date() if isinstance(row[1], str) else row[1]
                f_cierre = datetime.strptime(row[2], "%Y-%m-%d").date() if isinstance(row[2], str) else row[2]
                return {
                    "id": row[0],
                    "fecha_inicio": f_inicio,
                    "fecha_cierre": f_cierre,
                    "estado": row[3]
                }
            return None
        except Exception as e:
            print(f"Error al obtener período ({periodo_id}) desde el controlador: {e}")
            return None

    def exportar_nomina_excel(
        self,
        periodo_id: int,
        ruta_archivo: str,
    ) -> Dict[str, object]:
        """
        Exporta a Excel los registros de nómina ya liquidados y guardados
        en SQLite pertenecientes a un periodo_id específico.
        """
        try:
            # Validar que el periodo exista primero
            periodo = self.obtener_periodo_por_id(periodo_id)
            if not periodo:
                return {"success": False, "error": "El período especificado no existe para exportar."}

            # Consultar los registros guardados bajo este periodo
            registros = self.repo_nomina.obtener_por_periodo_id(periodo_id)

            if not registros:
                return {
                    "success": False,
                    "error": "No hay registros de nómina guardados para este período. Calcula la nómina antes.",
                }

            # Si el período sufrió re-cálculos, conservamos solo el último registro por empleado
            mas_reciente_por_empleado: Dict[int, object] = {}
            for registro in registros:
                actual = mas_reciente_por_empleado.get(registro.empleado_id)
                if actual is None or (registro.fecha_liquidacion and actual.fecha_liquidacion and registro.fecha_liquidacion > actual.fecha_liquidacion):
                    mas_reciente_por_empleado[registro.empleado_id] = registro
            registros = list(mas_reciente_por_empleado.values())

            from utils.excel_exporter import exportar_nomina_a_excel

            # Enviamos los objetos limpios junto con las fechas recuperadas del Periodo
            exportar_nomina_a_excel(registros, periodo["fecha_inicio"], periodo["fecha_cierre"], ruta_archivo)

            return {"success": True, "mensaje": "Nómina exportada exitosamente a Excel."}

        except ImportError:
            return {
                "success": False,
                "error": "openpyxl no está instalado en el entorno virtual. Ejecuta: pip install openpyxl",
            }
        except Exception as e:
            return {"success": False, "error": f"Error al exportar a Excel: {str(e)}"}

    def liquidar_nomina_periodo(
        self,
        periodo_id: object,
        dias_laborados: Optional[int] = None,
        horas_extras: int = 0,
    ) -> Dict[str, object]:
        """
        Liquida nómina para todos los empleados activos usando un periodo_id válido o fecha mapeable.
        Valida que el período esté ABIERTO antes de proceder para evitar duplicados.
        """
        try:
            # 1. Obtener datos del Periodo mapeándolo dinámicamente
            periodo = self.obtener_periodo_por_id(periodo_id)
            if not periodo:
                return {"success": False, "error": f"El período referenciado por '{periodo_id}' no existe en la base de datos."}

            if periodo["estado"] == "CERRADO":
                return {
                    "success": False, 
                    "error": "Este período ya se encuentra CERRADO y congelado. No se puede volver a liquidar."
                }

            # Extraemos el ID real resuelto y sus fechas físicas
            id_real_periodo = periodo["id"]
            fecha_inicio = periodo["fecha_inicio"]
            fecha_cierre = periodo["fecha_cierre"]

            # 2. Validar consistencia matemática de las fechas
            if not CalculadoraNomina.validar_periodo(fecha_inicio, fecha_cierre):
                return {
                    "success": False,
                    "error": "La fecha de inicio del período debe ser anterior a la fecha de cierre.",
                }

            # Si no se especifican días, se derivan del rango del período de forma automática
            if dias_laborados is None:
                dias_laborados = CalculadoraNomina.calcular_dias_laborados(fecha_inicio, fecha_cierre)

            # 3. Obtener empleados activos
            empleados = self.repo_empleados.obtener_todos()
            if not empleados:
                return {"success": False, "error": "No hay empleados registrados."}

            # Obtener configuración legal vigente (2026)
            config_actual = self.config_controller.obtener_configuracion_obj()

            registros_liquidados = []
            total_devengado = 0.0
            total_deducciones = 0.0
            total_neto = 0.0

            # 4. Procesar cálculo individualmente por empleado
            for empleado in empleados:
                try:
                    calculadora = CalculadoraNomina(config_actual)
                    calculos = calculadora.liquidar(
                        empleado=empleado,
                        fecha_inicio=fecha_inicio,
                        fecha_cierre=fecha_cierre,
                        dias_laborados=dias_laborados,
                        horas_extras=horas_extras,
                    )
                    calculos_dict = calculos.to_dict()

                    # Instanciar el modelo de dominio con la clave foránea real resuelta
                    registro = RegistroNomina(
                        id=0,  
                        empleado_id=empleado.id,
                        periodo_id=id_real_periodo,
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

                    # Guardar el encabezado de nómina en SQLite sin conflictos de columnas
                    registro_guardado = self.repo_nomina.guardar_registro(registro)
                    registros_liquidados.append(registro_guardado)

                    # Guardar el desglose histórico de conceptos aplicados por empleado
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
                            print(f"Error guardando registro de concepto desglosado: {e}")

                    # Sumatoria global del período
                    total_devengado += calculos_dict["total_devengado"]
                    total_deducciones += calculos_dict["total_deducciones"]
                    total_neto += calculos_dict["salario_neto"]

                except ValueError as e:
                    return {
                        "success": False,
                        "error": f"Error al calcular nómina de {empleado.get_nombre_completo()}: {str(e)}",
                    }

            return {
                "success": True,
                "registros": [r.to_dict() for r in registros_liquidados],
                "cantidad_empleados": len(registros_liquidados),
                "total_devengado": round(total_devengado, 2),
                "total_deducciones": round(total_deducciones, 2),
                "total_neto": round(total_neto, 2),
            }

        except Exception as e:
            return {"success": False, "error": f"Error general en NominaController: {str(e)}"}
    