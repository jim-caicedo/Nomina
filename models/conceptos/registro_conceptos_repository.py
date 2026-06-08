"""
Repositorio para `registro_conceptos_nomina` (valores calculados por nómina).
"""
from abc import ABC, abstractmethod
from typing import List
from database.db_manager import DBManager
from models.conceptos.concepto_models import RegistroConceptoNomina
import json


class RegistroConceptoRepositoryBase(ABC):
    @abstractmethod
    def crear(self, registro: RegistroConceptoNomina) -> RegistroConceptoNomina:
        pass

    @abstractmethod
    def obtener_por_registro_nomina(self, registro_nomina_id: int) -> List[RegistroConceptoNomina]:
        pass


class RegistroConceptoRepositorySQLite(RegistroConceptoRepositoryBase):
    def __init__(self):
        self.db = DBManager()

    def _row_to_model(self, row) -> RegistroConceptoNomina:
        metadata = None
        try:
            if row["metadata"]:
                metadata = json.loads(row["metadata"])
        except Exception:
            metadata = None
        try:
            keys = row.keys() if hasattr(row, 'keys') else []
        except Exception:
            keys = []

        def safe_get(column, default=None):
            try:
                if column in keys:
                    val = row[column]
                    return default if val is None else val
                return row[column] if column in row else default
            except Exception:
                return default

        return RegistroConceptoNomina(
            id=safe_get("id", None),
            registro_nomina_id=safe_get("registro_nomina_id", None),
            concepto_nombre=safe_get("concepto_nombre", ""),
            tipo=safe_get("tipo", ""),
            naturaleza=safe_get("naturaleza", "devengado"),
            valor_calculado=float(safe_get("valor_calculado", 0.0)),
            metadata=metadata,
            fecha_creacion=safe_get("fecha_creacion", None),
        )

    def crear(self, registro: RegistroConceptoNomina) -> RegistroConceptoNomina:
        try:
            cursor = self.db.get_connection().cursor()
            metadata_json = json.dumps(registro.metadata) if registro.metadata else None
            cursor.execute(
                """
                INSERT INTO registro_conceptos_nomina (registro_nomina_id, concepto_id, concepto_empleado_id, concepto_nombre, tipo, naturaleza, valor_calculado, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    registro.registro_nomina_id,
                    None,
                    None,
                    registro.concepto_nombre,
                    registro.tipo,
                    registro.naturaleza,
                    registro.valor_calculado,
                    metadata_json,
                ),
            )
            self.db.get_connection().commit()
            registro.id = cursor.lastrowid
            return registro
        except Exception as e:
            print(f"Error al crear registro de concepto: {e}")
            self.db.get_connection().rollback()
            raise

    def obtener_por_registro_nomina(self, registro_nomina_id: int) -> List[RegistroConceptoNomina]:
        try:
            cursor = self.db.get_connection().cursor()
            cursor.execute("SELECT * FROM registro_conceptos_nomina WHERE registro_nomina_id = ? ORDER BY id", (registro_nomina_id,))
            rows = cursor.fetchall()
            return [self._row_to_model(r) for r in rows]
        except Exception as e:
            print(f"Error al obtener registros por nómina: {e}")
            return []
