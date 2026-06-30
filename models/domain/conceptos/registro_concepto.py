"""
Modelo de dominio RegistroConceptoNomina.
Solo datos y validaciones básicas. Sin lógica de negocio ni persistencia.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Optional


@dataclass
class RegistroConceptoNomina:
    """Registro del valor calculado de un concepto en una liquidación"""
    id: Optional[int] = None
    registro_nomina_id: int = 0
    concepto_nombre: str = ""
    tipo: str = ""
    naturaleza: str = "devengado"
    valor_calculado: float = 0.0
    metadata: Optional[str] = None
    
    def validar(self) -> tuple[bool, str]:
        """Validación básica de datos"""
        if self.registro_nomina_id <= 0:
            return False, "ID de registro de nómina inválido"
        if not self.concepto_nombre:
            return False, "Nombre de concepto es obligatorio"
        if self.naturaleza not in ["devengado", "deduccion"]:
            return False, "Naturaleza debe ser devengado o deduccion"
        return True, ""
    
    def to_dict(self) -> Dict[str, object]:
        return {
            "id": self.id,
            "registro_nomina_id": self.registro_nomina_id,
            "concepto_nombre": self.concepto_nombre,
            "tipo": self.tipo,
            "naturaleza": self.naturaleza,
            "valor_calculado": self.valor_calculado,
            "metadata": self.metadata,
        }
