"""
Controlador principal de la aplicación.
Coordinador que instancia los controladores especializados.
"""
from controllers.empleado_controller import EmpleadoController
from controllers.nomina_controller import NominaController
from controllers.concepto_controller import ConceptoController
from controllers.dashboard_controller import DashboardController
from controllers.historial_controller import HistorialController
from controllers.configuracion_controller import ConfiguracionController


class MainController:
    """Controlador principal que coordina los controladores especializados."""
    
    def __init__(self):
        """Inicializa los controladores especializados."""
        self.empleado_controller = EmpleadoController()
        self.nomina_controller = NominaController()
        self.concepto_controller = ConceptoController()
        self.dashboard_controller = DashboardController()
        self.historial_controller = HistorialController()
        self.config_controller = ConfiguracionController()