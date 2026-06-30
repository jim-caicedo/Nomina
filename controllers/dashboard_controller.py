"""
Controlador de dashboard.
Maneja la generación de resúmenes estadísticos.
"""
from typing import Dict
from models.repositories.sqlite.empleado_repository_sqlite import EmpleadoRepositorySQLite


class DashboardController:
    """Controlador para generación de resúmenes del dashboard."""
    
    def __init__(self):
        """Inicializa el controlador con repositorio de empleados."""
        self.repo_empleados = EmpleadoRepositorySQLite()

    def generar_resumen_dashboard(self) -> Dict[str, object]:
        """Genera resumen para el dashboard con datos reales de SQLite."""
        empleados = self.repo_empleados.obtener_todos()
        
        if not empleados:
            return {
                "empleados_activos": 0,
                "gasto_total_mensual": 0.0,
                "salario_promedio": 0.0,
            }
        
        total_nomina = sum(e.salario for e in empleados)
        promedio_salario = round(total_nomina / len(empleados), 2)
        
        return {
            "empleados_activos": len(empleados),
            "gasto_total_mensual": round(total_nomina, 2),
            "salario_promedio": promedio_salario,
        }
