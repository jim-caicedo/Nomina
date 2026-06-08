import customtkinter as ctk
from tkinter import messagebox
from controllers.main_controller import MainController


class CrudEmpleadoView:
    def __init__(self, content_frame: ctk.CTkFrame, controller: MainController):
        self.content_frame = content_frame
        self.controller = controller
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
        self.entrada_numero_cuenta = None

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
        header = ctk.CTkLabel(
            self.frame, 
            text="Gestión de Empleados", 
            font=ctk.CTkFont(size=26, weight="bold")
        )
        header.grid(row=0, column=0, sticky="w", padx=20, pady=(20, 10))

        # ========== FORMULARIO ==========
        form_frame = ctk.CTkFrame(self.frame, fg_color="#1f2937", corner_radius=16)
        form_frame.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="ew")
        form_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)

        # Fila 1: Nombre y Apellido
        ctk.CTkLabel(form_frame, text="Nombre:", font=ctk.CTkFont(size=12, weight="bold")).grid(
            row=0, column=0, padx=12, pady=(16, 4), sticky="w"
        )
        self.entrada_nombre = ctk.CTkEntry(form_frame, placeholder_text="Ej: Juan", height=36)
        self.entrada_nombre.grid(row=1, column=0, padx=12, pady=(0, 12), sticky="ew")

        ctk.CTkLabel(form_frame, text="Apellido:", font=ctk.CTkFont(size=12, weight="bold")).grid(
            row=0, column=1, padx=12, pady=(16, 4), sticky="w"
        )
        self.entrada_apellido = ctk.CTkEntry(form_frame, placeholder_text="Ej: Pérez", height=36)
        self.entrada_apellido.grid(row=1, column=1, padx=12, pady=(0, 12), sticky="ew")

        ctk.CTkLabel(form_frame, text="Cargo:", font=ctk.CTkFont(size=12, weight="bold")).grid(
            row=0, column=2, padx=12, pady=(16, 4), sticky="w"
        )
        self.entrada_cargo = ctk.CTkEntry(form_frame, placeholder_text="Ej: Contador", height=36)
        self.entrada_cargo.grid(row=1, column=2, padx=12, pady=(0, 12), sticky="ew")

        ctk.CTkLabel(form_frame, text="Salario:", font=ctk.CTkFont(size=12, weight="bold")).grid(
            row=0, column=3, padx=12, pady=(16, 4), sticky="w"
        )
        self.entrada_salario = ctk.CTkEntry(form_frame, placeholder_text="Ej: 2500.00", height=36)
        self.entrada_salario.grid(row=1, column=3, padx=12, pady=(0, 12), sticky="ew")

        # Fila 2: Correo, Teléfono, Número de Cuenta
        ctk.CTkLabel(form_frame, text="Correo:", font=ctk.CTkFont(size=12, weight="bold")).grid(
            row=2, column=0, padx=12, pady=(0, 4), sticky="w"
        )
        self.entrada_correo = ctk.CTkEntry(form_frame, placeholder_text="Ej: juan@empresa.com", height=36)
        self.entrada_correo.grid(row=3, column=0, padx=12, pady=(0, 12), sticky="ew")

        ctk.CTkLabel(form_frame, text="Teléfono:", font=ctk.CTkFont(size=12, weight="bold")).grid(
            row=2, column=1, padx=12, pady=(0, 4), sticky="w"
        )
        self.entrada_telefono = ctk.CTkEntry(form_frame, placeholder_text="Ej: 3001234567", height=36)
        self.entrada_telefono.grid(row=3, column=1, padx=12, pady=(0, 12), sticky="ew")

        ctk.CTkLabel(form_frame, text="Nº Cuenta:", font=ctk.CTkFont(size=12, weight="bold")).grid(
            row=2, column=2, padx=12, pady=(0, 4), sticky="w"
        )
        self.entrada_numero_cuenta = ctk.CTkEntry(form_frame, placeholder_text="Ej: 001-2024-0001", height=36)
        self.entrada_numero_cuenta.grid(row=3, column=2, padx=12, pady=(0, 12), sticky="ew")

        # Fila 3: Botones
        botones_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        botones_frame.grid(row=4, column=0, columnspan=4, padx=12, pady=(0, 16), sticky="ew")
        botones_frame.grid_columnconfigure((0, 1, 2), weight=1)

        self.btn_crear = ctk.CTkButton(
            botones_frame, 
            text="Crear Empleado", 
            command=self._crear_empleado,
            height=36,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color="#10b981"
        )
        self.btn_crear.grid(row=0, column=0, padx=6, sticky="ew")

        self.btn_guardar = ctk.CTkButton(
            botones_frame, 
            text="Guardar Cambios", 
            command=self._guardar_cambios,
            height=36,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color="#3b82f6"
        )
        self.btn_guardar.grid(row=0, column=1, padx=6, sticky="ew")
        self.btn_guardar.grid_remove()

        self.btn_cancelar = ctk.CTkButton(
            botones_frame, 
            text="Cancelar", 
            command=self._cancelar_edicion,
            height=36,
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

        # Frame de contenedor de tabla
        tabla_container = ctk.CTkFrame(self.frame, fg_color="#1f2937", corner_radius=16)
        tabla_container.grid(row=3, column=0, padx=20, pady=(0, 20), sticky="nsew")
        tabla_container.grid_columnconfigure(0, weight=1)
        tabla_container.grid_rowconfigure(1, weight=1)

        # Scroll de tabla
        self.scroll_frame = ctk.CTkScrollableFrame(tabla_container, corner_radius=12, fg_color="#111827")
        self.scroll_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        self.scroll_frame.grid_columnconfigure(0, weight=1)

        self.frame.grid_rowconfigure(3, weight=1)

        self._actualizar_tabla()

        return self.frame

    def _actualizar_tabla(self):
        """Recarga la tabla con los datos actuales."""
        # Limpiar scroll
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
        row_frame.grid_columnconfigure((0, 1, 2, 3, 4, 5), weight=1)

        # Datos de empleado
        nombre_completo = f"{empleado['nombre']} {empleado['apellido']}"
        
        datos = [
            (nombre_completo, 0),
            (empleado['cargo'], 1),
            (f"${empleado['salario']:,.2f}", 2),
            (empleado['correo'], 3),
            (empleado['telefono'], 4),
        ]

        for texto, col in datos:
            lbl = ctk.CTkLabel(
                row_frame, 
                text=texto, 
                anchor="w",
                font=ctk.CTkFont(size=12)
            )
            lbl.grid(row=0, column=col, padx=10, pady=12, sticky="ew")

        # Botones de acción
        acciones_frame = ctk.CTkFrame(row_frame, fg_color="transparent")
        acciones_frame.grid(row=0, column=5, padx=10, pady=12, sticky="ew")
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
        cargo = self.entrada_cargo.get().strip()
        salario_str = self.entrada_salario.get().strip()
        correo = self.entrada_correo.get().strip()
        telefono = self.entrada_telefono.get().strip()
        numero_cuenta = self.entrada_numero_cuenta.get().strip()

        if not nombre or not apellido or not cargo or not salario_str:
            messagebox.showerror("Error", "Los campos Nombre, Apellido, Cargo y Salario son obligatorios.")
            return

        try:
            salario = float(salario_str)
        except ValueError:
            messagebox.showerror("Error", "El salario debe ser un número válido.")
            return

        resultado = self.controller.crear_empleado(
            nombre, apellido, cargo, salario, correo, telefono, numero_cuenta
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
        self.entrada_nombre.delete(0, "end")
        self.entrada_nombre.insert(0, empleado.nombre)
        self.entrada_apellido.delete(0, "end")
        self.entrada_apellido.insert(0, empleado.apellido)
        self.entrada_cargo.delete(0, "end")
        self.entrada_cargo.insert(0, empleado.cargo)
        self.entrada_salario.delete(0, "end")
        self.entrada_salario.insert(0, str(empleado.salario))
        self.entrada_correo.delete(0, "end")
        self.entrada_correo.insert(0, empleado.correo)
        self.entrada_telefono.delete(0, "end")
        self.entrada_telefono.insert(0, empleado.telefono)
        self.entrada_numero_cuenta.delete(0, "end")
        self.entrada_numero_cuenta.insert(0, empleado.numero_cuenta)

        self.en_edicion = True
        self.btn_crear.grid_remove()
        self.btn_guardar.grid()
        self.btn_cancelar.grid()

    def _guardar_cambios(self):
        """Guarda los cambios del empleado editado."""
        nombre = self.entrada_nombre.get().strip()
        apellido = self.entrada_apellido.get().strip()
        cargo = self.entrada_cargo.get().strip()
        salario_str = self.entrada_salario.get().strip()
        correo = self.entrada_correo.get().strip()
        telefono = self.entrada_telefono.get().strip()
        numero_cuenta = self.entrada_numero_cuenta.get().strip()

        if not nombre or not apellido or not cargo or not salario_str:
            messagebox.showerror("Error", "Los campos Nombre, Apellido, Cargo y Salario son obligatorios.")
            return

        try:
            salario = float(salario_str)
        except ValueError:
            messagebox.showerror("Error", "El salario debe ser un número válido.")
            return

        resultado = self.controller.actualizar_empleado(
            self.empleado_seleccionado_id, nombre, apellido, cargo, salario, correo, telefono, numero_cuenta
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
        self.entrada_nombre.delete(0, "end")
        self.entrada_apellido.delete(0, "end")
        self.entrada_cargo.delete(0, "end")
        self.entrada_salario.delete(0, "end")
        self.entrada_correo.delete(0, "end")
        self.entrada_telefono.delete(0, "end")
        self.entrada_numero_cuenta.delete(0, "end")
