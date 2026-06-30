"""
Controlador de historial de nóminas.
Maneja la consulta de liquidaciones pasadas.
"""
from typing import List
from datetime import datetime
from models.repositories.sqlite.empleado_repository_sqlite import EmpleadoRepositorySQLite
from models.repositories.sqlite.nomina_repository_sqlite import NominaRepositorySQLite


class HistorialController:
    """Controlador para consulta de historial de nóminas."""
    
    def __init__(self):
        """Inicializa el controlador con repositorios."""
        self.repo_empleados = EmpleadoRepositorySQLite()
        self.repo_nomina = NominaRepositorySQLite()

    def obtener_historial_nominas(self) -> list:
        """
        Retorna todas las liquidaciones guardadas, agrupadas por período.
        Cada grupo contiene: periodo_inicio, periodo_cierre, cantidad_empleados,
        total_devengado, total_deducciones, total_neto, fecha_liquidacion.
        """
        try:
            todos = self.repo_nomina.obtener_todos()
            if not todos:
                return []

            # Agrupar por (periodo_inicio, periodo_cierre)
            grupos = {}
            for r in todos:
                clave = (r.periodo_inicio, r.periodo_cierre)
                if clave not in grupos:
                    grupos[clave] = {
                        "periodo_inicio": r.periodo_inicio.strftime("%d/%m/%Y"),
                        "periodo_cierre": r.periodo_cierre.strftime("%d/%m/%Y"),
                        "cantidad_empleados": 0,
                        "total_devengado": 0.0,
                        "total_deducciones": 0.0,
                        "total_neto": 0.0,
                        "fecha_liquidacion": r.fecha_liquidacion.strftime("%d/%m/%Y %H:%M") if r.fecha_liquidacion else "",
                    }
                grupos[clave]["cantidad_empleados"] += 1
                grupos[clave]["total_devengado"] += r.total_devengado
                grupos[clave]["total_deducciones"] += r.total_deducciones
                grupos[clave]["total_neto"] += r.salario_neto

            # Redondear totales y ordenar por fecha de cierre descendente
            resultado = []
            for clave, g in sorted(grupos.items(), key=lambda x: x[0][1], reverse=True):
                g["total_devengado"] = round(g["total_devengado"], 2)
                g["total_deducciones"] = round(g["total_deducciones"], 2)
                g["total_neto"] = round(g["total_neto"], 2)
                resultado.append(g)

            return resultado
        except Exception as e:
            print(f"Error al obtener historial de nóminas: {e}")
            return []

    def obtener_detalle_nomina_periodo(
        self, fecha_inicio_str: str, fecha_cierre_str: str
    ) -> list:
        """
        Retorna el detalle por empleado de una liquidación específica.
        Las fechas deben estar en formato DD/MM/YYYY.
        """
        try:
            fmt = "%d/%m/%Y"
            fecha_inicio = datetime.strptime(fecha_inicio_str, fmt).date()
            fecha_cierre = datetime.strptime(fecha_cierre_str, fmt).date()
            registros = self.repo_nomina.obtener_por_periodo(fecha_inicio, fecha_cierre)

            detalle = []
            for r in registros:
                empleado = self.repo_empleados.obtener_por_id(r.empleado_id)
                nombre = empleado.get_nombre_completo() if empleado else f"Empleado #{r.empleado_id}"
                cargo = empleado.cargo if empleado else ""
                detalle.append({
                    "empleado_id": r.empleado_id,
                    "nombre": nombre,
                    "cargo": cargo,
                    "dias_laborados": r.dias_laborados,
                    "salario_base_periodo": r.salario_base_periodo,
                    "auxilio_transporte": r.auxilio_transporte_periodo,
                    "total_devengado": r.total_devengado,
                    "descuento_afp": r.descuento_afp,
                    "descuento_eps": r.descuento_eps,
                    "total_deducciones": r.total_deducciones,
                    "salario_neto": r.salario_neto,
                })
            return detalle
        except Exception as e:
            print(f"Error al obtener detalle de nómina: {e}")
            return []
