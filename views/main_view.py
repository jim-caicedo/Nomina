import customtkinter as ctk
from tkinter import StringVar
from controllers.main_controller import MainController
from controllers.empleado_controller import EmpleadoController
from controllers.nomina_controller import NominaController
from controllers.concepto_controller import ConceptoController
from controllers.dashboard_controller import DashboardController
from controllers.historial_controller import HistorialController
from controllers.configuracion_controller import ConfiguracionController
from views.crud_empleado_view import CrudEmpleadoView
from views.liquidar_nomina_view import LiquidarNominaView
from views.configuracion_view import ConfiguracionView
from views.gestion_conceptos_view import GestionConceptosView
from views.historial_nomina_view import HistorialNominaView


class MainView:
    def __init__(self, controller: MainController):
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")

        self.controller = controller
        self.root = ctk.CTk()
        self.root.title("Gestión de Nómina")
        self.root.geometry("1024x680")
        self.root.minsize(940, 640)

        self.sidebar = None
        self.content_frame = None
        self.frames = {}
        self._frame_factories = {}  # Diccionario de fábricas para lazy loading
        self.empleado_seleccionado = StringVar()
        self.horas_extra_var = StringVar(value="0")

        # Inicializar controladores especializados
        self.empleado_controller = EmpleadoController()
        self.nomina_controller = NominaController()
        self.concepto_controller = ConceptoController()
        self.dashboard_controller = DashboardController()
        self.historial_controller = HistorialController()
        self.config_controller = ConfiguracionController()

        self._build_ui()

    def _build_ui(self):
        # Configuración responsive del root
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)

        # Sidebar (scrollable) fija a la izquierda
        # Usamos CTkScrollableFrame para permitir scroll si la ventana es pequeña
        try:
            self.sidebar = ctk.CTkScrollableFrame(self.root, width=240, corner_radius=0)
        except Exception:
            # Fallback: si la versión de customtkinter no tiene CTkScrollableFrame, usar CTkFrame
            self.sidebar = ctk.CTkFrame(self.root, width=240, corner_radius=0)

        self.sidebar.grid(row=0, column=0, sticky="nsw")
        # Dejar que el contenido pueda expandirse y en versiones con scroll
        self.sidebar.grid_rowconfigure(0, weight=1)
        ##self.sidebar.grid_propagate(False)  # Mantiene ancho fijo

        title = ctk.CTkLabel(
            self.sidebar,
            text="Nómina Pro",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title.grid(row=0, column=0, padx=20, pady=(24, 8), sticky="w")

        subtitle = ctk.CTkLabel(
            self.sidebar,
            text="Gestión moderna",
            font=ctk.CTkFont(size=13)
        )
        subtitle.grid(row=1, column=0, padx=20, pady=(0, 24), sticky="w")

        # Botones del sidebar
        btn_dashboard = ctk.CTkButton(
            self.sidebar,
            text="Dashboard",
            command=lambda: self._show_frame("dashboard"),
            anchor="w"
        )
        btn_dashboard.grid(row=2, column=0, padx=20, pady=8, sticky="ew")

        btn_empleados = ctk.CTkButton(
            self.sidebar,
            text="Empleados",
            command=lambda: self._show_frame("empleados"),
            anchor="w"
        )
        btn_empleados.grid(row=3, column=0, padx=20, pady=8, sticky="ew")

        btn_crud = ctk.CTkButton(
            self.sidebar,
            text="Gestionar Empleados",
            command=lambda: self._show_frame("crud"),
            anchor="w"
        )
        btn_crud.grid(row=4, column=0, padx=20, pady=8, sticky="ew")

        btn_liquidar_nomina = ctk.CTkButton(
            self.sidebar,
            text="Liquidar Nómina",
            command=lambda: self._show_frame("liquidar_nomina"),
            anchor="w"
        )
        btn_liquidar_nomina.grid(row=5, column=0, padx=20, pady=8, sticky="ew")

        btn_historial = ctk.CTkButton(
            self.sidebar,
            text="📋 Historial de Nóminas",
            command=lambda: self._show_frame("historial_nomina"),
            anchor="w"
        )
        btn_historial.grid(row=6, column=0, padx=20, pady=8, sticky="ew")

        btn_configuracion = ctk.CTkButton(
            self.sidebar,
            text="⚙️ Configuración Legal",
            command=lambda: self._show_frame("configuracion"),
            anchor="w"
        )
        btn_configuracion.grid(row=7, column=0, padx=20, pady=8, sticky="ew")

        btn_conceptos = ctk.CTkButton(
            self.sidebar,
            text="📋 Conceptos de Nómina",
            command=lambda: self._show_frame("conceptos"),
            anchor="w"
        )
        btn_conceptos.grid(row=8, column=0, padx=20, pady=8, sticky="ew")

        # Content frame que ocupa TODO el espacio restante
        self.content_frame = ctk.CTkFrame(self.root)
        self.content_frame.grid(row=0, column=1, sticky="nsew", padx=(10, 20), pady=20)
        self.content_frame.grid_rowconfigure(0, weight=1)
        self.content_frame.grid_columnconfigure(0, weight=1)

        # ============================================================
        # LAZY LOADING - Registrar fábricas (NO crear vistas aún)
        # ============================================================
        self._frame_factories = {
            "dashboard": self._create_dashboard_frame,
            "empleados": self._create_empleados_frame,
            "crud": self._create_crud_frame,
            "liquidar_nomina": self._create_liquidar_nomina_frame,
            "historial_nomina": self._create_historial_nomina_frame,
            "configuracion": self._create_configuracion_frame,
            "conceptos": self._create_gestion_conceptos_frame,
            "liquidar": self._create_liquidar_frame,
        }

        # Precargar solo dashboard para inicio rápido
        self.frames["dashboard"] = self._create_dashboard_frame()

        # Mostrar dashboard inicial
        self._show_frame("dashboard")

    # ============================================================
    # DASHBOARD - Layout Responsive con Calendario de Pagos
    # ============================================================
    def _create_dashboard_frame(self):
        frame = ctk.CTkFrame(self.content_frame, corner_radius=20)
        frame.grid(row=0, column=0, sticky="nsew")
        frame.grid_rowconfigure(2, weight=1)
        frame.grid_columnconfigure(0, weight=1)

        header = ctk.CTkLabel(
            frame,
            text="Dashboard",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        header.grid(row=0, column=0, sticky="w", padx=20, pady=(20, 10))

        # Cards container
        cards_frame = ctk.CTkFrame(frame, fg_color="#1f2937", corner_radius=16)
        cards_frame.grid(row=1, column=0, sticky="new", padx=20, pady=(0, 20))
        cards_frame.grid_columnconfigure((0, 1, 2), weight=1, uniform="cards")

        resumen = self.dashboard_controller.generar_resumen_dashboard()

        card1 = self._create_stat_card(
            cards_frame,
            "Empleados activos",
            str(resumen["empleados_activos"])
        )
        card1.grid(row=0, column=0, padx=10, pady=20, sticky="nsew")

        card2 = self._create_stat_card(
            cards_frame,
            "Gasto total mensual",
            f"${resumen['gasto_total_mensual']:,.2f}"
        )
        card2.grid(row=0, column=1, padx=10, pady=20, sticky="nsew")

        card3 = self._create_stat_card(
            cards_frame,
            "Salario promedio",
            f"${resumen['salario_promedio']:,.2f}"
        )
        card3.grid(row=0, column=2, padx=10, pady=20, sticky="nsew")

        # ====== CALENDARIO DE PAGOS ======
        calendar_container = ctk.CTkFrame(frame, fg_color="#1f2937", corner_radius=16)
        calendar_container.grid(row=2, column=0, sticky="nsew", padx=20, pady=(0, 20))
        calendar_container.grid_rowconfigure(2, weight=1)
        calendar_container.grid_columnconfigure(0, weight=1)

        # Título del calendario
        calendar_title = ctk.CTkLabel(
            calendar_container,
            text="📅 Calendario de Pagos",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        calendar_title.grid(row=0, column=0, padx=20, pady=(16, 8), sticky="w")

        # Leyenda
        legend_frame = ctk.CTkFrame(calendar_container, fg_color="transparent")
        legend_frame.grid(row=1, column=0, padx=20, pady=(0, 8), sticky="w")

        pay_indicator = ctk.CTkFrame(legend_frame, width=14, height=14, fg_color="#10b981", corner_radius=7)
        pay_indicator.grid(row=0, column=0)
        pay_label = ctk.CTkLabel(legend_frame, text="Día de pago (15 y 30)", font=ctk.CTkFont(size=11))
        pay_label.grid(row=0, column=1, padx=(6, 16))

        today_indicator = ctk.CTkFrame(legend_frame, width=14, height=14, fg_color="#f59e0b", corner_radius=7)
        today_indicator.grid(row=0, column=2)
        today_label = ctk.CTkLabel(legend_frame, text="Hoy", font=ctk.CTkFont(size=11))
        today_label.grid(row=0, column=3, padx=(6, 0))

        # ====== CREAR payday_info_label ANTES del calendario ======
        self.payday_info_label = ctk.CTkLabel(
            calendar_container,
            text="",
            font=ctk.CTkFont(size=13),
            text_color="#94a3b8"
        )
        self.payday_info_label.grid(row=3, column=0, padx=20, pady=(0, 16), sticky="w")

        # ====== AHORA sí crear el calendario ======
        self.calendar_widget = self._create_calendar_widget(calendar_container)
        self.calendar_widget.grid(row=2, column=0, padx=20, pady=(0, 12), sticky="nsew")

        return frame

    def _create_calendar_widget(self, parent):
        """Crea un widget de calendario que marca los días 15 y 30 como días de pago."""
        import calendar
        from datetime import datetime

        container = ctk.CTkFrame(parent, fg_color="#0f172a", corner_radius=12)
        container.grid_rowconfigure(2, weight=1)
        container.grid_columnconfigure(0, weight=1)

        now = datetime.now()
        self._cal_year = now.year
        self._cal_month = now.month

        # Header con navegación
        header_frame = ctk.CTkFrame(container, fg_color="transparent")
        header_frame.grid(row=0, column=0, padx=12, pady=(12, 8), sticky="ew")
        header_frame.grid_columnconfigure(1, weight=1)

        month_names = [
            "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
            "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
        ]

        prev_btn = ctk.CTkButton(
            header_frame,
            text="◀",
            width=30,
            command=self._prev_month
        )
        prev_btn.grid(row=0, column=0, padx=(0, 8))

        self._month_year_label = ctk.CTkLabel(
            header_frame,
            text=f"{month_names[self._cal_month - 1]} {self._cal_year}",
            font=ctk.CTkFont(size=15, weight="bold")
        )
        self._month_year_label.grid(row=0, column=1)

        next_btn = ctk.CTkButton(
            header_frame,
            text="▶",
            width=30,
            command=self._next_month
        )
        next_btn.grid(row=0, column=2, padx=(8, 0))

        # Días de la semana
        weekdays_frame = ctk.CTkFrame(container, fg_color="transparent")
        weekdays_frame.grid(row=1, column=0, padx=12, pady=(0, 4), sticky="ew")
        for i, day in enumerate(["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"]):
            weekdays_frame.grid_columnconfigure(i, weight=1)
            ctk.CTkLabel(
                weekdays_frame,
                text=day,
                font=ctk.CTkFont(size=11, weight="bold"),
                text_color="#64748b",
                width=36
            ).grid(row=0, column=i, padx=2)

        # Grid de días
        self._days_grid = ctk.CTkFrame(container, fg_color="transparent")
        self._days_grid.grid(row=2, column=0, padx=12, pady=(0, 12), sticky="nsew")

        self._render_calendar_days()

        return container

    def _prev_month(self):
        """Navega al mes anterior."""
        self._cal_month -= 1
        if self._cal_month < 1:
            self._cal_month = 12
            self._cal_year -= 1
        self._render_calendar_days()

    def _next_month(self):
        """Navega al mes siguiente."""
        self._cal_month += 1
        if self._cal_month > 12:
            self._cal_month = 1
            self._cal_year += 1
        self._render_calendar_days()

    def _render_calendar_days(self):
        """Renderiza los días del calendario resaltando los días de pago."""
        import calendar
        from datetime import datetime

        # Limpiar grid anterior
        for widget in self._days_grid.winfo_children():
            widget.destroy()

        year, month = self._cal_year, self._cal_month
        today = datetime.now()

        # Calcular días del mes
        cal = calendar.Calendar(firstweekday=calendar.MONDAY)
        month_weeks = cal.monthdayscalendar(year, month)
        days_in_month = calendar.monthrange(year, month)[1]

        # Días de pago: 15 y el día 30 (o último día si el mes tiene menos de 30)
        paydays = {15}
        if days_in_month >= 30:
            paydays.add(30)
        else:
            paydays.add(days_in_month)

        # Renderizar semanas
        for week_idx, week in enumerate(month_weeks):
            for day_idx, day in enumerate(week):
                self._days_grid.grid_columnconfigure(day_idx, weight=1)

                if day == 0:
                    # Celda vacía
                    empty = ctk.CTkFrame(self._days_grid, fg_color="transparent", width=36, height=36)
                    empty.grid(row=week_idx, column=day_idx, padx=2, pady=2)
                    continue

                is_payday = day in paydays
                is_today = (year == today.year and month == today.month and day == today.day)

                # Determinar colores
                if is_payday and is_today:
                    fg_color = "#10b981"      # Verde (pago)
                    border_color = "#f59e0b"  # Borde naranja (hoy)
                    text_color = "#ffffff"
                elif is_payday:
                    fg_color = "#10b981"      # Verde
                    border_color = "#059669"
                    text_color = "#ffffff"
                elif is_today:
                    fg_color = "#f59e0b"      # Naranja
                    border_color = "#d97706"
                    text_color = "#ffffff"
                else:
                    fg_color = "#1e293b"
                    border_color = "#334155"
                    text_color = "#e2e8f0"

                day_cell = ctk.CTkFrame(
                    self._days_grid,
                    fg_color=fg_color,
                    border_color=border_color,
                    border_width=2 if (is_payday or is_today) else 1,
                    corner_radius=10,
                    width=36,
                    height=36
                )
                day_cell.grid(row=week_idx, column=day_idx, padx=2, pady=2, sticky="nsew")
                day_cell.grid_propagate(False)

                # Label del día
                day_label = ctk.CTkLabel(
                    day_cell,
                    text=str(day),
                    font=ctk.CTkFont(size=13, weight="bold" if (is_payday or is_today) else "normal"),
                    text_color=text_color
                )
                day_label.place(relx=0.5, rely=0.5, anchor="center")

                # Tooltip para días de pago
                if is_payday:
                    day_cell.bind("<Enter>", lambda e, d=day: self._show_payday_tooltip(e, d))
                    day_cell.bind("<Leave>", lambda e: self._hide_payday_tooltip(e))

        # Actualizar label del mes
        month_names = [
            "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
            "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
        ]
        self._month_year_label.configure(text=f"{month_names[month - 1]} {year}")

        # Actualizar info del próximo pago
        self._update_next_payday_info(year, month, paydays, today)

    def _show_payday_tooltip(self, event, day):
        """Muestra un tooltip indicando que es día de pago."""
        widget = event.widget.master if hasattr(event.widget, 'master') else event.widget
        if not hasattr(self, '_tooltip'):
            self._tooltip = ctk.CTkToplevel(self.root)
            self._tooltip.overrideredirect(True)
            self._tooltip.attributes('-topmost', True)
            self._tooltip.configure(fg_color="#0f172a")
            label = ctk.CTkLabel(
                self._tooltip,
                text=f"💰 Día de pago de nómina",
                font=ctk.CTkFont(size=11),
                text_color="#10b981",
                fg_color="#0f172a",
                corner_radius=6
            )
            label.pack(padx=10, pady=6)
        x = widget.winfo_rootx() + widget.winfo_width() // 2 - 60
        y = widget.winfo_rooty() - 35
        self._tooltip.geometry(f"+{x}+{y}")
        self._tooltip.deiconify()

    def _hide_payday_tooltip(self, event):
        """Oculta el tooltip."""
        if hasattr(self, '_tooltip'):
            self._tooltip.withdraw()

    def _update_next_payday_info(self, year, month, paydays, today):
        """Actualiza el label con información del próximo día de pago."""
        from datetime import datetime
        import calendar

        # Encontrar próximo día de pago
        next_pay = None
        current_month_paydays = sorted(paydays)

        for pd in current_month_paydays:
            pd_date = datetime(year, month, pd)
            if pd_date.date() >= today.date() and not next_pay:
                next_pay = pd_date

        # Si no hay más pagos este mes, ir al siguiente
        if not next_pay:
            next_m = month + 1
            next_y = year
            if next_m > 12:
                next_m = 1
                next_y += 1
            next_days = calendar.monthrange(next_y, next_m)[1]
            next_paydays = {15, 30 if next_days >= 30 else next_days}
            next_pay = datetime(next_y, next_m, min(next_paydays))

        diff_days = (next_pay.date() - today.date()).days
        diff_text = f"en {diff_days} días" if diff_days > 0 else "hoy" if diff_days == 0 else "pasado"

        self.payday_info_label.configure(
            text=f"💰 Próximo pago: {next_pay.day} de "
                 f"{['Enero','Febrero','Marzo','Abril','Mayo','Junio','Julio','Agosto','Septiembre','Octubre','Noviembre','Diciembre'][next_pay.month-1]} "
                 f"de {next_pay.year} ({diff_text})"
        )

    def _create_stat_card(self, parent, title: str, value: str):
        card = ctk.CTkFrame(parent, corner_radius=16)
        card.grid_rowconfigure(1, weight=1)
        card.grid_columnconfigure(0, weight=1)

        label_title = ctk.CTkLabel(
            card,
            text=title,
            font=ctk.CTkFont(size=14)
        )
        label_title.grid(row=0, column=0, padx=16, pady=(16, 6), sticky="w")

        label_value = ctk.CTkLabel(
            card,
            text=value,
            font=ctk.CTkFont(size=22, weight="bold")
        )
        label_value.grid(row=1, column=0, padx=16, pady=(0, 16), sticky="w")

        return card

    # ============================================================
    # EMPLEADOS - Layout Responsive
    # ============================================================
    def _create_empleados_frame(self):
        frame = ctk.CTkFrame(self.content_frame, corner_radius=20)
        frame.grid(row=0, column=0, sticky="nsew")
        frame.grid_rowconfigure(1, weight=1)
        frame.grid_columnconfigure(0, weight=1)

        title = ctk.CTkLabel(
            frame,
            text="Empleados",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="w")

        # Contenedor de la tabla
        table_frame = ctk.CTkFrame(frame, fg_color="#1f2937", corner_radius=16)
        table_frame.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="nsew")
        table_frame.grid_rowconfigure(1, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)

        # Header de la tabla
        headers = ["Nombre", "Cargo", "Salario"]
        header_container = ctk.CTkFrame(
            table_frame,
            fg_color="#111827",
            corner_radius=12
        )
        header_container.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 0))
        header_container.grid_columnconfigure((0, 1, 2), weight=1)

        for index, label in enumerate(headers):
            ctk.CTkLabel(
                header_container,
                text=label,
                font=ctk.CTkFont(size=13, weight="bold"),
                anchor="w"
            ).grid(row=0, column=index, padx=12, pady=12, sticky="ew")

        # ScrollableFrame
        scroll = ctk.CTkScrollableFrame(
            table_frame,
            corner_radius=16,
            fg_color="#111827"
        )
        scroll.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        scroll.grid_columnconfigure(0, weight=1)

        empleados = self.empleado_controller.obtener_empleados()
        for index, empleado in enumerate(empleados):
            row_frame = ctk.CTkFrame(
                scroll,
                fg_color="#1f2937",
                corner_radius=12
            )
            row_frame.grid(row=index, column=0, padx=8, pady=6, sticky="ew")
            row_frame.grid_columnconfigure((0, 1, 2), weight=1)

            ctk.CTkLabel(
                row_frame,
                text=empleado["nombre"],
                anchor="w"
            ).grid(row=0, column=0, padx=12, pady=12, sticky="ew")

            ctk.CTkLabel(
                row_frame,
                text=empleado["cargo"],
                anchor="w"
            ).grid(row=0, column=1, padx=12, pady=12, sticky="ew")

            ctk.CTkLabel(
                row_frame,
                text=f"${empleado['salario']:,.2f}",
                anchor="e"
            ).grid(row=0, column=2, padx=12, pady=12, sticky="ew")

        return frame

    # ============================================================
    # CRUD EMPLEADOS
    # ============================================================
    def _create_crud_frame(self):
        """Crea el frame del CRUD de empleados."""
        crud_view = CrudEmpleadoView(
            self.content_frame,
            self.empleado_controller,
            self.config_controller,
        )
        return crud_view.crear_frame()

    # ============================================================
    # LIQUIDAR NÓMINA
    # ============================================================
    def _create_liquidar_nomina_frame(self):
        """Crea el frame de liquidación de nómina quincenal."""
        liquidar_view = LiquidarNominaView(
            self.content_frame,
            self.nomina_controller,
            self.empleado_controller,
        )
        return liquidar_view.crear_frame()

    def _create_historial_nomina_frame(self):
        historial_view = HistorialNominaView(self.content_frame, self.historial_controller)
        return historial_view.crear_frame()

    # ============================================================
    # CONFIGURACIÓN
    # ============================================================
    def _create_configuracion_frame(self):
        """Crea el frame de configuración legal de nómina."""
        configuracion_view = ConfiguracionView(
            self.content_frame,
            self.config_controller
        )
        return configuracion_view.crear_frame()

    def _create_gestion_conceptos_frame(self):
        gestion_view = GestionConceptosView(self.content_frame, self.concepto_controller)
        return gestion_view.crear_frame()

    # ============================================================
    # LIQUIDAR (Old)
    # ============================================================
    def _create_liquidar_frame(self):
        frame = ctk.CTkFrame(self.content_frame, corner_radius=20)
        frame.grid(row=0, column=0, sticky="nsew")
        frame.grid_rowconfigure(1, weight=1)
        frame.grid_columnconfigure(0, weight=1)

        title = ctk.CTkLabel(
            frame,
            text="Liquidar Nómina",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="w")

        # Form frame
        form_frame = ctk.CTkFrame(frame, fg_color="#1f2937", corner_radius=16)
        form_frame.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="new")
        form_frame.grid_columnconfigure(1, weight=1)

        empleado_options = [
            f"{e['id']} - {e['nombre']}"
            for e in self.empleado_controller.obtener_empleados()
        ]
        if empleado_options:
            self.empleado_seleccionado.set(empleado_options[0])

        ctk.CTkLabel(
            form_frame,
            text="Selecciona un empleado:",
            font=ctk.CTkFont(size=14)
        ).grid(row=0, column=0, padx=16, pady=(16, 8), sticky="w")

        ctk.CTkOptionMenu(
            form_frame,
            values=empleado_options,
            variable=self.empleado_seleccionado,
            width=300
        ).grid(row=0, column=1, padx=16, pady=(16, 8), sticky="ew")

        ctk.CTkLabel(
            form_frame,
            text="Horas extra:",
            font=ctk.CTkFont(size=14)
        ).grid(row=1, column=0, padx=16, pady=8, sticky="w")

        ctk.CTkEntry(
            form_frame,
            textvariable=self.horas_extra_var,
            width=120
        ).grid(row=1, column=1, padx=16, pady=8, sticky="w")

        ctk.CTkButton(
            form_frame,
            text="Calcular",
            command=self._calcular_nomina
        ).grid(row=2, column=0, columnspan=2, padx=16, pady=12)

        # Resultado
        self.resultado_label = ctk.CTkLabel(
            form_frame,
            text="",
            wraplength=700,
            justify="left",
            font=ctk.CTkFont(size=13)
        )
        self.resultado_label.grid(
            row=3,
            column=0,
            columnspan=2,
            padx=16,
            pady=(12, 16),
            sticky="nw"
        )

        return frame

    # ============================================================
    # NAVEGACIÓN CON LAZY LOADING
    # ============================================================
    def _show_frame(self, name: str):
        """Muestra un frame, creándolo bajo demanda si no existe."""
        # Crear vista bajo demanda si no existe (lazy loading)
        if name not in self.frames:
            if name in self._frame_factories:
                # Crear la vista solo cuando se necesite
                self.frames[name] = self._frame_factories[name]()

        # Ocultar todas las vistas existentes
        for key, frame in self.frames.items():
            frame.grid_remove()

        # Mostrar la vista solicitada
        if name in self.frames:
            self.frames[name].grid(row=0, column=0, sticky="nsew")

    # ============================================================
    # CÁLCULO DE NÓMINA (Old)
    # ============================================================
    def _calcular_nomina(self):
        try:
            seleccionado = int(self.empleado_seleccionado.get().split(" - ")[0])
            horas_extra = float(self.horas_extra_var.get())
        except ValueError:
            self.resultado_label.configure(
                text="Ingrese valores válidos para el empleado y las horas extra."
            )
            return

        resultado = self.controller.liquidar_nomina(seleccionado, horas_extra)
        if "error" in resultado:
            self.resultado_label.configure(text=resultado["error"])
            return

        empleado = resultado["empleado"]
        nomina = resultado["nomina"]
        texto = (
            f"Liquidación para {empleado['nombre']} ({empleado['cargo']}):\n"
            f"Salario base: ${nomina['salario_base']:,.2f}\n"
            f"Horas extra: {horas_extra} -> ${nomina['total_extra']:,.2f}\n"
            f"Descuentos aproximados: ${nomina['descuentos']:,.2f}\n"
            f"Pago neto estimado: ${nomina['neto']:,.2f}"
        )
        self.resultado_label.configure(text=texto)

    # ============================================================
    # EJECUCIÓN
    # ============================================================
    def run(self):
        self.root.mainloop()