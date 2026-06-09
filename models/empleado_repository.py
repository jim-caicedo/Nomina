"""
Repositorio de empleados con persistencia en SQLite.
Implementa el patrón Repository para abstraer la fuente de datos.
"""
from abc import ABC, abstractmethod
from typing import List, Optional
from database.db_manager import DBManager
from models.empleado import Empleado


class EmpleadoRepositoryBase(ABC):
    """Abstract base class para operaciones CRUD de empleados.
    Permite cambiar la fuente de datos (arreglo, BD, API) sin cambiar el controlador."""

    @abstractmethod
    def crear(self, empleado: Empleado) -> Empleado:
        pass

    @abstractmethod
    def obtener_por_id(self, empleado_id: int) -> Optional[Empleado]:
        pass

    @abstractmethod
    def obtener_todos(self) -> List[Empleado]:
        pass

    @abstractmethod
    def actualizar(self, empleado: Empleado) -> bool:
        pass

    @abstractmethod
    def eliminar(self, empleado_id: int) -> bool:
        pass

    @abstractmethod
    def existe(self, empleado_id: int) -> bool:
        pass


class EmpleadoRepositorySQLite(EmpleadoRepositoryBase):
    """Implementación del repositorio usando SQLite con persistencia real.
    Inicia completamente vacío - sin datos de prueba."""

    def __init__(self):
        """Inicializa el repositorio con la conexión a BD."""
        self.db = DBManager()
        # NO hay datos iniciales - el sistema arranca vacío

    def _row_to_empleado(self, row) -> Empleado:
        """Convierte una fila de SQLite en objeto Empleado."""
        # Obtener recibe_auxilio_transporte (default True si la columna no existe)
        recibe_aux = True
        if "recibe_auxilio_transporte" in row.keys():
            recibe_aux = bool(row["recibe_auxilio_transporte"])

        return Empleado(
            id=row["id"],
            nombre=row["nombre"],
            apellido=row["apellido"],
            cargo=row["cargo"],
            salario=float(row["salario"]),
            correo=row["correo"] or "",
            telefono=row["telefono"] or "",
            numero_cuenta=row["numero_cuenta"] or "",
            eps=row["eps"] or "EPS por asignar",
            afp=row["afp"] or "AFP por asignar",
            sede_laboral=row["sede_laboral"] or "",
            auxilio_transporte_mensual=float(row["auxilio_transporte_mensual"] or 161916.0),
            fecha_ingreso=row["fecha_ingreso"],
            horas_extra=float(row["horas_extra"] or 0.0),
            recibe_auxilio_transporte=recibe_aux,
        )

    def crear(self, empleado: Empleado) -> Empleado:
        """Crea un nuevo empleado en la BD."""
        try:
            cursor = self.db.get_connection().cursor()
            cursor.execute("""
                INSERT INTO empleados 
                (nombre, apellido, cargo, salario, correo, telefono, numero_cuenta, eps, afp, sede_laboral, auxilio_transporte_mensual, recibe_auxilio_transporte)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                empleado.nombre,
                empleado.apellido,
                empleado.cargo,
                empleado.salario,
                empleado.correo,
                empleado.telefono,
                empleado.numero_cuenta,
                empleado.eps,
                empleado.afp,
                empleado.sede_laboral,
                empleado.auxilio_transporte_mensual,
                1 if empleado.recibe_auxilio_transporte else 0,
            ))
            self.db.get_connection().commit()

            # Obtener el ID asignado
            empleado.id = cursor.lastrowid
            return empleado
        except Exception as e:
            print(f"Error al crear empleado: {e}")
            self.db.get_connection().rollback()
            raise

    def obtener_por_id(self, empleado_id: int) -> Optional[Empleado]:
        """Obtiene un empleado por su ID."""
        try:
            cursor = self.db.get_connection().cursor()
            cursor.execute("SELECT * FROM empleados WHERE id = ? AND activo = 1", (empleado_id,))
            row = cursor.fetchone()
            
            if row:
                return self._row_to_empleado(row)
            return None
        except Exception as e:
            print(f"Error al obtener empleado: {e}")
            return None

    def obtener_todos(self) -> List[Empleado]:
        """Retorna la lista de todos los empleados activos."""
        try:
            cursor = self.db.get_connection().cursor()
            cursor.execute("SELECT * FROM empleados WHERE activo = 1 ORDER BY id")
            rows = cursor.fetchall()
            
            return [self._row_to_empleado(row) for row in rows]
        except Exception as e:
            print(f"Error al obtener empleados: {e}")
            return []

    def actualizar(self, empleado: Empleado) -> bool:
        """Actualiza los datos de un empleado existente."""
        try:
            cursor = self.db.get_connection().cursor()
            cursor.execute("""
                UPDATE empleados
                SET nombre=?, apellido=?, cargo=?, salario=?, correo=?,
                    telefono=?, numero_cuenta=?, eps=?, afp=?, sede_laboral=?, auxilio_transporte_mensual=?, recibe_auxilio_transporte=?
                WHERE id=? AND activo = 1
            """, (
                empleado.nombre,
                empleado.apellido,
                empleado.cargo,
                empleado.salario,
                empleado.correo,
                empleado.telefono,
                empleado.numero_cuenta,
                empleado.eps,
                empleado.afp,
                empleado.sede_laboral,
                empleado.auxilio_transporte_mensual,
                1 if empleado.recibe_auxilio_transporte else 0,
                empleado.id,
            ))
            self.db.get_connection().commit()
            return cursor.rowcount > 0
        except Exception as e:
            print(f"Error al actualizar empleado: {e}")
            self.db.get_connection().rollback()
            return False

    def eliminar(self, empleado_id: int) -> bool:
        """Elimina un empleado (soft delete - marca como inactivo)."""
        try:
            cursor = self.db.get_connection().cursor()
            cursor.execute("UPDATE empleados SET activo = 0 WHERE id = ?", (empleado_id,))
            self.db.get_connection().commit()
            return cursor.rowcount > 0
        except Exception as e:
            print(f"Error al eliminar empleado: {e}")
            self.db.get_connection().rollback()
            return False

    def existe(self, empleado_id: int) -> bool:
        """Verifica si un empleado existe y está activo."""
        try:
            cursor = self.db.get_connection().cursor()
            cursor.execute("SELECT COUNT(*) FROM empleados WHERE id = ? AND activo = 1", (empleado_id,))
            count = cursor.fetchone()[0]
            return count > 0
        except Exception as e:
            print(f"Error al verificar existencia: {e}")
            return False