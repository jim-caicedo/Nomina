"""
Modelo de Configuración Legal de Nómina.
Almacena los parámetros legales vigentes para cálculos de nómina.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Optional


@dataclass
class ConfiguracionNomina:
    """
    Configuración de parámetros legales para cálculo de nómina.
    Estos valores se actualizan anualmente según ley colombiana.
    
    Campos SQLite:
    - id: Autogenerado por BD (Primary Key)
    - fecha_creacion: Timestamp automático de cuándo se creó
    - activa: Boolean (1=activa, 0=inactiva)
    """

    anio_vigente: int = 2026
    salario_minimo_mensual: float = 1315000.0
    auxilio_transporte_mensual: float = 161916.0
    porcentaje_afp: float = 0.04  # 4%
    porcentaje_eps: float = 0.04  # 4%
    id: Optional[int] = None                      # Auto-generado por SQLite
    fecha_creacion: Optional[str] = None          # Auto-generado por SQLite
    activa: bool = True                           # 1=activa, 0=inactiva

    def to_dict(self) -> Dict[str, object]:
        """Convierte la configuración a diccionario."""
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

    @classmethod
    def from_dict(cls, data: Dict[str, object]) -> "ConfiguracionNomina":
        """
        Crea una instancia de ConfiguracionNomina desde un diccionario.

        Args:
            data: Diccionario con los campos de configuración

        Returns:
            Instancia de ConfiguracionNomina
        """
        return cls(
            anio_vigente=int(data.get("anio_vigente", 2026)),
            salario_minimo_mensual=float(data.get("salario_minimo_mensual", 1315000)),
            auxilio_transporte_mensual=float(data.get("auxilio_transporte_mensual", 161916)),
            porcentaje_afp=float(data.get("porcentaje_afp", 0.04)),
            porcentaje_eps=float(data.get("porcentaje_eps", 0.04)),
            id=data.get("id"),
            fecha_creacion=data.get("fecha_creacion"),
            activa=bool(data.get("activa", True)),
        )

    @classmethod
    def crear_default_2026(cls) -> "ConfiguracionNomina":
        """
        Crea configuración con valores por defecto para 2026.

        Returns:
            ConfiguracionNomina con valores 2026
        """
        return cls(
            anio_vigente=2026,
            salario_minimo_mensual=1315000.0,
            auxilio_transporte_mensual=161916.0,
            porcentaje_afp=0.04,
            porcentaje_eps=0.04,
            id=None,
            fecha_creacion=None,
            activa=True,
        )

    def validar(self) -> tuple[bool, str]:
        """
        Valida que los valores de configuración sean correctos.

        Returns:
            Tupla (es_valido, mensaje_error)
        """
        # Validar año
        if not (2020 <= self.anio_vigente <= 2050):
            return False, f"Año vigente debe estar entre 2020 y 2050. Valor: {self.anio_vigente}"

        # Validar salario mínimo
        if self.salario_minimo_mensual <= 0:
            return False, f"Salario mínimo debe ser positivo. Valor: {self.salario_minimo_mensual}"

        # Validar auxilio transporte
        if self.auxilio_transporte_mensual < 0:
            return False, f"Auxilio transporte no puede ser negativo. Valor: {self.auxilio_transporte_mensual}"

        # Validar porcentajes (entre 0 y 1, o entre 0 y 100)
        if not (0 <= self.porcentaje_afp <= 1):
            return False, f"Porcentaje AFP debe estar entre 0 y 1 (ej: 0.04 para 4%). Valor: {self.porcentaje_afp}"

        if not (0 <= self.porcentaje_eps <= 1):
            return False, f"Porcentaje EPS debe estar entre 0 y 1 (ej: 0.04 para 4%). Valor: {self.porcentaje_eps}"

        return True, ""
