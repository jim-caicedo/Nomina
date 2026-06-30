"""
Modelo de dominio ConceptoEmpleado.
Solo datos y validaciones básicas. Sin lógica de negocio ni persistencia.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Optional


@dataclass
class ConceptoEmpleado:
    """Asignación de concepto a un empleado específico"""
    id: Optional[int] = None
    empleado_id: int = 0
    concepto_id: Optional[int] = None  # ID de la plantilla (si aplica)
    nombre: str = ""
    tipo: str = "fijo"
    naturaleza: str = "devengado"
    valor_personalizado: Optional[float] = None
    porcentaje_personalizado: Optional[float] = None
    base_calculo: Optional[str] = None
    activo: bool = True
    
    def validar(self) -> tuple[bool, str]:
        """Validación básica de datos"""
        if self.empleado_id <= 0:
            return False, "ID de empleado inválido"
        if not self.nombre:
            return False, "Nombre es obligatorio"
        if self.tipo not in ["fijo", "variable", "porcentaje"]:
            return False, "Tipo debe ser fijo, variable o porcentaje"
        if self.naturaleza not in ["devengado", "deduccion"]:
            return False, "Naturaleza debe ser devengado o deduccion"
        return True, ""
    
    def to_dict(self) -> Dict[str, object]:
        return {
            "id": self.id,
            "empleado_id": self.empleado_id,
            "concepto_id": self.concepto_id,
            "nombre": self.nombre,
            "tipo": self.tipo,
            "naturaleza": self.naturaleza,
            "valor_personalizado": self.valor_personalizado,
            "porcentaje_personalizado": self.porcentaje_personalizado,
            "base_calculo": self.base_calculo,
            "activo": self.activo,
        }
