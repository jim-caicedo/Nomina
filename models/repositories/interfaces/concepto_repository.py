"""
Interfaz abstracta para operaciones de conceptos de nómina.
"""
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import List, Optional
from models.domain.conceptos.concepto_nomina import ConceptoNomina
from models.domain.conceptos.concepto_empleado import ConceptoEmpleado
from models.domain.conceptos.registro_concepto import RegistroConceptoNomina


class ConceptoRepository(ABC):
    """Interfaz abstracta para operaciones de conceptos (catálogo)"""
    
    @abstractmethod
    def crear(self, concepto: ConceptoNomina) -> ConceptoNomina:
        """Crea un concepto en el catálogo"""
        pass
    
    @abstractmethod
    def obtener_por_id(self, concepto_id: int) -> Optional[ConceptoNomina]:
        """Obtiene un concepto por ID"""
        pass
    
    @abstractmethod
    def obtener_todos(self) -> List[ConceptoNomina]:
        """Obtiene todos los conceptos activos"""
        pass
    
    @abstractmethod
    def actualizar(self, concepto: ConceptoNomina) -> bool:
        """Actualiza un concepto"""
        pass
    
    @abstractmethod
    def eliminar(self, concepto_id: int) -> bool:
        """Elimina un concepto (soft delete)"""
        pass


class ConceptoEmpleadoRepository(ABC):
    """Interfaz abstracta para asignaciones de conceptos a empleados"""
    
    @abstractmethod
    def asignar(self, asignacion: ConceptoEmpleado) -> ConceptoEmpleado:
        """Asigna un concepto a un empleado"""
        pass
    
    @abstractmethod
    def obtener_por_empleado(self, empleado_id: int) -> List[ConceptoEmpleado]:
        """Obtiene asignaciones de un empleado"""
        pass
    
    @abstractmethod
    def obtener_por_id(self, asignacion_id: int) -> Optional[ConceptoEmpleado]:
        """Obtiene una asignación por ID"""
        pass
    
    @abstractmethod
    def desasignar(self, asignacion_id: int) -> bool:
        """Elimina una asignación"""
        pass


class RegistroConceptoRepository(ABC):
    """Interfaz abstracta para registros de conceptos calculados"""
    
    @abstractmethod
    def crear(self, registro: RegistroConceptoNomina) -> RegistroConceptoNomina:
        """Crea un registro de concepto calculado"""
        pass
    
    @abstractmethod
    def obtener_por_nomina(self, registro_nomina_id: int) -> List[RegistroConceptoNomina]:
        """Obtiene registros de conceptos de una nómina"""
        pass
