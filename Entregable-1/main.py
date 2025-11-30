import os
from rich.console import Console
from rich.table import Table
from rich.markdown import Markdown

console = Console()

# Directorio raíz donde están los archivos .md
PROJECT_PATH = os.getcwd()

def listar_archivos_md():
    """Devuelve una lista de archivos .md del directorio raíz."""
    return [f for f in os.listdir(PROJECT_PATH) if f.endswith('.md')]

def mostrar_archivo(path):
    """Muestra el contenido de un archivo Markdown con formato."""
    console.clear()
    console.rule(f"[bold cyan]📄 {os.path.basename(path)}")
    with open(path, "r", encoding="utf-8") as f:
        contenido = f.read()
    console.print(Markdown(contenido))
    console.print("\nPresiona Enter para volver al menú...")
    input()

def buscar_en_archivos(palabra):
    """Busca una palabra clave en todos los archivos .md."""
    resultados = []
    for archivo in listar_archivos_md():
        with open(archivo, "r", encoding="utf-8") as f:
            contenido = f.read().lower()
            if palabra.lower() in contenido:
                resultados.append(archivo)
    return resultados

def menu():
    while True:
        console.clear()
        console.rule("[bold green]🤖 CONSULTOR DEL PROYECTO AURELION")
        console.print("[bold yellow]Selecciona una opción:\n")

        opciones = listar_archivos_md()
        for i, archivo in enumerate(opciones, start=1):
            console.print(f"[cyan]{i}.[/cyan] {archivo}")

        console.print("\n[b]B.[/b] Buscar palabra clave en todo el proyecto")
        console.print("[b]R.[/b] Exportar resumen automático del proyecto")
        console.print("[b]S.[/b] Salir\n")

        eleccion = input("👉 Opción: ").strip()

        if eleccion.lower() == 's':
            console.print("\n👋 ¡Hasta luego, estudiante de IA!")
            break

        elif eleccion.lower() == 'b':
            palabra = input("🔍 Ingresar palabra a buscar: ")
            resultados = buscar_en_archivos(palabra)
            if resultados:
                console.print(f"\n✅ Encontrado en: {', '.join(resultados)}")
            else:
                console.print("\n❌ No se encontró en ningún archivo.")
            input("\nPresiona Enter para continuar...")

        elif eleccion.isdigit() and 1 <= int(eleccion) <= len(opciones):
            archivo_seleccionado = opciones[int(eleccion) - 1]
            mostrar_archivo(archivo_seleccionado)
        
        elif eleccion.lower() == 'r':
             exportar_resumen()


        else:
            console.print("[red]Opción no válida. Intenta nuevamente.")
            input()
       
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

def exportar_resumen():
    """Genera un resumen automático estilo ejecutivo con emojis y lo exporta a MD y PDF."""
    resumen = "# 🚀 Resumen Ejecutivo del Proyecto *Aurelion IA*\n\n"
    resumen += "Este documento reúne los principales puntos de cada componente del proyecto, sintetizados automáticamente para facilitar una lectura rápida y estratégica.\n\n"

    for archivo in listar_archivos_md():
        with open(archivo, "r", encoding="utf-8") as f:
            contenido = f.readlines()

        resumen += f"\n## 📄 {archivo}\n\n"

        agregado = False
        for linea in contenido:
            if linea.strip() and not linea.startswith("#") and len(linea) > 40:
                resumen += f"✅ {linea.strip()}\n"
                agregado = True
                break

        if not agregado:
            resumen += "⚠️ Sin contenido destacable para resumir.\n"

    resumen += "\n---\n\n🧠 *Resumen generado automáticamente por el Asistente IA del Proyecto.*"

    # Guardar como .md
    with open("RESUMEN_PROYECTO.md", "w", encoding="utf-8") as salida:
        salida.write(resumen)

    # Exportar como PDF
    pdf = canvas.Canvas("RESUMEN_PROYECTO.pdf", pagesize=A4)
    width, height = A4
    y = height - 40

    for linea in resumen.split("\n"):
        if y < 50:  # Nueva página si se llena
            pdf.showPage()
            y = height - 40
        pdf.drawString(40, y, linea[:100])  # Corto para evitar desbordes
        y -= 15

    pdf.save()

    console.print("\n✅ Archivos 'RESUMEN_PROYECTO.md' y 'RESUMEN_PROYECTO.pdf' generados con éxito 💼🚀.")
    input("\nPresiona Enter para volver al menú...")


if __name__ == "__main__":
    menu()
