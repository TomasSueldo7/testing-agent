import litellm
from .models import TestCaseResponse
from .prompts import SYSTEM_PROMPT
from dotenv import load_dotenv
import json
import os

load_dotenv()

DEFAULT_MODEL = os.getenv("MODEL", "ollama/qwen2:7b")

def generar_test_cases(
    descripcion: str,
    model: str = DEFAULT_MODEL,
    contexto_extra: str = "",
    tags: list = None
) -> TestCaseResponse:
    if tags is None:
        tags = []

    # === DEBUG FUERTE: qué está llegando realmente ===
    print("\n" + "="*80)
    print("DEBUG GENERATOR - DESCRIPCIÓN RECIBIDA DEL CLI/JIRA:")
    print(descripcion[:1500])   # mostramos los primeros 1500 caracteres
    print("="*80 + "\n")

    user_prompt = f"""Genera casos de prueba **EXCLUSIVAMENTE** para esta funcionalidad descrita en el ticket Jira:

{descripcion}

Contexto adicional del usuario:
{contexto_extra if contexto_extra else "Ninguno"}

Tags sugeridos: {', '.join(tags) if tags else "Ninguno"}

IMPORTANTE: Usa SOLO la información del ticket anterior. No inventes nada.
"""

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt}
    ]

    for intento in range(1, 6):
        try:
            response = litellm.completion(
                model=model,
                messages=messages,
                temperature=0.0,
                max_tokens=4000,
            )

            content = response.choices[0].message.content.strip()
            print(f"\n[DEBUG - Respuesta cruda (intento {intento})]\n{content}\n")

            # Extraer JSON
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