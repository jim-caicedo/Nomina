"""
Constantes de interfaz de usuario (colores, formatos).
No contiene parámetros legales de nómina; esos viven en SQLite (data/nomina.db).
"""

FORMATO_FECHA = "%d/%m/%Y"
FORMATO_MONEDA = "${:,.2f}"

COLORES = {
    "success": "#10b981",
    "primary": "#3b82f6",
    "warning": "#f59e0b",
    "danger": "#ef4444",
    "neutral": "#6b7280",
    "secondary": "#0ea5e9",
}
