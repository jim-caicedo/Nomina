"""
Interfaz abstracta para operaciones de registros de nómina.
"""
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import List, Optional
from models.domain.nomina import RegistroNomina


class NominaRepository(ABC):
    """Interfaz abstracta para operaciones de nómina"""
    
    @abstractmethod
    def guardar_registro(self, registro: RegistroNomina) -> RegistroNomina:
        """Guarda un registro de nómina"""
        pass
    
    @abstractmethod
    def obtener_por_id(self, registro_id: int) -> Optional[RegistroNomina]:
        """Obtiene un registro por ID"""
        pass
    
    @abstractmethod
    def obtener_todos(self) -> List[RegistroNomina]:
        """Obtiene todos los registros de nómina"""
        pass
    
    @abstractmethod
    def obtener_por_periodo(self, fecha_inicio, fecha_cierre) -> List[RegistroNomina]:
        """Obtiene registros por período"""
        pass
    
    @abstractmethod
    def obtener_por_empleado(self, empleado_id: int) -> List[RegistroNomina]:
        """Obtiene registros de un empleado"""
        pass
