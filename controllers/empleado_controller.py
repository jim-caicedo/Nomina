"""
Controlador de gestión de empleados.
Maneja todas las operaciones CRUD de empleados.
"""
from typing import List, Dict, Optional
from models.domain.empleado import Empleado
from models.repositories.sqlite.empleado_repository_sqlite import EmpleadoRepositorySQLite
from database.db_manager import DBManager


class EmpleadoController:
    """Controlador para gestión de empleados (CRUD)."""
    
    def __init__(self):
        """Inicializa el controlador con repositorio SQLite."""
        self.repo_empleados = EmpleadoRepositorySQLite(DBManager())

    def obtener_empleados(self) -> List[Dict[str, object]]:
        """Obtiene lista de empleados como diccionarios."""
        return [empleado.to_dict() for empleado in self.repo_empleados.obtener_todos()]

    def buscar_empleado(self, empleado_id: int) -> Optional[Empleado]:
        """Busca un empleado por ID."""
        return self.repo_empleados.obtener_por_id(empleado_id)

    def crear_empleado(
        self, 
        nombre: str, 
        apellido: str, 
        cargo: str, 
        salario: float, 
        correo: str = "", 
        telefono: str = "", 
        numero_cuenta: str = "",
        eps: str = "EPS por asignar",
        afp: str = "AFP por asignar",
        sede_laboral: str = "",
        recibe_auxilio_transporte: bool = True,
    ) -> Dict[str, object]:
        """Crea un nuevo empleado."""
        if not nombre or not apellido or not cargo or salario <= 0:
            return {"success": False, "error": "Datos inválidos. Verifica nombre, apellido, cargo y salario."}
        
        nuevo_empleado = Empleado(
            id=0, 
            nombre=nombre, 
            apellido=apellido, 
            cargo=cargo, 
            salario=salario,
            correo=correo,
            telefono=telefono,
            numero_cuenta=numero_cuenta,
            eps=eps,
            afp=afp,
            sede_laboral=sede_laboral,
            recibe_auxilio_transporte=recibe_auxilio_transporte,
        )
        
        try:
            empleado_creado = self.repo_empleados.crear(nuevo_empleado)
            return {"success": True, "empleado": empleado_creado.to_dict()}
        except Exception as e:
            return {"success": False, "error": f"Error al crear empleado: {str(e)}"}

    def actualizar_empleado(
        self, 
        empleado_id: int, 
        nombre: str, 
        apellido: str, 
        cargo: str, 
        salario: float, 
        correo: str = "", 
        telefono: str = "", 
        numero_cuenta: str = "",
        eps: str = "EPS por asignar",
        afp: str = "AFP por asignar",
        sede_laboral: str = "",
        recibe_auxilio_transporte: bool = True,
    ) -> Dict[str, object]:
        """Actualiza un empleado existente."""
        if not self.repo_empleados.existe(empleado_id):
            return {"success": False, "error": "Empleado no encontrado."}
        
        if not nombre or not apellido or not cargo or salario <= 0:
            return {"success": False, "error": "Datos inválidos. Verifica nombre, apellido, cargo y salario."}
        
        empleado = Empleado(
            id=empleado_id, 
            nombre=nombre, 
            apellido=apellido, 
            cargo=cargo, 
            salario=salario,
            correo=correo,
            telefono=telefono,
            numero_cuenta=numero_cuenta,
            eps=eps,
            afp=afp,
            sede_laboral=sede_laboral,
            recibe_auxilio_transporte=recibe_auxilio_transporte,
        )
        
        try:
            self.repo_empleados.actualizar(empleado)
            return {"success": True, "mensaje": f"Empleado {nombre} {apellido} actualizado exitosamente."}
        except Exception as e:
            return {"success": False, "error": f"Error al actualizar empleado: {str(e)}"}

    def eliminar_empleado(self, empleado_id: int) -> Dict[str, object]:
        """Elimina un empleado (soft delete)."""
        if not self.repo_empleados.existe(empleado_id):
            return {"success": False, "error": "Empleado no encontrado."}
        
        try:
            self.repo_empleados.eliminar(empleado_id)
            return {"success": True, "mensaje": "Empleado eliminado exitosamente."}
        except Exception as e:
            return {"success": False, "error": f"Error al eliminar empleado: {str(e)}"}

    def listar_empleados(self) -> List[Dict[str, object]]:
        """Retorna lista de empleados."""
        return self.obtener_empleados()
