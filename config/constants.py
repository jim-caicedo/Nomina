"""
Constantes globales del sistema NominaSG.
Valores para cálculos de nómina ley colombiana 2026.
"""

# Valores legales 2026 (Colombia)
SALARIO_MINIMO_2026 = 1_315_000.0  # Salario Mínimo Mensual Legal Vigente
AUXILIO_TRANSPORTE_2026 = 161_916  # Valor mensual en pesos colombianos

# Cálculos de nómina
DIAS_MES_PROMEDIO = 30
PORCENTAJE_AFP = 0.04  # 4% para pensión
PORCENTAJE_EPS = 0.04  # 4% para salud

# Valores hora extra (a definir según cliente)
VALOR_HORA_EXTRA = 25.0

# Formatos
FORMATO_FECHA = "%d/%m/%Y"
FORMATO_MONEDA = "${:,.2f}"

# UI Constants
COLORES = {
    "success": "#10b981",
    "primary": "#3b82f6",
    "warning": "#f59e0b",
    "danger": "#ef4444",
    "neutral": "#6b7280",
    "secondary": "#0ea5e9",
}
