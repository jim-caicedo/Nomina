"""
Interfaz abstracta para operaciones CRUD de empleados.
"""
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import List, Optional
from models.domain.empleado import Empleado


class EmpleadoRepository(ABC):
    """Interfaz abstracta para operaciones CRUD de empleados"""
    
    @abstractmethod
    def crear(self, empleado: Empleado) -> Empleado:
        """Crea un nuevo empleado"""
        pass
    
    @abstractmethod
    def obtener_por_id(self, empleado_id: int) -> Optional[Empleado]:
        """Obtiene un empleado por ID"""
        pass
    
    @abstractmethod
    def obtener_todos(self) -> List[Empleado]:
        """Obtiene todos los empleados activos"""
        pass
    
    @abstractmethod
    def actualizar(self, empleado: Empleado) -> bool:
        """Actualiza un empleado existente"""
        pass
    
    @abstractmethod
    def eliminar(self, empleado_id: int) -> bool:
        """Elimina un empleado (soft delete)"""
        pass
    
    @abstractmethod
    def existe(self, empleado_id: int) -> bool:
        """Verifica si existe un empleado"""
        pass
