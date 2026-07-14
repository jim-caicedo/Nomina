"""
Modelos de dominio para conceptos de nómina.
ConceptoNomina: plantilla del catálogo.
ConceptoEmpleado: asignación personalizada a un empleado.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Optional


@dataclass
class ConceptoNomina:
    """Plantilla de concepto de nómina (catálogo global)"""
    id: Optional[int] = None
    nombre: str = ""
    tipo: str = "fijo"          # fijo | variable | porcentaje
    valor: Optional[float] = None
    porcentaje: Optional[float] = None
    base_calculo: Optional[str] = "salario"
    naturaleza: str = "devengado"   # devengado | deduccion
    activo: bool = True

    def validar(self) -> tuple[bool, str]:
        if not self.nombre:
            return False, "Nombre es obligatorio"
        if self.tipo not in ("fijo", "variable", "porcentaje"):
            return False, "Tipo debe ser fijo, variable o porcentaje"
        if self.tipo == "fijo" and self.valor is None:
            return False, "Concepto fijo requiere valor"
        if self.tipo == "porcentaje" and self.porcentaje is None:
            return False, "Concepto porcentaje requiere porcentaje"
        if self.naturaleza not in ("devengado", "deduccion"):
            return False, "Naturaleza debe ser devengado o deduccion"
        return True, ""

    def to_dict(self) -> Dict[str, object]:
        return {
            "id": self.id,
            "nombre": self.nombre,
            "tipo": self.tipo,
            "valor": self.valor,
            "porcentaje": self.porcentaje,
            "base_calculo": self.base_calculo,
            "naturaleza": self.naturaleza,
            "activo": self.activo,
        }


@dataclass
class ConceptoEmpleado:
    """Asignación personalizada de un concepto a un empleado específico.
    Mapea la tabla `conceptos_empleado` en SQLite.
    Permite sobrescribir valor/porcentaje/base del catálogo para un empleado.
    """
    id: Optional[int] = None
    empleado_id: int = 0
    concepto_id: Optional[int] = None
    nombre: str = ""
    tipo: str = "fijo"                       # fijo | variable | porcentaje
    naturaleza: str = "devengado"            # devengado | deduccion
    valor_personalizado: Optional[float] = None
    porcentaje_personalizado: Optional[float] = None
    base_calculo: Optional[str] = "salario"
    activo: bool = True
    fecha_asignacion: Optional[str] = None   # TIMESTAMP como string ISO

    def validar(self) -> tuple[bool, str]:
        if not self.nombre:
            return False, "Nombre es obligatorio"
        if self.empleado_id is None or self.empleado_id <= 0:
            return False, "Empleado es obligatorio"
        if self.tipo not in ("fijo", "variable", "porcentaje"):
            return False, "Tipo debe ser fijo, variable o porcentaje"
        if self.naturaleza not in ("devengado", "deduccion"):
            return False, "Naturaleza debe ser devengado o deduccion"
        if self.tipo == "fijo" and self.valor_personalizado is None:
            return False, "Concepto fijo requiere valor personalizado"
        if self.tipo == "porcentaje" and self.porcentaje_personalizado is None:
            return False, "Concepto porcentaje requiere porcentaje personalizado"
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
            "fecha_asignacion": self.fecha_asignacion,
        }

@dataclass
class RegistroConceptoNomina:
    """Desglose de un concepto aplicado en una liquidación específica."""
    id: Optional[int] = None
    registro_nomina_id: int = 0
    concepto_id: Optional[int] = None
    concepto_empleado_id: Optional[int] = None
    concepto_nombre: str = ""
    tipo: str = ""
    naturaleza: str = "devengado"
    valor_calculado: float = 0.0
    metadata: Optional[str] = None
    fecha_creacion: Optional[str] = None