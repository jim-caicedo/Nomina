"""
Interfaz para conceptos de nómina calculables.
"""
from abc import ABC, abstractmethod
from datetime import date
from typing import Protocol, runtime_checkable


@runtime_checkable
class IConceptoCalculable(Protocol):
    """Interfaz que define un concepto capaz de calcular su valor en un período."""

    @abstractmethod
    def calcular(self, empleado, periodo_inicio: date, periodo_cierre: date, valor_ingresado: float = 0.0) -> float:
        """Calcula el valor del concepto para el empleado en el período."""
        ...
