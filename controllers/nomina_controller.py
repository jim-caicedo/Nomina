"""
Controlador de liquidación de nómina.
Maneja el cálculo y persistencia de liquidaciones de nómina.
"""
import os
from typing import Dict, List, Optional
from datetime import date
from models.domain.empleado import Empleado
from models.domain.nomina import RegistroNomina, ItemConcepto
from models.domain.configuracion import ConfiguracionNomina
from models.domain.concepto import RegistroConceptoNomina           # fix: ruta correcta
from models.repositories.sqlite.empleado_repository_sqlite import EmpleadoRepositorySQLite
from models.repositories.sqlite.nomina_repository_sqlite import NominaRepositorySQLite
from models.repositories.sqlite.concepto_repository_sqlite import (
    ConceptoEmpleadoRepositorySQLite,
    RegistroConceptoRepositorySQLite,
)
from models.services.calculadora_nomina import CalculadoraNomina
from controllers.configuracion_controller import ConfiguracionController
from database.db_manager import DBManager


class NominaController:
    """Controlador para liquidación de nómina quincenal."""

    def __init__(self):
        db = DBManager()
        self.repo_empleados = EmpleadoRepositorySQLite(db)
        self.repo_nomina = NominaRepositorySQLite(db)
        self.repo_conceptos_emp = ConceptoEmpleadoRepositorySQLite(db)       # fix: faltaba
        self.repo_registro_conceptos = RegistroConceptoRepositorySQLite(db)
        self.config_controller = ConfiguracionController()

    # ------------------------------------------------------------------
    # helpers privados
    # ------------------------------------------------------------------

    def _obtener_conceptos_empleado(self, empleado_id: int) -> List[ItemConcepto]:
        """
        Consulta los conceptos asignados al empleado y los convierte a
        ItemConcepto para que CalculadoraNomina los sume/reste.
        Solo incluye conceptos con valor definido (fijo o porcentaje ya
        resuelto); los de tipo 'variable' sin valor se omiten con aviso.
        """
        asignaciones = self.repo_conceptos_emp.obtener_por_empleado(empleado_id)
        items: List[ItemConcepto] = []

        for a in asignaciones:
            valor = None

            if a.tipo == "fijo":
                valor = a.valor_personalizado

            elif a.tipo == "porcentaje" and a.porcentaje_personalizado is not None:
                # porcentaje sobre salario — se resuelve aquí, no en la calculadora
                empleado = self.repo_empleados.obtener_por_id(empleado_id)
                if empleado:
                    valor = round(empleado.salario * (a.porcentaje_personalizado / 100), 2)

            elif a.tipo == "variable":
                # Sin valor ingresado manualmente en esta quincena → omitir
                print(f"Concepto variable '{a.nombre}' omitido (requiere valor manual)")
                continue

            if valor is None:
                print(f"Concepto '{a.nombre}' omitido (sin valor definido)")
                continue

            items.append(ItemConcepto(
                nombre=a.nombre,
                tipo=a.tipo,
                naturaleza=a.naturaleza,
                valor=round(valor, 2),
            ))

        return items

    # ------------------------------------------------------------------
    # liquidación
    # ------------------------------------------------------------------

    def liquidar_nomina_periodo(
        self,
        fecha_inicio: date,
        fecha_cierre: date,
        dias_laborados: Optional[int] = None,
        horas_extras: int = 0,
    ) -> Dict[str, object]:
        """
        Liquida nómina para todos los empleados activos en un período.

        - dias_laborados: si no se pasa, se calcula desde las fechas.
        - Los conceptos asignados a cada empleado se consultan aquí y se
          pasan a CalculadoraNomina para que los incluya en el resultado.
        - Los conceptos de tipo deducción NO afectan el total_devengado
          ni la base de AFP/EPS; solo reducen el salario neto (otros_descuentos).
        """
        try:
            if not CalculadoraNomina.validar_periodo(fecha_inicio, fecha_cierre):
                return {
                    "success": False,
                    "error": "La fecha de inicio debe ser anterior a la fecha de cierre.",
                }

            if dias_laborados is None:
                dias_laborados = CalculadoraNomina.calcular_dias_laborados(
                    fecha_inicio, fecha_cierre
                )

            empleados = self.repo_empleados.obtener_todos()
            if not empleados:
                return {"success": False, "error": "No hay empleados registrados."}

            config_actual = self.config_controller.obtener_configuracion_obj()
            calculadora = CalculadoraNomina(config_actual)

            registros_liquidados = []
            total_devengado = 0.0
            total_deducciones = 0.0
            total_neto = 0.0

            for empleado in empleados:
                try:
                    # fix principal: consultar conceptos del empleado
                    conceptos = self._obtener_conceptos_empleado(empleado.id)

                    calculos = calculadora.liquidar(
                        empleado=empleado,
                        fecha_inicio=fecha_inicio,
                        fecha_cierre=fecha_cierre,
                        dias_laborados=dias_laborados,
                        horas_extras=horas_extras,
                        conceptos_aplicados=conceptos,      # ← ahora se pasan
                    )
                    calculos_dict = calculos.to_dict()

                    registro = RegistroNomina(
                        id=0,
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

                    registro_guardado = self.repo_nomina.guardar_registro(registro)
                    registros_liquidados.append(registro_guardado)

                    # Guardar desglose de cada concepto aplicado
                    for c in calculos_dict.get("conceptos_aplicados", []):
                        try:
                            self.repo_registro_conceptos.crear(
                                RegistroConceptoNomina(
                                    id=0,
                                    registro_nomina_id=registro_guardado.id,
                                    concepto_nombre=c.get("nombre", ""),
                                    tipo=c.get("tipo", ""),
                                    naturaleza=c.get("naturaleza", "devengado"),
                                    valor_calculado=c.get("valor", 0.0),
                                    metadata=None,
                                )
                            )
                        except Exception as e:
                            print(f"Error guardando registro de concepto: {e}")

                    total_devengado += calculos_dict["total_devengado"]
                    total_deducciones += calculos_dict["total_deducciones"]
                    total_neto += calculos_dict["salario_neto"]

                except ValueError as e:
                    return {
                        "success": False,
                        "error": f"Error al calcular nómina de "
                                 f"{empleado.get_nombre_completo()}: {str(e)}",
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
            return {"success": False, "error": f"Error general: {str(e)}"}

    def exportar_nomina_excel(
        self,
        fecha_inicio: date,
        fecha_cierre: date,
        ruta_archivo: str,
    ) -> Dict[str, object]:
        """Exporta a Excel la liquidación más reciente y genera los desprendibles PDF por empleado."""
        try:
            registros = self.repo_nomina.obtener_por_periodo(fecha_inicio, fecha_cierre)
            if not registros:
                return {
                    "success": False,
                    "error": "No hay registros para este período. Calcula la nómina primero.",
                }

            # Quedarse solo con la liquidación más reciente por empleado
            mas_reciente: Dict[int, object] = {}
            for r in registros:
                actual = mas_reciente.get(r.empleado_id)
                if actual is None or r.fecha_liquidacion > actual.fecha_liquidacion:
                    mas_reciente[r.empleado_id] = r
            registros = list(mas_reciente.values())

            # 1. Crear la carpeta organizada de la quincena (Ej: "desprendibles/quincena_2026_07_15")
            fecha_corte_str = fecha_cierre.strftime("%Y_%m_%d")
            carpeta_quincena = os.path.join("desprendibles", f"quincena_{fecha_corte_str}")
            os.makedirs(carpeta_quincena, exist_ok=True)

            # 2. UNIÓN DE DATOS Y GENERACIÓN DE PDFs (Un solo bucle limpio)
            for r in registros:
                empleado_obj = self.repo_empleados.obtener_por_id(r.empleado_id)
                if empleado_obj:
                    r.empleado = empleado_obj  # Enlace del objeto para el Excel
                    
                    # --- GENERACIÓN DEL PDF INDIVIDUAL ---
                    try:
                        from utils.pdf_generator import generar_desprendible_pdf
                        
                        # Reemplazamos espacios por guiones bajos para el nombre del archivo
                        nombre_limpio = f"{empleado_obj.nombre}_{empleado_obj.apellido}".replace(" ", "_")
                        
                        # Formato: Nombre_Apellido_YYYY_MM_DD.pdf
                        nombre_archivo_pdf = f"{nombre_limpio}_{fecha_corte_str}.pdf"
                        ruta_final_pdf = os.path.join(carpeta_quincena, nombre_archivo_pdf)
                        
                        # Generar el PDF en su respectiva carpeta
                        generar_desprendible_pdf(r, ruta_pdf=ruta_final_pdf)
                        
                    except Exception as pdf_error:
                        print(f"Error generando PDF para {empleado_obj.nombre}: {pdf_error}")
                else:
                    # Fallback por seguridad si no encuentra el empleado en BD
                    r.empleado = None

            # 3. Exportación final al archivo de Excel unificado
            from utils.excel_exporter import exportar_nomina_a_excel
            exportar_nomina_a_excel(registros, fecha_inicio, fecha_cierre, ruta_archivo)
            
            return {"success": True, "mensaje": "Nómina y desprendibles PDF exportados exitosamente."}

        except ImportError:
            return {"success": False, "error": "openpyxl no instalado: pip install openpyxl"}
        except Exception as e:
            return {"success": False, "error": f"Error al exportar: {str(e)}"}