from flask import Flask, render_template, request, jsonify, send_file
import os
import json
from datetime import datetime
from test_case_agent.core.generator import generar_test_cases, DEFAULT_MODEL
from dotenv import load_dotenv
from jira import JIRA

load_dotenv()

app = Flask(__name__, template_folder="templates", static_folder="static")

# Crear carpeta suites y templates si no existen
os.makedirs("suites", exist_ok=True)
os.makedirs("templates", exist_ok=True)
os.makedirs("static", exist_ok=True)

# =============================================
# RUTA PRINCIPAL
# =============================================
@app.route("/")
def index():
    return render_template("index.html")

# =============================================
# GENERAR DESDE DESCRIPCIÓN MANUAL
# =============================================
@app.route("/generate/manual", methods=["POST"])
def generate_manual():
    data = request.json
    descripcion = data.get("descripcion", "")
    contexto = data.get("contexto", "")

    if not descripcion.strip():
        return jsonify({"error": "Ingresa una descripción"}), 400

    try:
        resultado = generar_test_cases(descripcion, DEFAULT_MODEL, contexto, [])
        return jsonify({
            "success": True,
            "feature": resultado.feature,
            "escenarios": [esc.model_dump() for esc in resultado.escenarios]
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# =============================================
# GENERAR DESDE JIRA
# =============================================
@app.route("/generate/jira", methods=["POST"])
def generate_jira():
    data = request.json
    ticket = data.get("ticket", "")
    contexto = data.get("contexto", "")

    if not ticket.strip():
        return jsonify({"error": "Ingresa un ticket de Jira"}), 400

    try:
        jira_client = JIRA(
            server=os.getenv("JIRA_URL"),
            basic_auth=(os.getenv("JIRA_EMAIL"), os.getenv("JIRA_API_TOKEN"))
        )
        issue = jira_client.issue(ticket.strip())
        desc_jira = f"Ticket: {issue.key} - {issue.fields.summary}\n\n{issue.fields.description or 'Sin descripción'}"

        resultado = generar_test_cases(desc_jira, DEFAULT_MODEL, contexto, [])
        return jsonify({
            "success": True,
            "feature": resultado.feature,
            "escenarios": [esc.model_dump() for esc in resultado.escenarios]
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# =============================================
# DESCARGAR TXT
# =============================================
@app.route("/download", methods=["POST"])
def download_txt():
    data = request.json
    feature = data.get("feature", "test-cases")
    escenarios = data.get("escenarios", [])

    txt_content = f"# {feature}\n\n"
    for i, esc in enumerate(escenarios, 1):
        txt_content += f"Escenario {i}: {esc['titulo']}\n"
        txt_content += "Precondiciones:\n" + "\n".join(f"- {p}" for p in esc['precondiciones']) + "\n"
        txt_content += "Pasos:\n" + "\n".join(esc['steps']) + "\n\n"

    filename = f"test-cases-{feature.replace(' ', '-')}.txt"
    filepath = os.path.join("suites", filename)
    
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(txt_content)

    return send_file(filepath, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True, port=5000)