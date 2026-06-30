"""
Modelo de dominio ConfiguracionNomina.
Solo datos y validaciones básicas. Sin lógica de negocio ni persistencia.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Optional


@dataclass
class ConfiguracionNomina:
    """Configuración de parámetros legales para cálculo de nómina"""
    id: Optional[int] = None
    anio_vigente: int = 2026
    salario_minimo_mensual: float = 1315000.0
    auxilio_transporte_mensual: float = 161916.0
    porcentaje_afp: float = 0.04
    porcentaje_eps: float = 0.04
    fecha_creacion: Optional[str] = None
    activa: bool = True
    
    def validar(self) -> tuple[bool, str]:
        """Validación de parámetros legales"""
        if not (2020 <= self.anio_vigente <= 2050):
            return False, f"Año vigente debe estar entre 2020 y 2050"
        if self.salario_minimo_mensual <= 0:
            return False, "Salario mínimo debe ser positivo"
        if not (0 <= self.porcentaje_afp <= 1):
            return False, "Porcentaje AFP debe estar entre 0 y 1"
        if not (0 <= self.porcentaje_eps <= 1):
            return False, "Porcentaje EPS debe estar entre 0 y 1"
        return True, ""
    
    @classmethod
    def crear_default_2026(cls) -> "ConfiguracionNomina":
        return cls(
            anio_vigente=2026,
            salario_minimo_mensual=1315000.0,
            auxilio_transporte_mensual=161916.0,
            porcentaje_afp=0.04,
            porcentaje_eps=0.04,
        )
    
    def to_dict(self) -> Dict[str, object]:
        return {
            "id": self.id,
            "anio_vigente": self.anio_vigente,
            "salario_minimo_mensual": self.salario_minimo_mensual,
            "auxilio_transporte_mensual": self.auxilio_transporte_mensual,
            "porcentaje_afp": self.porcentaje_afp,
            "porcentaje_eps": self.porcentaje_eps,
            "fecha_creacion": self.fecha_creacion,
            "activa": self.activa,
        }
