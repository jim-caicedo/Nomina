"""
Repositorio para `conceptos_nomina` (plantillas de concepto).
"""
from abc import ABC, abstractmethod
from typing import List, Optional
from database.db_manager import DBManager
from models.conceptos.concepto_models import ConceptoNomina


class ConceptoRepositoryBase(ABC):
    @abstractmethod
    def crear(self, concepto: ConceptoNomina) -> ConceptoNomina:
        pass

    @abstractmethod
    def obtener_por_id(self, concepto_id: int) -> Optional[ConceptoNomina]:
        pass

    @abstractmethod
    def obtener_todos(self) -> List[ConceptoNomina]:
        pass

    @abstractmethod
    def actualizar(self, concepto: ConceptoNomina) -> bool:
        pass

    @abstractmethod
    def eliminar(self, concepto_id: int) -> bool:
        pass


class ConceptoRepositorySQLite(ConceptoRepositoryBase):
    def __init__(self):
        self.db = DBManager()

    def _row_to_model(self, row) -> ConceptoNomina:
        # sqlite3.Row tiene .keys() pero no siempre .get(), por eso accedemos con seguridad
        try:
            keys = row.keys() if hasattr(row, 'keys') else []
        except Exception:
            keys = []

        def safe_get(column, default=None):
            try:
                if column in keys:
                    val = row[column]
                    return default if val is None else val
                # si no está en keys, intentar acceder (lanzará) y si falla, devolver default
                return row[column] if column in row else default
            except Exception:
                return default

        return ConceptoNomina(
            id=safe_get("id", None),
            nombre=safe_get("nombre", ""),
            tipo=safe_get("tipo", "fijo"),
            naturaleza=safe_get("naturaleza", "devengado"),
            valor=safe_get("valor", None),
            porcentaje=safe_get("porcentaje", None),
            base_calculo=safe_get("base_calculo", None),
            activo=bool(safe_get("activo", 1)),
            fecha_creacion=safe_get("fecha_creacion", None),
        )

    def crear(self, concepto: ConceptoNomina) -> ConceptoNomina:
        try:
            cursor = self.db.get_connection().cursor()
            cursor.execute(
                """
                INSERT INTO conceptos_nomina (nombre, tipo, naturaleza, valor, porcentaje, base_calculo, activo)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    concepto.nombre,
                    concepto.tipo,
                    concepto.naturaleza,
                    concepto.valor,
                    concepto.porcentaje,
                    concepto.base_calculo,
                    1 if concepto.activo else 0,
                ),
            )
            self.db.get_connection().commit()
            concepto.id = cursor.lastrowid
            return concepto
        except Exception as e:
            print(f"Error al crear concepto: {e}")
            self.db.get_connection().rollback()
            raise

    def obtener_por_id(self, concepto_id: int) -> Optional[ConceptoNomina]:
        try:
            cursor = self.db.get_connection().cursor()
            cursor.execute("SELECT * FROM conceptos_nomina WHERE id = ? AND activo = 1", (concepto_id,))
            row = cursor.fetchone()
            if row:
                return self._row_to_model(row)
            return None
        except Exception as e:
            print(f"Error al obtener concepto: {e}")
            return None

    def obtener_todos(self) -> List[ConceptoNomina]:
        try:
            cursor = self.db.get_connection().cursor()
            cursor.execute("SELECT * FROM conceptos_nomina WHERE activo = 1 ORDER BY id")
            rows = cursor.fetchall()
            return [self._row_to_model(r) for r in rows]
        except Exception as e:
            print(f"Error al listar conceptos: {e}")
            return []

    def actualizar(self, concepto: ConceptoNomina) -> bool:
        try:
            cursor = self.db.get_connection().cursor()
            cursor.execute(
                """
                UPDATE conceptos_nomina
                SET nombre=?, tipo=?, naturaleza=?, valor=?, porcentaje=?, base_calculo=?, activo=?
                WHERE id=?
                """,
                (
                    concepto.nombre,
                    concepto.tipo,
                    concepto.naturaleza,
                    concepto.valor,
                    concepto.porcentaje,
                    concepto.base_calculo,
                    1 if concepto.activo else 0,
                    concepto.id,
                ),
            )
            self.db.get_connection().commit()
            return cursor.rowcount > 0
        except Exception as e:
            print(f"Error al actualizar concepto: {e}")
            self.db.get_connection().rollback()
            return False

    def eliminar(self, concepto_id: int) -> bool:
        try:
            cursor = self.db.get_connection().cursor()
            cursor.execute("UPDATE conceptos_nomina SET activo = 0 WHERE id = ?", (concepto_id,))
            self.db.get_connection().commit()
            return cursor.rowcount > 0
        except Exception as e:
            print(f"Error al eliminar concepto: {e}")
            self.db.get_connection().rollback()
            return False
