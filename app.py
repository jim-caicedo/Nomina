from controllers.main_controller import MainController
import sys


def main():
    # Verificar que `customtkinter` esté disponible en el intérprete actual
    try:
        import customtkinter  # noqa: F401
    except ModuleNotFoundError:
        print("Error: el paquete 'customtkinter' no está instalado en este intérprete de Python.")
        print("Soluciones:")
        print(" 1) Ejecutar la aplicación con el Python del entorno virtual del proyecto:\n    ./.venv/bin/python app.py")
        print(" 2) Activar el virtualenv y ejecutar:\n    source .venv/bin/activate\n    python app.py")
        print(" 3) Instalar 'customtkinter' en este intérprete:\n    python -m pip install --user customtkinter")
        sys.exit(1)

    # Importar la vista después de asegurar la dependencia (evita traceback crípticos)
    from views.main_view import MainView

    controller = MainController()
    view = MainView(controller)
    view.run()


if __name__ == "__main__":
    main()
