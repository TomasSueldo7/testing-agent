import ollama
from .models import TestCaseResponse
from .prompts import SYSTEM_PROMPT
from dotenv import load_dotenv
import json
import os

load_dotenv()

DEFAULT_MODEL = os.getenv("MODEL", "qwen2:7b") 

def generar_test_cases(descripcion: str, model: str = DEFAULT_MODEL, contexto_extra: str = "") -> TestCaseResponse:
    user_prompt = f"""Genera casos de prueba **EXCLUSIVAMENTE** basados en esta descripción:

{descripcion}

{contexto_extra if contexto_extra else ""}

Responde **SOLO** con un JSON válido. Nada más. No uses markdown, no uses ```json."""

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt}
    ]

    for intento in range(1, 6):
        try:
            response = ollama.chat(
                model=model,
                messages=messages,
                options={"temperature": 0.0, "num_predict": 4000}
            )

            content = response['message']['content'].strip()

            print(f"\n[DEBUG intento {intento}] Respuesta cruda:\n{content}\n")

            # Limpieza del JSON
            if "```json" in content:
                start = content.find("```json") + 7
                end = content.find("```", start)
                json_str = content[start:end].strip()
            else:
                start = content.find("{")
                end = content.rfind("}") + 1
                json_str = content[start:end]

            data = json.loads(json_str)
            return TestCaseResponse.model_validate(data)

        except Exception as e:
            print(f"[Intento {intento}/5] Error: {type(e).__name__} - {e}")

    raise RuntimeError("No se pudo obtener un JSON válido después de 5 intentos.")