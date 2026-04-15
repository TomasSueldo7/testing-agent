from flask import Flask, render_template, request, jsonify, send_file
import os
import sys
import json
from datetime import datetime
from .core.generator import generar_test_cases, DEFAULT_MODEL
from dotenv import load_dotenv
from jira import JIRA

load_dotenv()

# === MANEJO DE TEMPLATES PARA PYINSTALLER ===
if getattr(sys, 'frozen', False):
    template_folder = os.path.join(sys._MEIPASS, 'templates')
    config_path = os.path.join(os.path.dirname(sys.executable), "config.json")
else:
    template_folder = os.path.join(os.path.dirname(__file__), 'templates')
    config_path = "config.json"

app = Flask(__name__, template_folder=template_folder)

# Cargar / Guardar configuración (multi-Jira)
def load_config():
    default = {
        "model": "qwen2:7b",
        "jira_profiles": []   # lista de perfiles: [{"name": "Proyecto A", "url": "...", "email": "...", "token": "..."}]
    }
    if os.path.exists(config_path):
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return default
    return default

def save_config(config):
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)

config = load_config()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/config", methods=["GET"])
def get_config():
    return jsonify(config)

@app.route("/api/config", methods=["POST"])
def save_config_api():
    global config
    data = request.json
    config["model"] = data.get("model", "qwen2:7b")
    config["jira_profiles"] = data.get("jira_profiles", [])
    save_config(config)
    return jsonify({"success": True})

# =============================================
# GENERAR MANUAL
# =============================================
@app.route("/generate/manual", methods=["POST"])
def generate_manual():
    data = request.json
    descripcion = data.get("descripcion", "")
    contexto = data.get("contexto", "")

    if not descripcion.strip():
        return jsonify({"error": "Ingresa una descripción"}), 400

    try:
        resultado = generar_test_cases(descripcion, config["model"], contexto)
        return jsonify({
            "success": True,
            "feature": resultado.feature,
            "escenarios": [esc.model_dump() for esc in resultado.escenarios]
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# =============================================
# GENERAR JIRA (usa el perfil seleccionado)
# =============================================
@app.route("/generate/jira", methods=["POST"])
def generate_jira():
    data = request.json
    ticket = data.get("ticket", "")
    contexto = data.get("contexto", "")
    profile_index = data.get("profile_index", 0)

    if not ticket.strip():
        return jsonify({"error": "Ingresa un ticket de Jira"}), 400

    try:
        profiles = config.get("jira_profiles", [])
        if not profiles or profile_index >= len(profiles):
            return jsonify({"error": "No hay perfiles de Jira configurados"}), 400

        profile = profiles[profile_index]
        jira_client = JIRA(
            server=profile["url"],
            basic_auth=(profile["email"], profile["token"])
        )
        issue = jira_client.issue(ticket.strip())
        desc_jira = f"Ticket: {issue.key} - {issue.fields.summary}\n\n{issue.fields.description or 'Sin descripción'}"

        resultado = generar_test_cases(desc_jira, config["model"], contexto)
        return jsonify({
            "success": True,
            "feature": resultado.feature,
            "escenarios": [esc.model_dump() for esc in resultado.escenarios]
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    print("=== Servidor iniciado - Templates Auto Reload activado ===")
    app.run(host="127.0.0.1", port=3000, debug=True)