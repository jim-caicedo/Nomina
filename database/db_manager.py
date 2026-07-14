"""
Gestor de base de datos SQLite para NominaSG.
Singleton que maneja la conexión y inicialización de tablas.
"""
import sqlite3
from pathlib import Path
from typing import Optional


class DBManager:
    """Singleton para gestionar la conexión a SQLite."""
    _instance: Optional["DBManager"] = None
    _connection: Optional[sqlite3.Connection] = None

    def __new__(cls) -> "DBManager":
        """Implementa patrón singleton."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """Inicializa la conexión a la BD si no existe."""
        if self._connection is None:
            self._initialize_database()

    def _initialize_database(self) -> None:
        """Crea la carpeta data/ y la base de datos con tablas."""
        # Crear carpeta data/ si no existe
        db_dir = Path(__file__).parent.parent / "data"
        db_dir.mkdir(parents=True, exist_ok=True)

        # Ruta de la BD
        db_path = db_dir / "nomina.db"

        # Conectar
        self._connection = sqlite3.connect(
            str(db_path), check_same_thread=False, isolation_level=None
        )
        self._connection.row_factory = sqlite3.Row

        # Crear tablas si no existen
        self._create_tables()

        # Seed de configuración legal si la BD está vacía
        try:
            from database.seed_data import seed_configuracion_si_vacia
            seed_configuracion_si_vacia(self)
        except Exception as e:
            print(f"Error al sembrar configuración legal: {e}")

    def _create_tables(self) -> None:
        """Crea todas las tablas necesarias."""
        cursor = self._connection.cursor()

        # Tabla de configuración legal
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS configuracion_legal (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                anio_vigente INTEGER NOT NULL,
                salario_minimo_mensual REAL NOT NULL,
                auxilio_transporte_mensual REAL NOT NULL,
                porcentaje_afp REAL NOT NULL,
                porcentaje_eps REAL NOT NULL,
                fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                activa INTEGER DEFAULT 1
            )
        """)

        # Tabla de historial de cambios
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS historial_cambios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                campo_cambiado TEXT NOT NULL,
                valor_anterior TEXT,
                valor_nuevo TEXT NOT NULL,
                fecha_cambio TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                usuario TEXT DEFAULT 'admin'
            )
        """)

        # Tabla de empleados
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS empleados (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                apellido TEXT NOT NULL,
                cargo TEXT NOT NULL,
                salario REAL NOT NULL,
                correo TEXT DEFAULT '',
                telefono TEXT DEFAULT '',
                numero_cuenta TEXT DEFAULT '',
                eps TEXT DEFAULT 'EPS por asignar',
                afp TEXT DEFAULT 'AFP por asignar',
                sede_laboral TEXT DEFAULT '',
                fecha_ingreso TIMESTAMP,
                horas_extra REAL DEFAULT 0.0,
                recibe_auxilio_transporte INTEGER DEFAULT 1,
                activo INTEGER DEFAULT 1,
                fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Tabla de registros de nómina
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS registros_nomina (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                empleado_id INTEGER NOT NULL,
                periodo_inicio TEXT NOT NULL,
                periodo_cierre TEXT NOT NULL,
                dias_laborados INTEGER NOT NULL,
                salario_base_periodo REAL NOT NULL,
                auxilio_transporte_periodo REAL NOT NULL,
                horas_extras INTEGER NOT NULL,
                valor_horas_extras REAL NOT NULL,
                total_devengado REAL NOT NULL,
                descuento_afp REAL NOT NULL,
                descuento_eps REAL NOT NULL,
                otros_descuentos REAL DEFAULT 0.0,
                total_deducciones REAL NOT NULL,
                salario_neto REAL NOT NULL,
                fecha_liquidacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (empleado_id) REFERENCES empleados(id)
            )
        """)

        # Tabla de conceptos generales (plantillas de concepto)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS conceptos_nomina (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                tipo TEXT NOT NULL,
                naturaleza TEXT DEFAULT 'devengado',
                valor REAL,
                porcentaje REAL,
                base_calculo TEXT,
                activo INTEGER DEFAULT 1,
                fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Tabla de conceptos asignados a empleados (posible personalización)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS conceptos_empleado (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                empleado_id INTEGER NOT NULL,
                concepto_id INTEGER,
                nombre TEXT NOT NULL,
                tipo TEXT NOT NULL,
                naturaleza TEXT DEFAULT 'devengado',
                valor_personalizado REAL,
                porcentaje_personalizado REAL,
                base_calculo TEXT,
                activo INTEGER DEFAULT 1,
                fecha_asignacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (empleado_id) REFERENCES empleados(id),
                FOREIGN KEY (concepto_id) REFERENCES conceptos_nomina(id)
            )
        """)

        # Tabla para registrar los valores calculados de conceptos por registro de nómina
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS registro_conceptos_nomina (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                registro_nomina_id INTEGER NOT NULL,
                concepto_id INTEGER,
                concepto_empleado_id INTEGER,
                concepto_nombre TEXT NOT NULL,
                tipo TEXT,
                naturaleza TEXT,
                valor_calculado REAL NOT NULL,
                metadata TEXT,
                fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (registro_nomina_id) REFERENCES registros_nomina(id),
                FOREIGN KEY (concepto_id) REFERENCES conceptos_nomina(id),
                FOREIGN KEY (concepto_empleado_id) REFERENCES conceptos_empleado(id)
            )
        """)
        self._connection.commit()

        # Seed inicial de conceptos si la tabla está vacía
        try:
            # Asegurar columnas nuevas (migración ligera) antes de insertar seed
            self._ensure_concept_columns()
            self._ensure_empleado_columns()
            self._seed_conceptos_if_empty()
        except Exception as e:
            print(f"Error al sembrar datos iniciales de conceptos: {e}")

    def get_connection(self) -> sqlite3.Connection:
        """Retorna la conexión activa a la BD."""
        if self._connection is None:
            self._initialize_database()
        return self._connection

    def close(self) -> None:
        """Cierra la conexión a la BD."""
        if self._connection:
            self._connection.close()
            self._connection = None

    def execute(self, query: str, params: tuple = ()) -> Optional[list]:
        """Ejecuta una consulta SELECT."""
        try:
            cursor = self._connection.cursor()
            cursor.execute(query, params)
            return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Error en execute: {e}")
            return None

    def execute_update(self, query: str, params: tuple = ()) -> bool:
        """Ejecuta una consulta INSERT/UPDATE/DELETE."""
        try:
            cursor = self._connection.cursor()
            cursor.execute(query, params)
            self._connection.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error en execute_update: {e}")
            self._connection.rollback()
            return False

    def _seed_conceptos_if_empty(self) -> None:
        """Inserta conceptos básicos en `conceptos_nomina` si la tabla está vacía."""
        cursor = self._connection.cursor()
        cursor.execute("SELECT COUNT(*) as cnt FROM conceptos_nomina")
        row = cursor.fetchone()
        try:
            count = int(row[0]) if row is not None else 0
        except Exception:
            count = 0

        if count > 0:
            return

        seeds = [
            {"nombre": "Horas Extras Diurnas", "tipo": "variable", "naturaleza": "devengado", "valor": None, "porcentaje": None, "base_calculo": None},
            {"nombre": "Horas Extras Nocturnas", "tipo": "variable", "naturaleza": "devengado", "valor": None, "porcentaje": None, "base_calculo": None},
            {"nombre": "Comisión de Ventas", "tipo": "porcentaje", "naturaleza": "devengado", "valor": None, "porcentaje": 5.0, "base_calculo": "ventas"},
            {"nombre": "Bono de Puntualidad", "tipo": "fijo", "naturaleza": "devengado", "valor": 50000.0, "porcentaje": None, "base_calculo": None},
            {"nombre": "Auxilio de Alimentación", "tipo": "fijo", "naturaleza": "devengado", "valor": 0.0, "porcentaje": None, "base_calculo": None},
            {"nombre": "Préstamo Empresa", "tipo": "fijo", "naturaleza": "deduccion", "valor": 0.0, "porcentaje": None, "base_calculo": None},
            {"nombre": "Embargo Judicial", "tipo": "fijo", "naturaleza": "deduccion", "valor": 0.0, "porcentaje": None, "base_calculo": None},
        ]

        for s in seeds:
            try:
                cursor.execute(
                    """
                    INSERT INTO conceptos_nomina (nombre, tipo, naturaleza, valor, porcentaje, base_calculo, activo)
                    VALUES (?, ?, ?, ?, ?, ?, 1)
                    """,
                    (
                        s["nombre"],
                        s["tipo"],
                        s["naturaleza"],
                        s["valor"],
                        s["porcentaje"],
                        s["base_calculo"],
                    ),
                )
            except Exception as e:
                # Si falla inserción individual, loguear de forma concisa
                print(f"Seed insert failed ({s['nombre']}): {e}")

        self._connection.commit()

    def _ensure_concept_columns(self) -> None:
        """Asegura que las columnas 'naturaleza' existen en las tablas relacionadas.

        Hace ALTER TABLE para añadir columnas faltantes si la tabla ya existe
        (migración ligera, no destructiva).
        """
        cursor = self._connection.cursor()

        # Helper para comprobar columnas
        def has_column(table: str, column: str) -> bool:
            try:
                cursor.execute(f"PRAGMA table_info({table})")
                cols = [r[1] for r in cursor.fetchall()]
                return column in cols
            except Exception:
                return False

        # Añadir 'naturaleza' si falta en conceptos_nomina
        if not has_column('conceptos_nomina', 'naturaleza'):
            try:
                cursor.execute("ALTER TABLE conceptos_nomina ADD COLUMN naturaleza TEXT DEFAULT 'devengado'")
            except Exception as e:
                print(f"No se pudo agregar columna 'naturaleza' a conceptos_nomina: {e}")

        # Añadir 'naturaleza' si falta en conceptos_empleado
        if not has_column('conceptos_empleado', 'naturaleza'):
            try:
                cursor.execute("ALTER TABLE conceptos_empleado ADD COLUMN naturaleza TEXT DEFAULT 'devengado'")
            except Exception as e:
                print(f"No se pudo agregar columna 'naturaleza' a conceptos_empleado: {e}")

        # Añadir 'naturaleza' si falta en registro_conceptos_nomina
        if not has_column('registro_conceptos_nomina', 'naturaleza'):
            try:
                cursor.execute("ALTER TABLE registro_conceptos_nomina ADD COLUMN naturaleza TEXT")
            except Exception as e:
                print(f"No se pudo agregar columna 'naturaleza' a registro_conceptos_nomina: {e}")

        self._connection.commit()

    def _ensure_empleado_columns(self) -> None:
        """Asegura que la columna 'recibe_auxilio_transporte' existe en la tabla empleados.

        Hace ALTER TABLE para añadir la columna si la tabla ya existe
        (migración ligera, no destructiva).
        """
        cursor = self._connection.cursor()

        # Helper para comprobar columnas
        def has_column(table: str, column: str) -> bool:
            try:
                cursor.execute(f"PRAGMA table_info({table})")
                cols = [r[1] for r in cursor.fetchall()]
                return column in cols
            except Exception:
                return False

        # Añadir 'recibe_auxilio_transporte' si falta en empleados
        if not has_column('empleados', 'recibe_auxilio_transporte'):
            try:
                cursor.execute("ALTER TABLE empleados ADD COLUMN recibe_auxilio_transporte INTEGER DEFAULT 1")
                self._connection.commit()
            except Exception as e:
                print(f"No se pudo agregar columna 'recibe_auxilio_transporte' a empleados: {e}")