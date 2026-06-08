"""
Vista de liquidación de nómina quincenal.
Permite calcular y visualizar la nómina de todos los empleados en un período.
"""

import customtkinter as ctk
from tkinter import messagebox, filedialog
from datetime import datetime, date
from controllers.main_controller import MainController
from config.constants import COLORES, FORMATO_FECHA
from utils.excel_exporter import exportar_nomina_a_excel


class LiquidarNominaView:
    """Vista para la liquidación de nómina."""

    def __init__(self, content_frame: ctk.CTkFrame, controller: MainController):
        self.content_frame = content_frame
        self.controller = controller
        self.frame = None

        # Variables de entrada
        self.entrada_fecha_inicio = None
        self.entrada_fecha_cierre = None
        self.entrada_dias_laborados = None
        self.entrada_horas_extras = None

        # Frame de resultados
        self.scroll_resultados = None
        self.label_totales = None

    def crear_frame(self) -> ctk.CTkFrame:
        """Crea el frame principal de liquidación de nómina."""
        self.frame = ctk.CTkFrame(self.content_frame, corner_radius=20)
        self.frame.grid(row=0, column=0, sticky="nsew")
        self.frame.grid_rowconfigure(3, weight=1)
        self.frame.grid_columnconfigure(0, weight=1)

        # ========== ENCABEZADO ==========
        header = ctk.CTkLabel(
            self.frame,
            text="Liquidación de Nómina Quincenal",
            font=ctk.CTkFont(size=26, weight="bold"),
        )
        header.grid(row=0, column=0, sticky="w", padx=20, pady=(20, 10))

        # ========== FORMULARIO ==========
        form_frame = ctk.CTkFrame(self.frame, fg_color="#1f2937", corner_radius=16)
        form_frame.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="ew")
        form_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)

        # Fila 1: Fechas
        ctk.CTkLabel(
            form_frame, text="Fecha Inicio (DD/MM/YYYY):", font=ctk.CTkFont(size=12, weight="bold")
        ).grid(row=0, column=0, padx=12, pady=(16, 4), sticky="w")
        self.entrada_fecha_inicio = ctk.CTkEntry(
            form_frame, placeholder_text="Ej: 01/05/2026", height=36
        )
        self.entrada_fecha_inicio.grid(row=1, column=0, padx=12, pady=(0, 12), sticky="ew")

        ctk.CTkLabel(
            form_frame, text="Fecha Cierre (DD/MM/YYYY):", font=ctk.CTkFont(size=12, weight="bold")
        ).grid(row=0, column=1, padx=12, pady=(16, 4), sticky="w")
        self.entrada_fecha_cierre = ctk.CTkEntry(
            form_frame, placeholder_text="Ej: 15/05/2026", height=36
        )
        self.entrada_fecha_cierre.grid(row=1, column=1, padx=12, pady=(0, 12), sticky="ew")

        ctk.CTkLabel(
            form_frame, text="Días Laborados:", font=ctk.CTkFont(size=12, weight="bold")
        ).grid(row=0, column=2, padx=12, pady=(16, 4), sticky="w")
        self.entrada_dias_laborados = ctk.CTkEntry(
            form_frame, placeholder_text="Ej: 15", height=36
        )
        self.entrada_dias_laborados.insert(0, "15")
        self.entrada_dias_laborados.grid(row=1, column=2, padx=12, pady=(0, 12), sticky="ew")

        ctk.CTkLabel(
            form_frame, text="Horas Extras:", font=ctk.CTkFont(size=12, weight="bold")
        ).grid(row=0, column=3, padx=12, pady=(16, 4), sticky="w")
        self.entrada_horas_extras = ctk.CTkEntry(
            form_frame, placeholder_text="Ej: 0", height=36
        )
        self.entrada_horas_extras.insert(0, "0")
        self.entrada_horas_extras.grid(row=1, column=3, padx=12, pady=(0, 12), sticky="ew")

        # Botones de acción
        botones_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        botones_frame.grid(row=2, column=0, columnspan=4, padx=12, pady=(0, 16), sticky="ew")
        botones_frame.grid_columnconfigure((0, 1), weight=1)

        btn_calcular = ctk.CTkButton(
            botones_frame,
            text="📊 Calcular Nómina",
            command=self._calcular_nomina,
            height=40,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color=COLORES["success"],
        )
        btn_calcular.grid(row=0, column=0, padx=6, sticky="ew")

        btn_exportar = ctk.CTkButton(
            botones_frame,
            text="📥 Exportar a Excel",
            command=self._exportar_excel,
            height=40,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color=COLORES["primary"],
        )
        btn_exportar.grid(row=0, column=1, padx=6, sticky="ew")

        # ========== RESULTADOS ==========
        resultados_header = ctk.CTkLabel(
            self.frame, text="Resultados de Liquidación", font=ctk.CTkFont(size=16, weight="bold")
        )
        resultados_header.grid(row=2, column=0, sticky="w", padx=20, pady=(0, 12))

        # Tabla de resultados
        tabla_container = ctk.CTkFrame(self.frame, fg_color="#1f2937", corner_radius=16)
        tabla_container.grid(row=3, column=0, padx=20, pady=(0, 20), sticky="nsew")
        tabla_container.grid_columnconfigure(0, weight=1)
        tabla_container.grid_rowconfigure(0, weight=1)

        # Scroll con resultados
        self.scroll_resultados = ctk.CTkScrollableFrame(
            tabla_container, corner_radius=12, fg_color="#111827"
        )
        self.scroll_resultados.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.scroll_resultados.grid_columnconfigure(0, weight=1)

        # Label vacío para mostrar mensaje inicial
        label_empty = ctk.CTkLabel(
            self.scroll_resultados,
            text="Ingresa los datos y haz clic en 'Calcular Nómina'",
            font=ctk.CTkFont(size=14),
            text_color="#9ca3af",
        )
        label_empty.grid(row=0, column=0, pady=30)

        # Label de totales
        self.label_totales = ctk.CTkLabel(
            self.frame,
            text="",
            font=ctk.CTkFont(size=13),
            text_color="#10b981",
            wraplength=800,
        )
        self.label_totales.grid(row=4, column=0, sticky="ew", padx=20, pady=(0, 20))

        return self.frame

    def _calcular_nomina(self):
        """Calcula la nómina para el período especificado."""
        try:
            # Validar y parsear fechas
            fecha_inicio_str = self.entrada_fecha_inicio.get().strip()
            fecha_cierre_str = self.entrada_fecha_cierre.get().strip()
            dias_laborados_str = self.entrada_dias_laborados.get().strip()
            horas_extras_str = self.entrada_horas_extras.get().strip()

            if not fecha_inicio_str or not fecha_cierre_str:
                messagebox.showerror("Error", "Las fechas son obligatorias (formato DD/MM/YYYY).")
                return

            try:
                fecha_inicio = datetime.strptime(fecha_inicio_str, FORMATO_FECHA).date()
                fecha_cierre = datetime.strptime(fecha_cierre_str, FORMATO_FECHA).date()
            except ValueError:
                messagebox.showerror("Error", "Formato de fecha inválido. Usa DD/MM/YYYY.")
                return

            if not dias_laborados_str or not horas_extras_str:
                messagebox.showerror("Error", "Días laborados y horas extras son obligatorios.")
                return

            try:
                dias_laborados = int(dias_laborados_str)
                horas_extras = int(horas_extras_str)
            except ValueError:
                messagebox.showerror("Error", "Días y horas extras deben ser números enteros.")
                return

            # Llamar al controlador para liquidar
            resultado = self.controller.liquidar_nomina_periodo(
                fecha_inicio, fecha_cierre, dias_laborados, horas_extras
            )

            if not resultado["success"]:
                messagebox.showerror("Error", resultado["error"])
                return

            # Mostrar resultados
            self._mostrar_resultados(resultado)
            self.ultimo_resultado = resultado

        except Exception as e:
            messagebox.showerror("Error", f"Error al calcular nómina: {str(e)}")

    def _mostrar_resultados(self, resultado: dict):
        """Muestra los resultados de la liquidación."""
        # Limpiar scroll
        for widget in self.scroll_resultados.winfo_children():
            widget.destroy()

        registros = resultado["registros"]

        if not registros:
            label = ctk.CTkLabel(
                self.scroll_resultados,
                text="No hay registros para mostrar",
                font=ctk.CTkFont(size=14),
                text_color="#9ca3af",
            )
            label.grid(row=0, column=0, pady=30)
            return

        # Encabezados de tabla
        headers = [
            "Nº",
            "Nombre",
            "Cargo",
            "Ordinario",
            "Aux Transp",
            "Total Dev",
            "AFP",
            "EPS",
            "Total Ded",
            "Salario Neto",
        ]

        header_frame = ctk.CTkFrame(self.scroll_resultados, fg_color="#111827", corner_radius=12)
        header_frame.grid(row=0, column=0, sticky="ew", padx=8, pady=(8, 4))
        header_frame.grid_columnconfigure(tuple(range(len(headers))), weight=1)

        for col_idx, header in enumerate(headers):
            lbl = ctk.CTkLabel(
                header_frame,
                text=header,
                font=ctk.CTkFont(size=11, weight="bold"),
                anchor="w",
            )
            lbl.grid(row=0, column=col_idx, padx=8, pady=10, sticky="w")

        # Filas de datos
        for row_idx, registro in enumerate(registros, start=1):
            row_frame = ctk.CTkFrame(self.scroll_resultados, fg_color="#1f2937", corner_radius=12)
            row_frame.grid(row=row_idx, column=0, sticky="ew", padx=8, pady=4)
            row_frame.grid_columnconfigure(tuple(range(len(headers))), weight=1)

            # Obtener datos del empleado
            empleado = self.controller.buscar_empleado(registro["empleado_id"])
            nombre_completo = f"{empleado.nombre} {empleado.apellido}" if empleado else "N/A"

            datos = [
                str(row_idx),
                nombre_completo,
                empleado.cargo if empleado else "N/A",
                f"${registro['salario_base_periodo']:,.2f}",
                f"${registro['auxilio_transporte_periodo']:,.2f}",
                f"${registro['total_devengado']:,.2f}",
                f"${registro['descuento_afp']:,.2f}",
                f"${registro['descuento_eps']:,.2f}",
                f"${registro['total_deducciones']:,.2f}",
                f"${registro['salario_neto']:,.2f}",
            ]

            for col_idx, dato in enumerate(datos):
                lbl = ctk.CTkLabel(
                    row_frame, text=dato, font=ctk.CTkFont(size=10), anchor="w"
                )
                lbl.grid(row=0, column=col_idx, padx=8, pady=8, sticky="w")

        # Mostrar totales
        totales_text = (
            f"📊 TOTALES: {resultado['cantidad_empleados']} empleados | "
            f"Total Devengado: ${resultado['total_devengado']:,.2f} | "
            f"Total Deducciones: ${resultado['total_deducciones']:,.2f} | "
            f"Nómina Neta: ${resultado['total_neto']:,.2f}"
        )
        self.label_totales.configure(text=totales_text)

    def _exportar_excel(self):
        """Exporta la nómina a Excel."""
        try:
            # Verificar si hay resultado calculado
            if not self.ultimo_resultado:
                messagebox.showwarning(
                    "Sin datos",
                    "No hay resultados de cálculo. Calcula la nómina primero.",
                )
                return

            # Obtener fechas del resultado
            fecha_inicio_str = self.entrada_fecha_inicio.get().strip()
            fecha_cierre_str = self.entrada_fecha_cierre.get().strip()

            try:
                fecha_inicio = datetime.strptime(fecha_inicio_str, FORMATO_FECHA).date()
                fecha_cierre = datetime.strptime(fecha_cierre_str, FORMATO_FECHA).date()
            except ValueError:
                messagebox.showerror("Error", "Formato de fecha inválido.")
                return

            # Obtener registros del repositorio
            registros = self.controller.repo_nomina.obtener_por_periodo(
                fecha_inicio, fecha_cierre
            )

            if not registros:
                messagebox.showwarning(
                    "Sin datos",
                    "No hay registros para el período especificado.",
                )
                return

            # Solicitar ubicación para guardar
            ruta_archivo = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Archivos Excel", "*.xlsx")],
                initialfile=f"nomina_{fecha_inicio.strftime('%Y%m%d')}_"
                f"{fecha_cierre.strftime('%Y%m%d')}.xlsx",
            )

            if not ruta_archivo:
                return  # Usuario canceló

            # Exportar usando el servicio
            exportar_nomina_a_excel(registros, fecha_inicio, fecha_cierre, ruta_archivo)

            messagebox.showinfo(
                "Éxito",
                f"Archivo exportado exitosamente:\n{ruta_archivo}",
            )

        except ImportError:
            messagebox.showerror(
                "Error",
                "openpyxl no está instalado. Ejecuta: pip install openpyxl",
            )
        except Exception as e:
            messagebox.showerror("Error", f"Error al exportar: {str(e)}")
