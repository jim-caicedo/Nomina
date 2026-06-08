"""
Exportador de nómina a Excel.
Genera archivos Excel con formato profesional para liquidaciones de nómina.
"""

from datetime import date
from typing import List
from models.registro_nomina import RegistroNomina


def exportar_nomina_a_excel(
    registros: List[RegistroNomina],
    periodo_inicio: date,
    periodo_cierre: date,
    ruta_archivo: str = None,
) -> str:
    """
    Exporta los registros de nómina a un archivo Excel.

    Args:
        registros: Lista de registros de nómina a exportar
        periodo_inicio: Fecha de inicio del período
        periodo_cierre: Fecha de cierre del período
        ruta_archivo: Ruta donde guardar el archivo (opcional)

    Returns:
        Ruta del archivo Excel generado

    Raises:
        ImportError: Si openpyxl no está instalado
        Exception: Si hay error al generar el archivo
    """
    try:
        import openpyxl
        from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
    except ImportError:
        raise ImportError(
            "openpyxl no está instalado. Ejecuta: pip install openpyxl"
        )

    # Crear libro de trabajo
    wb = openpyxl.Workbook()
    wb.remove(wb.active)  # Eliminar hoja por defecto

    # ========== HOJA 1: RESUMEN ==========
    ws_resumen = wb.create_sheet("Resumen")

    # Título
    ws_resumen.merge_cells("A1:E1")
    ws_resumen["A1"] = f"RESUMEN DE NÓMINA"
    ws_resumen["A1"].font = Font(name="Arial", size=16, bold=True)
    ws_resumen["A1"].alignment = Alignment(horizontal="center", vertical="center")

    # Período
    ws_resumen.merge_cells("A2:E2")
    ws_resumen["A2"] = (
        f"Período: {periodo_inicio.strftime('%d/%m/%Y')} - "
        f"{periodo_cierre.strftime('%d/%m/%Y')}"
    )
    ws_resumen["A2"].font = Font(name="Arial", size=12, bold=True)
    ws_resumen["A2"].alignment = Alignment(horizontal="center", vertical="center")

    # Calcular totales
    total_empleados = len(registros)
    total_devengado = sum(r.total_devengado for r in registros)
    total_deducciones = sum(r.total_deducciones for r in registros)
    total_neto = sum(r.salario_neto for r in registros)

    # Datos de resumen
    datos_resumen = [
        ["", "", "", "", ""],
        ["Total Empleados:", total_empleados, "", "", ""],
        ["Total Devengado:", f"${total_devengado:,.2f}", "", "", ""],
        ["Total Deducciones:", f"${total_deducciones:,.2f}", "", "", ""],
        ["Nómina Neta:", f"${total_neto:,.2f}", "", "", ""],
    ]

    for row_idx, row_data in enumerate(datos_resumen, start=4):
        for col_idx, value in enumerate(row_data, start=1):
            cell = ws_resumen.cell(row=row_idx, column=col_idx, value=value)
            if col_idx == 1:
                cell.font = Font(name="Arial", size=11, bold=True)
                cell.alignment = Alignment(horizontal="right")
            else:
                cell.font = Font(name="Arial", size=11)
                cell.alignment = Alignment(horizontal="left")

    # Ajustar ancho de columnas
    ws_resumen.column_dimensions["A"].width = 20
    ws_resumen.column_dimensions["B"].width = 20

    # ========== HOJA 2: DETALLE POR EMPLEADO ==========
    ws_detalle = wb.create_sheet("Detalle")

    # Título
    ws_detalle.merge_cells("A1:L1")
    ws_detalle["A1"] = "DETALLE DE LIQUIDACIÓN POR EMPLEADO"
    ws_detalle["A1"].font = Font(name="Arial", size=14, bold=True)
    ws_detalle["A1"].alignment = Alignment(horizontal="center", vertical="center")

    # Período
    ws_detalle.merge_cells("A2:L2")
    ws_detalle["A2"] = (
        f"Período: {periodo_inicio.strftime('%d/%m/%Y')} - "
        f"{periodo_cierre.strftime('%d/%m/%Y')}"
    )
    ws_detalle["A2"].font = Font(name="Arial", size=11, bold=True)
    ws_detalle["A2"].alignment = Alignment(horizontal="center", vertical="center")

    # Encabezados de tabla
    headers = [
        "Nº",
        "ID Empleado",
        "Periodo Inicio",
        "Periodo Cierre",
        "Días Laborados",
        "Salario Base",
        "Auxilio Transporte",
        "Horas Extras",
        "Total Devengado",
        "Descuento AFP",
        "Descuento EPS",
        "Salario Neto",
    ]

    # Estilo para encabezados
    header_fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
    header_font = Font(name="Arial", size=10, bold=True, color="FFFFFF")
    header_alignment = Alignment(horizontal="center", vertical="center")

    # Escribir encabezados
    for col_idx, header in enumerate(headers, start=1):
        cell = ws_detalle.cell(row=4, column=col_idx, value=header)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = header_alignment

    # Escribir datos
    thin_border = Border(
        left=Side(style="thin"),
        right=Side(style="thin"),
        top=Side(style="thin"),
        bottom=Side(style="thin"),
    )

    for row_idx, registro in enumerate(registros, start=5):
        datos_fila = [
            row_idx - 4,  # Nº
            registro.empleado_id,
            registro.periodo_inicio.strftime("%d/%m/%Y"),
            registro.periodo_cierre.strftime("%d/%m/%Y"),
            registro.dias_laborados,
            registro.salario_base_periodo,
            registro.auxilio_transporte_periodo,
            registro.horas_extras,
            registro.total_devengado,
            registro.descuento_afp,
            registro.descuento_eps,
            registro.salario_neto,
        ]

        for col_idx, valor in enumerate(datos_fila, start=1):
            cell = ws_detalle.cell(row=row_idx, column=col_idx, value=valor)
            cell.border = thin_border
            cell.font = Font(name="Arial", size=10)
            cell.alignment = Alignment(horizontal="center", vertical="center")

    # Ajustar ancho de columnas
    column_widths = [6, 12, 15, 15, 12, 15, 18, 12, 15, 12, 12, 15]
    for col_idx, width in enumerate(column_widths, start=1):
        ws_detalle.column_dimensions[openpyxl.utils.get_column_letter(col_idx)].width = width

    # Generar nombre de archivo si no se proporciona
    if ruta_archivo is None:
        ruta_archivo = f"nomina_{periodo_inicio.strftime('%Y%m%d')}_"
        ruta_archivo += f"{periodo_cierre.strftime('%Y%m%d')}.xlsx"

    # Guardar archivo
    wb.save(ruta_archivo)
    return ruta_archivo
