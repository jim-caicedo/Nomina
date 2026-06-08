from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, Any


@dataclass
class ConceptoNomina:
    id: Optional[int] = None
    nombre: str = ""
    tipo: str = "fijo"  # 'fijo' | 'variable' | 'porcentaje'
    valor: Optional[float] = None
    porcentaje: Optional[float] = None
    base_calculo: Optional[str] = "salario"  # 'salario' | 'ventas' | custom
    naturaleza: str = "devengado"  # 'devengado' | 'deduccion'
    activo: bool = True
    fecha_creacion: datetime = field(default_factory=datetime.utcnow)


@dataclass
class ConceptoEmpleado:
    """Representa una asignación de concepto para un empleado.

    Cuando concepto_id es None, los campos nombre/tipo/naturaleza son la fuente de
    verdad. Cuando concepto_id tiene valor, la fuente de verdad de nombre/tipo/naturaleza
    es ConceptoNomina. Los campos locales en ese caso son ignorados por el calculador.
    """
    id: Optional[int] = None
    empleado_id: Optional[int] = None
    concepto_id: Optional[int] = None
    nombre: Optional[str] = None  # Usado solo cuando no hay plantilla (concepto_id is None)
    tipo: Optional[str] = None  # Usado solo cuando no hay plantilla
    naturaleza: Optional[str] = None  # Usado solo cuando no hay plantilla
    valor_personalizado: Optional[float] = None
    porcentaje_personalizado: Optional[float] = None
    base_calculo: Optional[str] = None
    activo: bool = True
    fecha_asignacion: datetime = field(default_factory=datetime.utcnow)


@dataclass
class RegistroConceptoNomina:
    id: Optional[int] = None
    registro_nomina_id: Optional[int] = None
    concepto_nombre: str = ""
    tipo: str = ""
    naturaleza: str = "devengado"
    valor_calculado: float = 0.0
    metadata: Optional[Dict[str, Any]] = None
    fecha_creacion: datetime = field(default_factory=datetime.utcnow)
