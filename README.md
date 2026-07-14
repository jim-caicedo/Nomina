```markdown
# IMPLEMENTACIÓN COMPLETADA: Sistema de Nómina con SQLite & Reportes Avanzados

## 📊 Resumen del Proyecto

Sistema integral de gestión de nómina para empresas colombianas, implementado en Python con `customtkinter` para la interfaz gráfica, `SQLite` para persistencia de datos, y módulos avanzados de exportación de reportes.

### Características Principales

✅ **CRUD de Empleados**: Crear, leer, actualizar, eliminar empleados con todos sus datos  
✅ **Cálculo de Nómina**: Liquidación quincenal automática según leyes colombianas  
✅ **Configuración Legal**: Gestión centralizada de parámetros anuales  
✅ **Historial de Cambios**: Auditoría completa de modificaciones de configuración  
✅ **Validaciones**: Validaciones automáticas en todos los niveles (UI, negocio, BD)  
✅ **Interfaz Responsiva**: UI moderna con `customtkinter` y temas oscuros  
✅ **Módulo de Reportes Excel**: Exportación unificada de la quincena compatible con la banca  
✅ **Desprendibles PDF**: Generación automática de colillas de pago individuales por empleado  
✅ **Soporte Multiplataforma**: Sistema inteligente optimizado tanto para entornos de desarrollo Linux (Kali) como para despliegues de producción en Windows  

---

## 🏗️ Arquitectura del Proyecto


```

NominaSG/
├── app.py                           # Punto de entrada
├── requirements.txt
├── config/
│   └── constants.py                # Constantes globales (2026)
├── database/
│   ├── db_manager.py               # Singleton SQLite
│   └── seed_data.py                # Script inicializador
├── models/
│   ├── empleado.py                 # Dataclass Empleado
│   ├── empleado_repository.py       # Repositorio Empleados
│   ├── registro_nomina.py           # Dataclass RegistroNomina
│   ├── nomina_repository.py         # Repositorio Nóminas
│   ├── configuracion.py             # Dataclass Configuración
│   └── configuracion_repository.py  # Repositorio SQLite
├── services/
│   └── nomina_calculator.py         # Cálculos de nómina
├── utils/
│   ├── excel_exporter.py           # Exportador de libros Excel (.xlsx)
│   └── pdf_generator.py            # Motor de renderizado de PDFs (ReportLab)
├── controllers/
│   ├── main_controller.py           # Controlador principal
│   └── configuracion_controller.py  # Controlador configuración
├── views/
│   ├── main_view.py                 # Ventana principal
│   ├── crud_empleado_view.py        # Vista CRUD empleados
│   ├── liquidar_nomina_view.py      # Vista liquidación con control dinámico de estados
│   └── configuracion_view.py        # Vista configuración
├── data/
│   └── nomina.db                    # Base de datos SQLite
├── desprendibles/                   # Carpetas automatizadas generadas por período
└── MIGRACION_SQLITE.md              # Documentación técnica

```

---

## 💾 Base de Datos SQLite

### Tablas Principales

#### `configuracion_legal`
Almacena todas las configuraciones de parámetros legales (histórico completo).

| Campo | Tipo | Descripción |
|-------|------|-------------|
| id | INTEGER PK | ID único (autoincremento) |
| anio_vigente | INTEGER | Año de la configuración |
| salario_minimo_mensual | REAL | SMMLV |
| auxilio_transporte_mensual | REAL | Auxilio transporte |
| porcentaje_afp | REAL | % AFP (pensión) |
| porcentaje_eps | REAL | % EPS (salud) |
| fecha_creacion | TIMESTAMP | Cuándo se creó |
| activa | INTEGER | 1=Activa, 0=Inactiva |

#### `historial_cambios`
Registro detallado de todos los cambios realizados.

| Campo | Tipo | Descripción |
|-------|------|-------------|
| id | INTEGER PK | ID único |
| campo_cambiado | TEXT | Qué cambió |
| valor_anterior | TEXT | Valor antes |
| valor_nuevo | TEXT | Valor después |
| fecha_cambio | TIMESTAMP | Cuándo |
| usuario | TEXT | Quién hizo el cambio |

---

## 🔄 Modelo de Datos

### Empleado
```python
@dataclass
class Empleado:
    id: int
    nombre: str
    apellido: str
    cargo: str
    salario: float
    correo: str = ""
    telefono: str = ""
    numero_cuenta: str = ""
    eps: str = "EPS"
    afp: str = "AFP"
    sede_laboral: str = "Principal"
    auxilio_transporte_mensual: float = 161916.0
    fecha_ingreso: str = ""
    horas_extra: float = 0.0

