"""
Controlador para la gestión de Liquidaciones Finales de Contrato.
Orquesta la consulta de datos, cálculo y guardado.
"""
from datetime import date, datetime
from typing import Dict, Any, List, Optional

from models.services.calculadora_liquidacion import CalculadoraLiquidacionFinal, ResultadoLiquidacionFinal
from models.repositories.sqlite.liquidacion_repository_sqlite import LiquidacionRepositorySQLite
from models.domain.liquidacion import LiquidacionFinal


class LiquidacionController:
    def __init__(
        self,
        empleado_controller,        # EmpleadoController — interfaz pública
        liquidacion_repo: LiquidacionRepositorySQLite,
        config_controller,          # ConfiguracionController — interfaz pública
    ):
        self.empleado_controller = empleado_controller
        self.liquidacion_repo = liquidacion_repo
        self.config_controller = config_controller

    def obtener_empleados_activos(self) -> List[Dict[str, Any]]:
        """Devuelve empleados activos para el selector de la UI."""
        # listar_empleados() ya filtra activo=1 en el repositorio
        empleados = self.empleado_controller.listar_empleados()
        return [
            {
                "id": e["id"],
                "nombre_completo": e["nombre_completo"],
                "cedula": e.get("cedula", ""),
                "salario": e["salario"],
                "fecha_ingreso": str(e.get("fecha_ingreso", date.today())),
            }
            for e in empleados
        ]

    def calcular_previsualizacion(
        self,
        empleado_id: int,
        fecha_retiro_str: str,
        motivo_retiro: str,
        dias_vacaciones_tomadas: float = 0.0,
        deducciones_varias: float = 0.0,
    ) -> Dict[str, Any]:
        """Simula la liquidación y retorna dict para la UI."""
        # buscar_empleado devuelve el objeto Empleado directamente
        empleado = self.empleado_controller.buscar_empleado(empleado_id)
        if not empleado:
            raise ValueError("Empleado no encontrado.")

        # obtener_configuracion_obj() devuelve ConfiguracionNomina
        config = self.config_controller.obtener_configuracion_obj()
        calculadora = CalculadoraLiquidacionFinal(config)

        try:
            fecha_retiro = datetime.strptime(fecha_retiro_str, "%Y-%m-%d").date()
        except ValueError:
            raise ValueError("Formato de fecha inválido. Usar YYYY-MM-DD.")

        # Sumar horas extras pagadas en el período para base prestacional
        inicio_evaluacion = date(fecha_retiro.year, 1, 1)
        total_he = self.liquidacion_repo.obtener_sumatoria_horas_extras_y_variables(
            empleado_id, inicio_evaluacion, fecha_retiro
        )
        meses_evaluados = max(1, fecha_retiro.month - inicio_evaluacion.month + 1)
        promedio_variables = total_he / meses_evaluados

        resultado: ResultadoLiquidacionFinal = calculadora.liquidar_final(
            empleado=empleado,
            fecha_retiro=fecha_retiro,
            motivo_retiro=motivo_retiro,
            dias_vacaciones_tomadas=dias_vacaciones_tomadas,
            promedio_variables=promedio_variables,
            deducciones_varias=deducciones_varias,
        )

        return {
            "empleado_id": empleado.id,
            "empleado_nombre": empleado.get_nombre_completo(),
            "fecha_ingreso": str(getattr(empleado, "fecha_ingreso", "N/A")),
            "fecha_retiro": str(fecha_retiro),
            "dias_totales": resultado.dias_totales_trabajados,
            "dias_cesantias": resultado.dias_cesantias,
            "dias_prima": resultado.dias_prima,
            "dias_vacaciones": resultado.dias_vacaciones,
            "salario_base": resultado.salario_base,
            "auxilio_transporte": resultado.auxilio_transporte,
            "base_prestaciones": resultado.base_prestaciones,
            "promedio_variables": round(promedio_variables, 2),
            "valor_cesantias": resultado.valor_cesantias,
            "valor_intereses": resultado.valor_intereses_cesantias,
            "valor_prima": resultado.valor_prima,
            "valor_vacaciones": resultado.valor_vacaciones,
            "valor_indemnizacion": resultado.valor_indemnizacion,
            "total_devengado": resultado.total_devengado,
            "total_deducciones": resultado.total_deducciones,
            "neto_a_pagar": resultado.neto_a_pagar,
            "motivo_retiro": resultado.motivo_retiro,
        }

    def procesar_y_guardar(self, datos_calculados: Dict[str, Any]) -> bool:
        """Guarda la liquidación aprobada y desactiva al empleado."""
        try:
            liquidacion = LiquidacionFinal(
                id=None,
                empleado_id=datos_calculados["empleado_id"],
                fecha_liquida=date.today(),
                fecha_retiro=datetime.strptime(
                    datos_calculados["fecha_retiro"], "%Y-%m-%d"
                ).date(),
                motivo_retiro=datos_calculados["motivo_retiro"],
                dias_totales_trabajados=datos_calculados["dias_totales"],
                salario_base=datos_calculados["salario_base"],
                promedio_variables=datos_calculados["promedio_variables"],
                auxilio_transporte=datos_calculados["auxilio_transporte"],
                base_prestaciones=datos_calculados["base_prestaciones"],
                valor_cesantias=datos_calculados["valor_cesantias"],
                valor_intereses_cesantias=datos_calculados["valor_intereses"],
                valor_prima=datos_calculados["valor_prima"],
                valor_vacaciones=datos_calculados["valor_vacaciones"],
                valor_indemnizacion=datos_calculados["valor_indemnizacion"],
                total_devengado=datos_calculados["total_devengado"],
                total_deducciones=datos_calculados["total_deducciones"],
                neto_a_pagar=datos_calculados["neto_a_pagar"],
                estado="PROCESADO",
            )
            self.liquidacion_repo.guardar(liquidacion)
            return True
        except Exception as e:
            print(f"Error al guardar liquidación: {e}")
            return False