import streamlit as st
import os
from test_case_agent.core.generator import generar_test_cases, DEFAULT_MODEL
from dotenv import load_dotenv
from jira import JIRA

load_dotenv()

st.set_page_config(page_title="Test Case Agent", page_icon="🧪", layout="wide")
st.title("🧪 Test Case Agent")
st.caption("Generador local de casos de prueba en Gherkin (Ollama + Jira)")

# =============================================
# FLUJO 1: Cargar desde Jira
# =============================================
st.subheader("1. Cargar desde Jira")
ticket_id = st.text_input("Ticket de Jira (ej: BAL-456)", placeholder="BAL-456")

if st.button("📥 Cargar ticket de Jira", type="secondary"):
    if not ticket_id.strip():
        st.error("Ingresa un ticket de Jira")
    else:
        with st.spinner("Conectando a Jira..."):
            try:
                jira_client = JIRA(
                    server=os.getenv("JIRA_URL"),
                    basic_auth=(os.getenv("JIRA_EMAIL"), os.getenv("JIRA_API_TOKEN"))
                )
                issue = jira_client.issue(ticket_id.strip())
                descripcion_jira = f"Ticket: {issue.key} - {issue.fields.summary}\n\n{issue.fields.description or 'Sin descripción'}"
                
                # Guardamos en session_state para que persista
                st.session_state.descripcion_jira = descripcion_jira
                st.success(f"✅ Ticket {issue.key} cargado correctamente")
                
            except Exception as e:
                st.error(f"Error al cargar ticket: {e}")

# =============================================
# FLUJO 2: Descripción manual
# =============================================
st.subheader("2. Descripción manual")
descripcion_manual = st.text_area(
    "Descripción de la funcionalidad",
    height=150,
    placeholder="El usuario puede iniciar sesión con su email y contraseña...",
    value=st.session_state.get("descripcion_manual", "")
)

# Guardamos la descripción manual también en session_state
if descripcion_manual:
    st.session_state.descripcion_manual = descripcion_manual

# =============================================
# Contexto adicional (común a ambos flujos)
# =============================================
contexto = st.text_area("Contexto adicional o instrucciones extra (opcional)", height=100)

# =============================================
# Selección de modelo
# =============================================
model = st.selectbox(
    "Modelo a usar",
    ["ollama/qwen2:7b", "ollama/llama3.1:8b"],
    index=0
)

# =============================================
# LÓGICA DE GENERACIÓN (separada por flujo)
# =============================================
if st.button("Generar casos de prueba", type="primary"):
    # Determinar qué descripción usar
    if st.session_state.get("descripcion_jira"):
        descripcion = st.session_state.descripcion_jira
        fuente = "Jira"
    elif st.session_state.get("descripcion_manual"):
        descripcion = st.session_state.descripcion_manual
        fuente = "Manual"
    else:
        st.error("Por favor carga un ticket de Jira o ingresa una descripción manual")
        st.stop()

    with st.spinner(f"Generando casos de prueba desde {fuente}..."):
        try:
            resultado = generar_test_cases(descripcion, model, contexto, [])

            st.subheader(resultado.feature)

            txt_output = f"# {resultado.feature}\n\n"

            for i, esc in enumerate(resultado.escenarios, 1):
                st.markdown(f"**Escenario {i}: {esc.titulo}**")
                
                st.write("**Precondiciones**")
                for p in esc.precondiciones:
                    st.write(f"- {p}")
                
                st.write("**Pasos (Gherkin)**")
                for step in esc.steps:
                    st.write(f"{step}")
                
                st.divider()

                # Para el TXT
                txt_output += f"Escenario {i}: {esc.titulo}\n"
                txt_output += "Precondiciones:\n" + "\n".join(f"- {p}" for p in esc.precondiciones) + "\n"
                txt_output += "Pasos:\n" + "\n".join(esc.steps) + "\n\n"

            # Botón de descarga
            st.download_button(
                label="📥 Descargar como .txt",
                data=txt_output,
                file_name=f"test-cases-{resultado.feature.replace(' ', '-')}.txt",
                mime="text/plain"
            )

        except Exception as e:
            st.error(f"Error: {e}")

st.info("💡 Puedes usar **solo uno** de los dos flujos (Jira o Manual). El contexto adicional es común a ambos.")