```

### ConfiguracionNomina

```python
@dataclass
class ConfiguracionNomina:
    id: Optional[int] = None
    anio_vigente: int = 2026
    salario_minimo_mensual: float = 1315000.0
    auxilio_transporte_mensual: float = 161916.0
    porcentaje_afp: float = 0.04        # 4%
    porcentaje_eps: float = 0.04        # 4%
    fecha_creacion: Optional[str] = None
    activa: bool = True

```

### RegistroNomina

Almacena resultado de una liquidación para un empleado.

```python
@dataclass
class RegistroNomina:
    id: int
    empleado_id: int
    periodo_inicio: date
    periodo_cierre: date
    dias_laborados: int
    salario_base_periodo: float
    auxilio_transporte_periodo: float
    horas_extras: int
    valor_horas_extras: float
    total_devengado: float
    descuento_afp: float
    descuento_eps: float
    otros_descuentos: float
    total_deducciones: float
    salario_neto: float

```

---

## 📐 Fórmulas de Cálculo (Ley Colombiana)

### Devengados

```
Ordinario = (Salario Base / 30) × Días Laborados
Auxilio Transporte = (Auxilio Mensual / 30) × Días Laborados
Horas Extras = Valor Hora Extra × Cantidad
Total Devengado = Ordinario + Auxilio + Horas Extras

```

### Deducciones

```
AFP = Ordinario × 4%          (SOLO sobre ordinario, no auxilio)
EPS = Ordinario × 4%          (SOLO sobre ordinario, no auxilio)
Total Deducciones = AFP + EPS + Otros Descuentos

```

### Salario Neto

```
Salario Neto = Total Devengado - Total Deducciones

```

---

## 🎯 Funcionalidades Principales

### 1. Gestión de Empleados

* **Operaciones CRUD completas** con interfaz gráfica adaptada.
* **Datos Avanzados**: Manejo de cuentas bancarias, sedes, entidades de salud (EPS) y pensiones (AFP).

### 2. Liquidación de Nómina

* Cálculo automático en lote para toda la planilla activa basándose en el rango de fechas.
* Visualización interactiva previa en un contenedor scrollable moderno.

### 3. Módulo de Exportación y Reportes Automatizados 🚀

* **Exportación a Excel**: Estructura libros unificados por quincena utilizando `openpyxl`.
* **Desprendibles PDF Masivos**: Generación en paralelo de las colillas de pago individuales. El sistema crea automáticamente directorios organizados por fecha de corte (`desprendibles/quincena_AAAA_MM_DD/`) y guarda cada archivo con una nomenclatura limpia: `Nombre_Apellido_FechaCorte.pdf`.
* **Control de Flujo UI**: El botón de acceso a los PDFs permanece bloqueado protegiendo el ciclo de la aplicación y solo se activa tras una escritura de datos exitosa.

### 4. Configuración Legal & Auditoría

* Actualización de parámetros globales en caliente con bitácora relacional automática de valores anteriores y nuevos.

---

## 🔐 Seguridad y Multiplataforma

✅ **Historial Completo**: Todos los cambios de configuración quedan registrados

✅ **Auditoría**: Cada cambio tiene timestamp y usuario

✅ **Transacciones**: SQLite garantiza integridad de datos

✅ **Estrategia Multiplataforma**: El sistema detecta mediante la capa `platform` el OS en ejecución. En sistemas Linux invoca subprocesos `xdg-open` y en entornos Windows conmuta dinámicamente a la API nativa `os.startfile`, garantizando estabilidad total pre-compilación.

---

## 🚀 Cómo Usar

### Instalación de dependencias

```bash
pip install customtkinter openpyxl tkcalendar babel reportlab pyinstaller

```

### Ejecutar Aplicación

```bash
python app.py

```

### Compilación para Producción (Windows)

Para generar el ejecutable standalone (`.exe`) limpio y sin ventanas de comando en segundo plano:

```bash
pyinstaller --noconsole --onefile app.py

```

---

## 📦 Dependencias Core

```
customtkinter==5.2.2
openpyxl==3.1.2
reportlab==4.1.0
tkcalendar==1.6.1

```

---

## ✨ Mejoras Futuras (Siguiente Versión)

* [ ] Módulo integrado de liquidación de prestaciones sociales (Primas, Cesantías e Intereses).
* [ ] Módulo para cálculo de liquidaciones definitivas por retiro de personal.
* [ ] Integración directa con pasarelas de dispersión bancaria.
* [ ] Sistema multiusuario con control de roles y permisos.

---

## 👨‍💻 Autor: Jim Alejandro Caicedo Osorio

Desarrollado con arquitectura limpia y robusta, diseñado para cumplir estrictamente con los requisitos normativos del entorno empresarial colombiano.
