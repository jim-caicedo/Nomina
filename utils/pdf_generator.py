"""
Generador de desprendibles de pago en PDF.
Maqueta desprendibles verticales profesionales tipo colilla para S.G. DIGITAL S.A.S.
"""

import os
from datetime import date
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Spacer, Paragraph
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

def generar_desprendible_pdf(registro, ruta_pdf: str = None) -> str:
    """
    Genera un desprendible de pago único en formato PDF basado en la colilla real.
    
    Args:
        registro: Objeto RegistroNomina con el atributo .empleado ya cargado.
        ruta_pdf: Ruta de destino (Opcional).
        
    Returns:
        str: Ruta del archivo PDF generado.
    """
    emp = getattr(registro, "empleado", None)
    if not emp:
        raise ValueError("El registro de nómina debe contener la entidad empleado cargada.")

    # Definir ruta por defecto si no se proporciona una
    if not ruta_pdf:
        nombre_archivo = f"desprendible_{emp.id}_{registro.periodo_cierre.strftime('%Y%m%d')}.pdf"
        ruta_pdf = os.path.join(os.getcwd(), nombre_archivo)

    # Configuración del documento (tamaño carta, márgenes ajustados)
    doc = SimpleDocTemplate(
        ruta_pdf,
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )

    story = []
    styles = getSampleStyleSheet()

    # Estilos personalizados de texto
    style_center_bold = ParagraphStyle(
        'CenterBold', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=10, alignment=1
    )
    style_left_bold = ParagraphStyle(
        'LeftBold', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=9, alignment=0
    )
    style_left_normal = ParagraphStyle(
        'LeftNormal', parent=styles['Normal'], fontName='Helvetica', fontSize=9, alignment=0
    )
    style_right_normal = ParagraphStyle(
        'RightNormal', parent=styles['Normal'], fontName='Helvetica', fontSize=9, alignment=2
    )

    # -------------------------------------------------------------------------
    # BLOQUE 1: ENCABEZADO Y DATOS MAESTROS DEL EMPLEADO
    # -------------------------------------------------------------------------
    # Mapeamos 1 a 1 los campos extraídos del script de SQLite de la tabla empleados
    datos_maestros = [
        [Paragraph("4", style_center_bold), ""],
        [Paragraph("S.G. DIGITAL S.A.S.", style_center_bold), ""],
        [Paragraph("CODIGO", style_left_bold), Paragraph(str(emp.id), style_center_bold)],
        [Paragraph("PERIODO INICIO", style_left_bold), Paragraph(registro.periodo_inicio.strftime('%d/%m/%Y'), style_left_normal)],
        [Paragraph("PERIODO CIERRE", style_left_bold), Paragraph(registro.periodo_cierre.strftime('%d/%m/%Y'), style_left_normal)],
        [Paragraph("SEDE LABORAL", style_left_bold), Paragraph(getattr(emp, "sede_laboral", "CALLE 27") or "CALLE 27", style_left_normal)],
        [Paragraph("NOMBRE", style_left_bold), Paragraph(f"{getattr(emp, 'apellido', '')} {getattr(emp, 'nombre', '')}".strip().upper(), style_left_normal)],
        [Paragraph("CEDULA", style_left_bold), Paragraph(str(getattr(emp, "cedula", "")), style_left_normal)],
        [Paragraph("BASICO", style_left_bold), Paragraph(f"${getattr(emp, 'salario', 0):,.0f}".replace(",", "."), style_left_normal)],
        [Paragraph(f"Nº BANCO {getattr(emp, 'codigo_banco', 'COLPATRIA') or 'COLPATRIA'}", style_left_bold), Paragraph(str(getattr(emp, "numero_cuenta", "")), style_left_normal)],
        [Paragraph("CORREO", style_left_bold), Paragraph(getattr(emp, "correo", "") or "", style_left_normal)],
        [Paragraph("CARGO", style_left_bold), Paragraph(getattr(emp, "cargo", "").upper(), style_left_normal)],
        [Paragraph("AFP", style_left_bold), Paragraph(getattr(emp, "afp", "").upper() or "PORVENIR", style_left_normal)],
        [Paragraph("EPS", style_left_bold), Paragraph(getattr(emp, "eps", "").upper() or "NUEVA EPS", style_left_normal)],
    ]

    # Ajustamos el ancho exacto para simular la colilla vertical de la captura (Ancho total: 530)
    tabla_maestra = Table(datos_maestros, colWidths=[180, 350])
    tabla_maestra.setStyle(TableStyle([
        # Combinar celdas para el título principal y el indicador superior
        ('SPAN', (0, 0), (1, 0)),
        ('SPAN', (0, 1), (1, 1)),
        # Cuadrícula general negra y delgada como la colilla real
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        # Color amarillo de fondo para resaltar el campo Código
        ('BACKGROUND', (1, 2), (1, 2), colors.yellow),
    ]))
    
    story.append(tabla_maestra)
    story.append(Spacer(1, 15))

    # -------------------------------------------------------------------------
    # BLOQUE 2: TABLA DE CONCEPTOS (DEVENGADOS / DEDUCCIONES)
    # -------------------------------------------------------------------------
    # Encabezado del desglose dinámico
    conceptos_tabla = [
        [
            Paragraph("DESCRIPCION CONCEPTO", style_center_bold), 
            Paragraph("CANTIDAD", style_center_bold), 
            Paragraph("DEVENGADO / DEDUCIDO", style_center_bold)
        ]
    ]

    # Fila base: Salario Quincenal / Mensual Liquidado
    conceptos_tabla.append([
        Paragraph("SUELDO BÁSICO PERIODO", style_left_normal),
        Paragraph(str(registro.dias_laborados), style_center_bold),
        Paragraph(f"${registro.salario_base_periodo:,.0f}".replace(",", "."), style_right_normal)
    ])

    # Inyectar auxilio de transporte si aplica
    if getattr(registro, "auxilio_transporte_periodo", 0) > 0:
        conceptos_tabla.append([
            Paragraph("AUXILIO DE TRANSPORTE", style_left_normal),
            Paragraph("", style_center_bold),
            Paragraph(f"${registro.auxilio_transporte_periodo:,.0f}".replace(",", "."), style_right_normal)
        ])

    # Horas extras
    if getattr(registro, "horas_extras", 0) > 0:
        conceptos_tabla.append([
            Paragraph(f"HORAS EXTRAS ({registro.horas_extras})", style_left_normal),
            Paragraph("", style_center_bold),
            Paragraph(f"${getattr(registro, 'valor_horas_extras', 0):,.0f}".replace(",", "."), style_right_normal)
        ])

    # Deducciones de Ley Obligatorias
    if getattr(registro, "descuento_eps", 0) > 0:
        conceptos_tabla.append([
            Paragraph("DEDUCCIÓN EPS (SALUD)", style_left_normal),
            Paragraph("", style_center_bold),
            Paragraph(f"-${registro.descuento_eps:,.0f}".replace(",", "."), style_right_normal)
        ])
    if getattr(registro, "descuento_afp", 0) > 0:
        conceptos_tabla.append([
            Paragraph("DEDUCCIÓN AFP (PENSIÓN)", style_left_normal),
            Paragraph("", style_center_bold),
            Paragraph(f"-${registro.descuento_afp:,.0f}".replace(",", "."), style_right_normal)
        ])

    # Otros Descuentos / Conceptos adicionales
    if getattr(registro, "otros_descuentos", 0) > 0:
        conceptos_tabla.append([
            Paragraph("OTROS DESCUENTOS / ADICIONALES", style_left_normal),
            Paragraph("", style_center_bold),
            Paragraph(f"-${registro.otros_descuentos:,.0f}".replace(",", "."), style_right_normal)
        ])

    # Fila de Cierre: NETO A RECIBIR
    conceptos_tabla.append([
        Paragraph("NETO PAGADO EFECTIVO", style_left_bold),
        Paragraph("", style_center_bold),
        Paragraph(f"${registro.salario_neto:,.0f}".replace(",", "."), style_right_normal)
    ])

    # Formatear la tabla inferior de conceptos dinámicos
    tabla_conceptos = Table(conceptos_tabla, colWidths=[230, 100, 200])
    tabla_conceptos.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        # Resaltar fila de totales finales
        ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
    ]))

    story.append(tabla_conceptos)

    # Construir y renderizar el PDF
    doc.build(story)
    return ruta_pdf