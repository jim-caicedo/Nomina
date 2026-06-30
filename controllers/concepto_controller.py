"""
Controlador de gestión de conceptos de nómina.
Maneja el catálogo de conceptos y asignaciones a empleados.
"""
from typing import List, Dict, Optional
from dataclasses import asdict
from models.domain.conceptos.concepto_nomina import ConceptoNomina
from models.domain.conceptos.concepto_empleado import ConceptoEmpleado
from models.repositories.sqlite.empleado_repository_sqlite import EmpleadoRepositorySQLite
from models.repositories.sqlite.concepto_repository_sqlite import ConceptoRepositorySQLite, ConceptoEmpleadoRepositorySQLite
from database.db_manager import DBManager


class ConceptoController:
    """Controlador para gestión de conceptos de nómina."""
    
    def __init__(self):
        """Inicializa el controlador con repositorios."""
        db = DBManager()
        self.repo_empleados = EmpleadoRepositorySQLite(db)
        self._repo_conceptos = ConceptoRepositorySQLite(db)
        self._repo_conceptos_emp = ConceptoEmpleadoRepositorySQLite(db)

    def obtener_conceptos_disponibles(self) -> List[Dict[str, object]]:
        """Retorna catálogo de conceptos activos."""
        conceptos = self._repo_conceptos.obtener_todos()
        return [asdict(c) for c in conceptos]

    def crear_concepto(
        self,
        nombre: str,
        tipo: str,
        naturaleza: str = "devengado",
        valor: Optional[float] = None,
        porcentaje: Optional[float] = None,
        base_calculo: Optional[str] = "salario",
    ) -> Dict[str, object]:
        """Crea una plantilla de concepto en el catálogo."""
        if not nombre or not tipo:
            return {"success": False, "error": "Nombre y tipo son requeridos."}

        concepto = ConceptoNomina(
            id=None,
            nombre=nombre,
            tipo=tipo,
            valor=valor,
            porcentaje=porcentaje,
            base_calculo=base_calculo,
            naturaleza=naturaleza,
            activo=True,
        )
        try:
            creado = self._repo_conceptos.crear(concepto)
            return {"success": True, "concepto": asdict(creado)}
        except Exception as e:
            return {"success": False, "error": f"Error al crear concepto: {e}"}

    def asignar_concepto_a_empleado(
        self,
        empleado_id: int,
        concepto_id: Optional[int] = None,
        nombre: Optional[str] = None,
        tipo: str = "fijo",
        naturaleza: str = "devengado",
        valor_personalizado: Optional[float] = None,
        porcentaje_personalizado: Optional[float] = None,
        base_calculo: Optional[str] = None,
    ) -> Dict[str, object]:
        """Asigna un concepto (plantilla o nuevo nombre) a un empleado."""
        if not self.repo_empleados.existe(empleado_id):
            return {"success": False, "error": "Empleado no encontrado."}

        plantilla = None
        if concepto_id:
            plantilla = self._repo_conceptos.obtener_por_id(concepto_id)
            if plantilla is None:
                return {"success": False, "error": "Concepto plantilla no encontrado."}

        # Si no se pasó nombre y hay plantilla, tomar nombre de plantilla
        nombre_final = nombre or (plantilla.nombre if plantilla else "")
        tipo_final = plantilla.tipo if plantilla and plantilla.tipo else tipo
        naturaleza_final = plantilla.naturaleza if plantilla and getattr(plantilla, 'naturaleza', None) else naturaleza
        valor_personalizado_final = valor_personalizado if valor_personalizado is not None else (plantilla.valor if plantilla else None)
        porcentaje_personalizado_final = porcentaje_personalizado if porcentaje_personalizado is not None else (plantilla.porcentaje if plantilla else None)
        base_calculo_final = base_calculo or (plantilla.base_calculo if plantilla else None)

        asign = ConceptoEmpleado(
            id=None,
            empleado_id=empleado_id,
            concepto_id=concepto_id,
            nombre=nombre_final,
            tipo=tipo_final,
            naturaleza=naturaleza_final,
            valor_personalizado=valor_personalizado_final,
            porcentaje_personalizado=porcentaje_personalizado_final,
            base_calculo=base_calculo_final,
            activo=True,
        )
        try:
            creado = self._repo_conceptos_emp.asignar(asign)
            return {"success": True, "asignacion": asdict(creado)}
        except Exception as e:
            return {"success": False, "error": f"Error al asignar concepto: {e}"}

    def obtener_conceptos_de_empleado(self, empleado_id: int) -> List[Dict[str, object]]:
        """Lista las asignaciones de conceptos de un empleado."""
        if not self.repo_empleados.existe(empleado_id):
            return []
        asignaciones = self._repo_conceptos_emp.obtener_por_empleado(empleado_id)
        return [asdict(a) for a in asignaciones]

    # Exponer repositorios para operaciones directas desde vistas
    @property
    def repo_conceptos(self):
        """Expone el repositorio de conceptos para operaciones directas."""
        return self._repo_conceptos

    @property
    def repo_conceptos_emp(self):
        """Expone el repositorio de conceptos de empleado para operaciones directas."""
        return self._repo_conceptos_emp
