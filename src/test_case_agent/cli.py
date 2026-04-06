import typer
import os
from rich.console import Console
from rich.markdown import Markdown
from .core.generator import generar_test_cases, DEFAULT_MODEL
from dotenv import load_dotenv
from jira import JIRA

app = typer.Typer(name="test-agent", help="Asistente local para generar casos de prueba en Gherkin")
console = Console()

def _mostrar_resultado(resultado):
    console.print(Markdown(f"# {resultado.feature}\n"))
    for i, esc in enumerate(resultado.escenarios, 1):
        console.print(f"[bold]Escenario {i}: {esc.titulo}[/]")
        console.print("[dim]Precondiciones:[/]")
        for p in esc.precondiciones:
            console.print(f"  • {p}")
        if esc.tags:
            console.print("[dim]Tags:[/] " + ", ".join(esc.tags))
        console.print("[dim]Pasos (Gherkin):[/]")
        for step in esc.steps:
            console.print(f"  {step}")
        console.print("─" * 80)

def main():
    app()

@app.command()
def generar(
    descripcion: str = typer.Argument(..., help="Descripción de la funcionalidad"),
    contexto: str = typer.Option("", "--contexto", "-c", help="Contexto adicional"),
    tags: str = typer.Option("", "--tags", "-t", help="Tags separados por coma"),
    model: str = typer.Option(None, "--model", "-m"),
):
    """Genera casos de prueba desde una descripción."""
    load_dotenv()

    # Conversión fuerte para evitar ArgumentInfo/OptionInfo
    descripcion = str(descripcion) if descripcion else ""
    contexto = str(contexto) if contexto else ""
    tags = str(tags) if tags else ""
    if model is None or not isinstance(model, str):
        model = DEFAULT_MODEL

    tag_list = [t.strip() for t in tags.split(",") if t.strip()]

    console.print(f"[bold blue]Modelo:[/] [cyan]{model}[/]")
    console.print("[bold green]Generando casos de prueba...[/bold green]")

    # Debug final
    console.print("[bold yellow]DEBUG - Descripción recibida:[/]")
    console.print(descripcion[:1200] + "..." if len(descripcion) > 1200 else descripcion)
    console.print("─" * 80)

    resultado = generar_test_cases(descripcion, model, contexto, tag_list)
    _mostrar_resultado(resultado)

@app.command()
def jira(
    ticket: str = typer.Argument(..., help="Ticket de Jira (ej: BAL-456)"),
    contexto: str = typer.Option("", "--contexto", "-c"),
    tags: str = typer.Option("", "--tags", "-t"),
    model: str = typer.Option(None, "--model", "-m"),
):
    """Lee un ticket de Jira y genera los test cases."""
    load_dotenv()

    contexto = str(contexto) if contexto else ""
    tags = str(tags) if tags else ""
    if model is None or not isinstance(model, str):
        model = DEFAULT_MODEL

    tag_list = [t.strip() for t in tags.split(",") if t.strip()]

    try:
        console.print("[bold blue]Conectando a Jira...[/]")
        jira_client = JIRA(
            server=os.getenv("JIRA_URL"),
            basic_auth=(os.getenv("JIRA_EMAIL"), os.getenv("JIRA_API_TOKEN"))
        )

        issue = jira_client.issue(ticket)
        console.print(f"[bold green]✅ Ticket Jira leído:[/] [cyan]{issue.key} - {issue.fields.summary}[/]")

        descripcion_jira = f"Ticket: {issue.key} - {issue.fields.summary}\n\n{issue.fields.description or 'Sin descripción'}"

        console.print("[bold yellow]DEBUG - Descripción enviada al modelo:[/]")
        console.print(descripcion_jira[:1200] + "..." if len(descripcion_jira) > 1200 else descripcion_jira)
        console.print("─" * 80)

        resultado = generar_test_cases(descripcion_jira, model, contexto, tag_list)
        _mostrar_resultado(resultado)

    except Exception as e:
        console.print(f"[bold red]❌ ERROR en Jira:[/] {type(e).__name__} - {e}")

if __name__ == "__main__":
    main()