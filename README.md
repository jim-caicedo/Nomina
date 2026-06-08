# Sistema de Gestión de Nómina

Aplicación ejemplo de nómina usando el patrón MVC con `customtkinter` y datos de prueba.

## Requisitos

- Python 3.10+ (recomendado)
- `venv` para entornos virtuales

## Instalación

```bash
cd /home/kjim/Escritorio/NominaSG
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

## Ejecución

```bash
source .venv/bin/activate
python app.py
```

## Estructura del proyecto

- `models/` - Clases de dominio: `Empleado` y `Nomina`
- `controllers/` - Lógica de negocio y datos de prueba
- `views/` - Interfaz gráfica con `customtkinter`
- `app.py` - Punto de entrada de la aplicación

## Nota

En esta versión no se usa base de datos; los empleados se cargan desde datos mock en memoria.
