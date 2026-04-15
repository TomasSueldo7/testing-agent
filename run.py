import sys
import win32event
import win32api
import winerror
import webbrowser
import threading
from src.test_case_agent.app import app

# ==================== SINGLE INSTANCE CHECK ====================
MUTEX_NAME = "TestCaseAgent_SingleInstanceMutex"

def is_already_running():
    """Devuelve True si ya hay una instancia corriendo."""
    mutex = win32event.CreateMutex(None, False, MUTEX_NAME)
    last_error = win32api.GetLastError()
    
    if last_error == winerror.ERROR_ALREADY_EXISTS:
        # Ya existe otra instancia
        return True
    return False

if is_already_running():
    print("El programa ya está abierto.")
    webbrowser.open_new("http://127.0.0.1:3000")
    sys.exit(0)  # Salir sin abrir otra instancia

# ==================== ABRIR NAVEGADOR ====================
def open_browser():
    webbrowser.open_new("http://127.0.0.1:3000")

if __name__ == "__main__":
    # Abre el navegador automáticamente
    threading.Timer(1.5, open_browser).start()
    
    # Inicia la aplicación
    app.run(
        host="127.0.0.1",
        port=3000,
        debug=False
    )