import customtkinter as ctk
from tkinter import messagebox
from controllers.configuracion_controller import ConfiguracionController
from controllers.empleado_controller import EmpleadoController
from utils.ui_theme import COLORES


class CrudEmpleadoView:
    def __init__(
        self,
        content_frame: ctk.CTkFrame,
        controller: EmpleadoController,
        config_controller: ConfiguracionController | None = None,
    ):
        self.content_frame = content_frame
        self.controller = controller
        self.config_controller = config_controller
        self.frame = None
        self.scroll_frame = None
        self.empleado_seleccionado_id = None
        self.en_edicion = False

        # Campos del formulario
        self.entrada_nombre = None
        self.entrada_apellido = None
        self.entrada_cargo = None
        self.entrada_salario = None
        self.entrada_correo = None
        self.entrada_telefono = None
        self.entrada_eps = None
        self.entrada_afp = None
        self.entrada_numero_cuenta = None
        self.entrada_cedula = None
        self.entrada_codigo_banco = None
        self.entrada_tipo_cuenta = None
        self.entrada_tipo_documento = None
        self.checkbox_auxilio = None

        # Botones
        self.btn_crear = None
        self.btn_guardar = None
        self.btn_cancelar = None

    def crear_frame(self) -> ctk.CTkFrame:
        """Crea el frame principal del CRUD con layout responsive."""
        self.frame = ctk.CTkFrame(self.content_frame, corner_radius=20)
        self.frame.grid(row=0, column=0, sticky="nsew")
        self.frame.grid_rowconfigure(2, weight=1)
        self.frame.grid_columnconfigure(0, weight=1)

        # ========== ENCABEZADO ==========
        header_frame = ctk.CTkFrame(self.frame, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 10))
        header_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            header_frame,
            text="Gestión de Empleados",
            font=ctk.CTkFont(size=26, weight="bold")
        ).grid(row=0, column=0, sticky="w")

        ctk.CTkButton(
            header_frame,
            text="📥 Exportar lista",
            command=self._exportar_empleados,
            height=36,
            width=140,
            font=ctk.CTkFont(size=12),
            fg_color=COLORES["primary"],
        ).grid(row=0, column=1, sticky="e")

        # ========== FORMULARIO ==========
        # Usar CTkScrollableFrame para que el formulario sea scrolleable
        form_scroll = ctk.CTkScrollableFrame(
            self.frame, 
            fg_color="#1f2937", 
            corner_radius=16,
            scrollbar_button_color="#3b82f6",
            scrollbar_button_hover_color="#2563eb"
        )
        form_scroll.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="ew")
        form_scroll.grid_columnconfigure((0, 1, 2, 3), weight=1, uniform="cols")

        # --- Fila 1: Tipo Documento, Cédula, Nombre, Apellido ---
        ctk.CTkLabel(form_scroll, text="Tipo Documento:", font=ctk.CTkFont(size=12, weight="bold")).grid(
            row=0, column=0, padx=12, pady=(16, 4), sticky="w"
        )
        self.entrada_tipo_documento = ctk.CTkOptionMenu(
            form_scroll, 
            values=["CC - Cédula de Ciudadanía", "CE - Cédula de Extranjería", "PA - Pasaporte", "NIT"],
            height=36,
            font=ctk.CTkFont(size=12)
        )
        self.entrada_tipo_documento.set("CC - Cédula de Ciudadanía")
        self.entrada_tipo_documento.grid(row=1, column=0, padx=12, pady=(0, 12), sticky="ew")

        ctk.CTkLabel(form_scroll, text="Cédula:", font=ctk.CTkFont(size=12, weight="bold")).grid(
            row=0, column=1, padx=12, pady=(16, 4), sticky="w"
        )
        self.entrada_cedula = ctk.CTkEntry(form_scroll, placeholder_text="Ej: 1023456789", height=36)
        self.entrada_cedula.grid(row=1, column=1, padx=12, pady=(0, 12), sticky="ew")

        ctk.CTkLabel(form_scroll, text="Nombre:", font=ctk.CTkFont(size=12, weight="bold")).grid(
            row=0, column=2, padx=12, pady=(16, 4), sticky="w"
        )
        self.entrada_nombre = ctk.CTkEntry(form_scroll, placeholder_text="Ej: Juan", height=36)
        self.entrada_nombre.grid(row=1, column=2, padx=12, pady=(0, 12), sticky="ew")

        ctk.CTkLabel(form_scroll, text="Apellido:", font=ctk.CTkFont(size=12, weight="bold")).grid(
            row=0, column=3, padx=12, pady=(16, 4), sticky="w"
        )
        self.entrada_apellido = ctk.CTkEntry(form_scroll, placeholder_text="Ej: Pérez", height=36)
        self.entrada_apellido.grid(row=1, column=3, padx=12, pady=(0, 12), sticky="ew")

        # --- Fila 2: Cargo, Salario, Correo, Teléfono ---
        ctk.CTkLabel(form_scroll, text="Cargo:", font=ctk.CTkFont(size=12, weight="bold")).grid(
            row=2, column=0, padx=12, pady=(0, 4), sticky="w"
        )
        self.entrada_cargo = ctk.CTkEntry(form_scroll, placeholder_text="Ej: Contador", height=36)
        self.entrada_cargo.grid(row=3, column=0, padx=12, pady=(0, 12), sticky="ew")

        ctk.CTkLabel(form_scroll, text="Salario:", font=ctk.CTkFont(size=12, weight="bold")).grid(
            row=2, column=1, padx=12, pady=(0, 4), sticky="w"
        )
        self.entrada_salario = ctk.CTkEntry(form_scroll, placeholder_text="Ej: 2500000", height=36)
        self.entrada_salario.grid(row=3, column=1, padx=12, pady=(0, 12), sticky="ew")

        ctk.CTkLabel(form_scroll, text="Correo:", font=ctk.CTkFont(size=12, weight="bold")).grid(
            row=2, column=2, padx=12, pady=(0, 4), sticky="w"
        )
        self.entrada_correo = ctk.CTkEntry(form_scroll, placeholder_text="Ej: juan@empresa.com", height=36)
        self.entrada_correo.grid(row=3, column=2, padx=12, pady=(0, 12), sticky="ew")

        ctk.CTkLabel(form_scroll, text="Teléfono:", font=ctk.CTkFont(size=12, weight="bold")).grid(
            row=2, column=3, padx=12, pady=(0, 4), sticky="w"
        )
        self.entrada_telefono = ctk.CTkEntry(form_scroll, placeholder_text="Ej: 3001234567", height=36)
        self.entrada_telefono.grid(row=3, column=3, padx=12, pady=(0, 12), sticky="ew")

        # --- Fila 3: EPS, AFP, Nº Cuenta, Código Banco ---
        ctk.CTkLabel(form_scroll, text="EPS:", font=ctk.CTkFont(size=12, weight="bold")).grid(
            row=4, column=0, padx=12, pady=(0, 4), sticky="w"
        )
        self.entrada_eps = ctk.CTkEntry(form_scroll, placeholder_text="Ej: Sura", height=36)
        self.entrada_eps.grid(row=5, column=0, padx=12, pady=(0, 12), sticky="ew")

        ctk.CTkLabel(form_scroll, text="AFP:", font=ctk.CTkFont(size=12, weight="bold")).grid(
            row=4, column=1, padx=12, pady=(0, 4), sticky="w"
        )
        self.entrada_afp = ctk.CTkEntry(form_scroll, placeholder_text="Ej: Colfondos", height=36)
        self.entrada_afp.grid(row=5, column=1, padx=12, pady=(0, 12), sticky="ew")

        ctk.CTkLabel(form_scroll, text="Nº Cuenta:", font=ctk.CTkFont(size=12, weight="bold")).grid(
            row=4, column=2, padx=12, pady=(0, 4), sticky="w"
        )
        self.entrada_numero_cuenta = ctk.CTkEntry(form_scroll, placeholder_text="Ej: 001-2024-0001", height=36)
        self.entrada_numero_cuenta.grid(row=5, column=2, padx=12, pady=(0, 12), sticky="ew")

        ctk.CTkLabel(form_scroll, text="Código Banco:", font=ctk.CTkFont(size=12, weight="bold")).grid(
            row=4, column=3, padx=12, pady=(0, 4), sticky="w"
        )
        self.entrada_codigo_banco = ctk.CTkEntry(form_scroll, placeholder_text="Ej: 007 (Bancolombia)", height=36)
        self.entrada_codigo_banco.grid(row=5, column=3, padx=12, pady=(0, 12), sticky="ew")

        # --- Fila 4: Tipo Cuenta, Checkbox Auxilio ---
        ctk.CTkLabel(form_scroll, text="Tipo Cuenta:", font=ctk.CTkFont(size=12, weight="bold")).grid(
            row=6, column=0, padx=12, pady=(0, 4), sticky="w"
        )
        self.entrada_tipo_cuenta = ctk.CTkOptionMenu(
            form_scroll, 
            values=["Ahorros", "Corriente", "Nómina"],
            height=36,
            font=ctk.CTkFont(size=12)
        )
        self.entrada_tipo_cuenta.set("Ahorros")
        self.entrada_tipo_cuenta.grid(row=7, column=0, padx=12, pady=(0, 12), sticky="ew")

        self.checkbox_auxilio = ctk.CTkCheckBox(
            form_scroll,
            text="Recibe Auxilio de Transporte",
            font=ctk.CTkFont(size=12),
            onvalue=True,
            offvalue=False
        )
        self.checkbox_auxilio.grid(row=7, column=1, columnspan=2, padx=12, pady=(0, 12), sticky="w")
        self.checkbox_auxilio.select()

        # Bind para actualizar checkbox cuando cambia el salario
        self.entrada_salario.bind("<KeyRelease>", self._on_salario_change)
        self.entrada_salario.bind("<FocusOut>", self._on_salario_change)

        # --- Fila 5: Botones ---
        botones_frame = ctk.CTkFrame(form_scroll, fg_color="transparent")
        botones_frame.grid(row=8, column=0, columnspan=4, padx=12, pady=(8, 16), sticky="ew")
        botones_frame.grid_columnconfigure((0, 1, 2), weight=1)

        self.btn_crear = ctk.CTkButton(
            botones_frame, 
            text="Crear Empleado", 
            command=self._crear_empleado,
            height=40,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color="#10b981"
        )
        self.btn_crear.grid(row=0, column=0, padx=6, sticky="ew")

        self.btn_guardar = ctk.CTkButton(
            botones_frame, 
            text="Guardar Cambios", 
            command=self._guardar_cambios,
            height=40,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color="#3b82f6"
        )
        self.btn_guardar.grid(row=0, column=1, padx=6, sticky="ew")
        self.btn_guardar.grid_remove()

        self.btn_cancelar = ctk.CTkButton(
            botones_frame, 
            text="Cancelar", 
            command=self._cancelar_edicion,
            height=40,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color="#6b7280"
        )
        self.btn_cancelar.grid(row=0, column=2, padx=6, sticky="ew")
        self.btn_cancelar.grid_remove()

        # ========== TABLA DE EMPLEADOS ==========
        tabla_header = ctk.CTkLabel(
            self.frame, 
            text="Lista de Empleados", 
            font=ctk.CTkFont(size=16, weight="bold")
        )
        tabla_header.grid(row=2, column=0, sticky="w", padx=20, pady=(0, 12))

        tabla_container = ctk.CTkFrame(self.frame, fg_color="#1f2937", corner_radius=16)
        tabla_container.grid(row=3, column=0, padx=20, pady=(0, 20), sticky="nsew")
        tabla_container.grid_columnconfigure(0, weight=1)
        tabla_container.grid_rowconfigure(1, weight=1)

        self.scroll_frame = ctk.CTkScrollableFrame(tabla_container, corner_radius=12, fg_color="#111827")
        self.scroll_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        self.scroll_frame.grid_columnconfigure(0, weight=1)

        self.frame.grid_rowconfigure(3, weight=1)

        self._actualizar_tabla()

        return self.frame

    def _actualizar_tabla(self):
        """Recarga la tabla con los datos actuales."""
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()

        empleados = self.controller.listar_empleados()

        if not empleados:
            empty_label = ctk.CTkLabel(
                self.scroll_frame, 
                text="No hay empleados registrados", 
                font=ctk.CTkFont(size=14),
                text_color="#9ca3af"
            )
            empty_label.grid(row=0, column=0, pady=20)
            return

        for index, empleado in enumerate(empleados):
            self._crear_fila_tabla(index, empleado)

    def _crear_fila_tabla(self, index: int, empleado: dict):
        """Crea una fila en la tabla."""
        row_frame = ctk.CTkFrame(self.scroll_frame, fg_color="#1f2937", corner_radius=12)
        row_frame.grid(row=index, column=0, padx=8, pady=8, sticky="ew")
        row_frame.grid_columnconfigure((0, 1, 2, 3, 4, 5, 6), weight=1)

        nombre_completo = f"{empleado['nombre']} {empleado['apellido']}"

        datos = [
            (nombre_completo, 0),
            (empleado.get('cedula', 'N/A'), 1),
            (empleado['cargo'], 2),
            (f"${empleado['salario']:,.2f}", 3),
            (empleado.get('tipo_cuenta', 'N/A'), 4),
            (empleado.get('codigo_banco', 'N/A'), 5),
        ]

        for texto, col in datos:
            lbl = ctk.CTkLabel(
                row_frame, 
                text=texto, 
                anchor="w",
                font=ctk.CTkFont(size=11)
            )
            lbl.grid(row=0, column=col, padx=8, pady=12, sticky="ew")

        acciones_frame = ctk.CTkFrame(row_frame, fg_color="transparent")
        acciones_frame.grid(row=0, column=6, padx=8, pady=12, sticky="ew")
        acciones_frame.grid_columnconfigure((0, 1), weight=1)

        btn_edit = ctk.CTkButton(
            acciones_frame,
            text="✎ Editar",
            width=70,
            height=28,
            font=ctk.CTkFont(size=11),
            command=lambda emp_id=empleado["id"]: self._cargar_para_edicion(emp_id),
            fg_color="#3b82f6",
            hover_color="#2563eb"
        )
        btn_edit.grid(row=0, column=0, padx=4, sticky="ew")

        btn_delete = ctk.CTkButton(
            acciones_frame,
            text="✕ Eliminar",
            width=70,
            height=28,
            font=ctk.CTkFont(size=11),
            command=lambda emp_id=empleado["id"]: self._eliminar_empleado(emp_id),
            fg_color="#ef4444",
            hover_color="#dc2626"
        )
        btn_delete.grid(row=0, column=1, padx=4, sticky="ew")

    def _crear_empleado(self):
        """Crea un nuevo empleado."""
        nombre = self.entrada_nombre.get().strip()
        apellido = self.entrada_apellido.get().strip()
        cedula = self.entrada_cedula.get().strip()
        cargo = self.entrada_cargo.get().strip()
        salario_str = self.entrada_salario.get().strip()
        correo = self.entrada_correo.get().strip()
        telefono = self.entrada_telefono.get().strip()
        numero_cuenta = self.entrada_numero_cuenta.get().strip()
        eps = self.entrada_eps.get().strip() if self.entrada_eps else ""
        afp = self.entrada_afp.get().strip() if self.entrada_afp else ""
        codigo_banco = self.entrada_codigo_banco.get().strip()
        tipo_cuenta = self.entrada_tipo_cuenta.get()
        tipo_documento = self.entrada_tipo_documento.get()
        recibe_auxilio = self.checkbox_auxilio.get()

        if not nombre or not apellido or not cedula or not cargo or not salario_str:
            messagebox.showerror("Error", "Los campos Nombre, Apellido, Cédula, Cargo y Salario son obligatorios.")
            return

        try:
            salario = float(salario_str)
        except ValueError:
            messagebox.showerror("Error", "El salario debe ser un número válido.")
            return

        resultado = self.controller.crear_empleado(
            nombre=nombre,
            apellido=apellido,
            cedula=cedula,
            cargo=cargo,
            salario=salario,
            correo=correo,
            telefono=telefono,
            numero_cuenta=numero_cuenta,
            eps=eps,
            afp=afp,
            sede_laboral="",
            recibe_auxilio=recibe_auxilio,
            codigo_banco=codigo_banco,
            tipo_cuenta=tipo_cuenta,
            tipo_documento=tipo_documento
        )
        if resultado["success"]:
            self._limpiar_formulario()
            self._actualizar_tabla()
            messagebox.showinfo("Éxito", f"Empleado {nombre} {apellido} creado correctamente.")
        else:
            messagebox.showerror("Error", resultado["error"])

    def _cargar_para_edicion(self, empleado_id: int):
        """Carga un empleado en el formulario para edición."""
        empleado = self.controller.buscar_empleado(empleado_id)
        if not empleado:
            messagebox.showerror("Error", "Empleado no encontrado.")
            return

        self.empleado_seleccionado_id = empleado_id

        # Cargar todos los campos
        self._set_entry(self.entrada_tipo_documento, empleado.get('tipo_documento', 'CC - Cédula de Ciudadanía'))
        self._set_entry(self.entrada_cedula, empleado.get('cedula', ''))
        self._set_entry(self.entrada_nombre, empleado.nombre)
        self._set_entry(self.entrada_apellido, empleado.apellido)
        self._set_entry(self.entrada_cargo, empleado.cargo)
        self._set_entry(self.entrada_salario, str(empleado.salario))
        self._set_entry(self.entrada_correo, empleado.correo)
        self._set_entry(self.entrada_telefono, empleado.telefono)
        self._set_entry(self.entrada_numero_cuenta, empleado.numero_cuenta)
        self._set_entry(self.entrada_eps, empleado.eps)
        self._set_entry(self.entrada_afp, empleado.afp)
        self._set_entry(self.entrada_codigo_banco, empleado.get('codigo_banco', ''))
        self._set_entry(self.entrada_tipo_cuenta, empleado.get('tipo_cuenta', 'Ahorros'))

        if empleado.recibe_auxilio_transporte:
            self.checkbox_auxilio.select()
        else:
            self.checkbox_auxilio.deselect()

        self.en_edicion = True
        self.btn_crear.grid_remove()
        self.btn_guardar.grid()
        self.btn_cancelar.grid()

    def _set_entry(self, widget, value):
        """Helper para setear valor en entry u optionmenu."""
        if isinstance(widget, ctk.CTkOptionMenu):
            widget.set(value)
        else:
            widget.delete(0, "end")
            widget.insert(0, value)

    def _guardar_cambios(self):
        """Guarda los cambios del empleado editado."""
        nombre = self.entrada_nombre.get().strip()
        apellido = self.entrada_apellido.get().strip()
        cedula = self.entrada_cedula.get().strip()
        cargo = self.entrada_cargo.get().strip()
        salario_str = self.entrada_salario.get().strip()
        correo = self.entrada_correo.get().strip()
        telefono = self.entrada_telefono.get().strip()
        numero_cuenta = self.entrada_numero_cuenta.get().strip()
        eps = self.entrada_eps.get().strip() if self.entrada_eps else ""
        afp = self.entrada_afp.get().strip() if self.entrada_afp else ""
        codigo_banco = self.entrada_codigo_banco.get().strip()
        tipo_cuenta = self.entrada_tipo_cuenta.get()
        tipo_documento = self.entrada_tipo_documento.get()
        recibe_auxilio = self.checkbox_auxilio.get()

        if not nombre or not apellido or not cedula or not cargo or not salario_str:
            messagebox.showerror("Error", "Los campos Nombre, Apellido, Cédula, Cargo y Salario son obligatorios.")
            return

        try:
            salario = float(salario_str)
        except ValueError:
            messagebox.showerror("Error", "El salario debe ser un número válido.")
            return

        resultado = self.controller.actualizar_empleado(
            empleado_id=self.empleado_seleccionado_id,
            nombre=nombre,
            apellido=apellido,
            cedula=cedula,
            cargo=cargo,
            salario=salario,
            correo=correo,
            telefono=telefono,
            numero_cuenta=numero_cuenta,
            eps=eps,
            afp=afp,
            sede_laboral="",
            recibe_auxilio=recibe_auxilio,
            codigo_banco=codigo_banco,
            tipo_cuenta=tipo_cuenta,
            tipo_documento=tipo_documento
        )
        if resultado["success"]:
            self._limpiar_formulario()
            self._cancelar_edicion()
            self._actualizar_tabla()
            messagebox.showinfo("Éxito", resultado["mensaje"])
        else:
            messagebox.showerror("Error", resultado["error"])

    def _cancelar_edicion(self):
        """Cancela la edición y vuelve al modo creación."""
        self.en_edicion = False
        self.empleado_seleccionado_id = None
        self._limpiar_formulario()
        self.btn_crear.grid()
        self.btn_guardar.grid_remove()
        self.btn_cancelar.grid_remove()

    def _eliminar_empleado(self, empleado_id: int):
        """Elimina un empleado con confirmación."""
        if messagebox.askyesno("Confirmar eliminación", "¿Estás seguro de que deseas eliminar este empleado?"):
            resultado = self.controller.eliminar_empleado(empleado_id)
            if resultado["success"]:
                self._actualizar_tabla()
                messagebox.showinfo("Éxito", resultado["mensaje"])
            else:
                messagebox.showerror("Error", resultado["error"])

    def _limpiar_formulario(self):
        """Limpia los campos del formulario."""
        campos = [
            self.entrada_nombre, self.entrada_apellido, self.entrada_cedula,
            self.entrada_cargo, self.entrada_salario, self.entrada_correo,
            self.entrada_telefono, self.entrada_numero_cuenta,
            self.entrada_eps, self.entrada_afp,
            self.entrada_codigo_banco
        ]
        for campo in campos:
            if campo:
                campo.delete(0, "end")

        self.entrada_tipo_documento.set("CC - Cédula de Ciudadanía")
        self.entrada_tipo_cuenta.set("Ahorros")
        self.checkbox_auxilio.select()

    def _exportar_empleados(self):
        from tkinter import filedialog
        from utils.excel_exporter import exportar_empleados_a_excel

        empleados = self.controller.listar_empleados()
        if not empleados:
            messagebox.showwarning("Sin datos", "No hay empleados para exportar.")
            return

        ruta = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Archivos Excel", "*.xlsx")],
            initialfile="empleados.xlsx",
        )
        if not ruta:
            return
        try:
            exportar_empleados_a_excel(empleados, ruta)
            messagebox.showinfo("Éxito", f"Lista exportada:\n{ruta}")
        except Exception as e:
            messagebox.showerror("Error", f"Error al exportar: {str(e)}")

    def _on_salario_change(self, event=None):
        """Actualiza el checkbox de auxilio cuando cambia el salario."""
        try:
            salario_str = self.entrada_salario.get().strip()
            if not salario_str:
                return

            if not self.config_controller:
                return

            salario = float(salario_str)
            config = self.config_controller.obtener_configuracion_obj()
            limite_smmlv = 2 * config.salario_minimo_mensual

            if salario <= limite_smmlv:
                self.checkbox_auxilio.select()
            else:
                self.checkbox_auxilio.deselect()
        except ValueError:
            pass