# Migración de Configuración a SQLite

## 📋 Estado de la Implementación

### ✅ Completado

1. **Database Manager (SQLite)**
   - `database/db_manager.py`: Singleton para gestionar conexión SQLite
   - Tablas creadas: `configuracion_legal` y `historial_cambios`
   - Inicialización automática con configuración por defecto 2026

2. **Repositorio SQLite**
   - `models/configuracion_repository.py`: Completamente migrado a SQLite
   - Métodos:
     - `obtener_configuracion_actual()`: Obtiene configuración activa
     - `guardar_configuracion()`: Guarda y desactiva anterior
     - `obtener_historial()`: Historial de todas las configuraciones
     - `obtener_historial_cambios()`: Cambios detallados

3. **Controlador**
   - `controllers/configuracion_controller.py`: Actualizado a SQLite
   - Métodos disponibles:
     - `cargar_configuracion()`: Carga config actual
     - `guardar_configuracion()`: Valida y guarda nueva config
     - `restaurar_defaults_2026()`: Restaura valores por defecto
     - `obtener_historial_configuraciones()`: Historial formateado
     - `obtener_historial_cambios()`: Cambios del historial
     - `obtener_configuracion_obj()`: Retorna objeto ConfiguracionNomina

4. **Vista de Configuración**
   - `views/configuracion_view.py`: Completamente funcional
   - Características:
     - Formulario para editar parámetros legales
     - Validaciones integradas
     - Botón para ver historial en ventana modal
     - Botón para ver cambios detallados
     - Restaurar valores por defecto

5. **Integración con Nómina**
   - `services/nomina_calculator.py`: Ya soporta ConfiguracionNomina
   - `controllers/main_controller.py`: Usa `config_controller.obtener_configuracion_obj()`

### 📊 Schema SQLite

#### Tabla: configuracion_legal
```sql
CREATE TABLE IF NOT EXISTS configuracion_legal (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    anio_vigente INTEGER NOT NULL,
    salario_minimo_mensual REAL NOT NULL,
    auxilio_transporte_mensual REAL NOT NULL,
    porcentaje_afp REAL NOT NULL,
    porcentaje_eps REAL NOT NULL,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    activa INTEGER DEFAULT 1
);
```

#### Tabla: historial_cambios
```sql
CREATE TABLE IF NOT EXISTS historial_cambios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    campo_cambiado TEXT NOT NULL,
    valor_anterior TEXT NOT NULL,
    valor_nuevo TEXT NOT NULL,
    fecha_cambio TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario TEXT DEFAULT 'admin'
);
```

## 🔄 Flujo de Actualización de Configuración

1. Usuario modifica parámetros en formulario
2. `ConfiguracionController.guardar_configuracion()` valida datos
3. Repositorio obtiene configuración activa anterior
4. Desactiva configuración anterior (activa = 0)
5. Inserta nueva configuración (activa = 1)
6. Registra cambios en `historial_cambios`
7. Cambios se aplican automáticamente en próximas liquidaciones

## 📝 Modelo ConfiguracionNomina

```python
@dataclass
class ConfiguracionNomina:
    id: Optional[int] = None                    # Auto-generado por SQLite
    anio_vigente: int = 2026
    salario_minimo_mensual: float = 1315000.0
    auxilio_transporte_mensual: float = 161916.0
    porcentaje_afp: float = 0.04               # 4%
    porcentaje_eps: float = 0.04               # 4%
    fecha_creacion: Optional[str] = None       # Auto-generado por SQLite
    activa: bool = True
```

## 🚀 Uso en Aplicación

### Cargar configuración activa
```python
controller = ConfiguracionController()
config = controller.obtener_configuracion_obj()
print(f"SMMLV: {config.salario_minimo_mensual}")
```

### Guardar nueva configuración
```python
resultado = controller.guardar_configuracion(
    anio=2027,
    salario_minimo=1400000,
    auxilio_transporte=165000,
    porcentaje_afp=0.04,
    porcentaje_eps=0.04
)
if resultado["success"]:
    print("Configuración guardada")
```

### Ver historial
```python
historial = controller.obtener_historial_configuraciones()
for config in historial:
    estado = "Activa" if config["activa"] else "Inactiva"
    print(f"{config['anio_vigente']}: {estado}")
```

## 🔒 Seguridad y Auditoría

- ✅ Historial completo de cambios
- ✅ Timestamp automático de cambios
- ✅ Usuario registrado en cambios
- ✅ Configuración anterior guardada (nunca eliminada)
- ✅ Solo una configuración activa a la vez
- ✅ Transacciones SQLite para integridad

## 📁 Ubicación de Base de Datos

- **Archivo**: `/data/nomina.db`
- **Tipo**: SQLite3
- **Acceso**: Singleton DBManager

## 🔗 Dependencias

- `database/db_manager.py`: Gestor de conexión
- `models/configuracion.py`: Dataclass del modelo
- `models/configuracion_repository.py`: Operaciones CRUD
- `controllers/configuracion_controller.py`: Lógica de negocio
- `views/configuracion_view.py`: Interfaz de usuario

## ✨ Mejoras Futuras

- [ ] Exportar historial a Excel
- [ ] Copiar configuración de períodos anteriores
- [ ] Validación de cambios antes de guardar
- [ ] Búsqueda en historial por fecha/campo
- [ ] Reversión de cambios (rollback)
