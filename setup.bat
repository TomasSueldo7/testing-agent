@echo off
chcp 65001 >nul
echo.
echo =====================================================
echo          Test Case Agent - Configuración Inicial
echo =====================================================
echo.

echo Verificando si Ollama está instalado...

ollama --version >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Ollama no está instalado en este equipo.
    echo.
    echo Por favor descarga e instala Ollama desde:
    echo https://ollama.com/download
    echo.
    pause
    exit /b
)

echo [OK] Ollama encontrado.
echo.

echo Descargando modelo qwen2:7b (puede tardar varios minutos la primera vez)...
echo.

ollama pull qwen2:7b

echo.
echo =====================================================
echo ¡Configuración completada correctamente!
echo.
echo Ahora puedes ejecutar el programa:
echo.
echo    TestCaseAgent.exe
echo.
echo (Se abrirá automáticamente en tu navegador)
echo =====================================================
echo.

pause