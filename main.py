try:
    from fastmcp import FastMCP
except Exception:
    # Proveer un fallback mínimo para poder importar el módulo sin fastmcp
    class _DummyMCP:
        def __init__(self, name=None):
            self.name = name

        def tool(self, f=None):
            if f is None:
                def decorator(fn):
                    return fn
                return decorator
            return f

        def resource(self, _=None):
            def decorator(fn):
                return fn
            return decorator

        def prompt(self, f=None):
            if f is None:
                def decorator(fn):
                    return fn
                return decorator
            return f

        def run(self):
            print("fastmcp no está instalado: modo dummy, sin servidor MCP")

    FastMCP = _DummyMCP

import csv
from pathlib import Path
from datetime import datetime

mcp = FastMCP('Gastos MCP')


@mcp.tool
def agregar_gasto(fecha: str, categoria: str, cantidad: float, metodo_de_pago: str):
    """Agrega un gasto a `gastos.csv`.

    Parámetros esperados:
    - fecha: cadena en formato YYYY-MM-DD
    - categoria: cadena no vacía
    - cantidad: número (float)
    - metodo_de_pago: cadena no vacía

    Devuelve un mensaje de confirmación o una descripción del error.
    """
    # Validaciones básicas
    try:
        datetime.strptime(fecha, "%Y-%m-%d")
    except Exception:
        return f"Error: fecha inválida '{fecha}'. Usa YYYY-MM-DD."

    if not categoria or not categoria.strip():
        return "Error: la categoría no puede estar vacía."

    try:
        cantidad = float(cantidad)
    except Exception:
        return f"Error: cantidad inválida '{cantidad}'. Debe ser un número."

    if cantidad < 0:
        return "Error: la cantidad no puede ser negativa."

    if not metodo_de_pago or not str(metodo_de_pago).strip():
        return "Error: el método de pago no puede estar vacío."

    # Ruta al archivo gastos.csv (misma carpeta que este script)
    csv_path = Path(__file__).parent / "gastos.csv"

    # Asegurar que el archivo existe y, si no, crear con cabecera
    file_exists = csv_path.exists()

    try:
        with csv_path.open("a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(["fecha", "categoria", "cantidad", "metodo_de_pago"])
            # Escribir la fila (cantidad con dos decimales)
            writer.writerow([fecha, categoria, f"{cantidad:.2f}", metodo_de_pago])
    except Exception as e:
        return f"Error al escribir en el archivo: {e}"

    return f"Se ha agregado tu gasto: {fecha}, {categoria}, {cantidad:.2f}, {metodo_de_pago}"


@mcp.resource('resource://gastos')
def datos_de_gastos():
    """Devuelve todos los gastos almacenados en `gastos.csv`.

    La salida es una cadena JSON (UTF-8) con la forma:
    {"gastos": [{"fecha":"YYYY-MM-DD","categoria":"...","cantidad": number, "metodo_de_pago":"..."}, ...]}

    Este formato es sencillo de parsear por un LLM o por cualquier programa.
    """
    csv_path = Path(__file__).parent / "gastos.csv"
    if not csv_path.exists():
        return '{"gastos": []}'

    try: 
        with csv_path.open("r", encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)
            gastos = []
            for row in reader:
                # Normalizar y convertir tipos
                fecha = row.get("fecha", "")
                categoria = row.get("categoria", "")
                metodo = row.get("metodo_de_pago", row.get("metodo_de_pago", ""))
                cantidad_raw = row.get("cantidad", "")
                try:
                    cantidad = float(cantidad_raw) if cantidad_raw != "" else None
                except Exception:
                    cantidad = cantidad_raw

                gastos.append({
                    "fecha": fecha,
                    "categoria": categoria,
                    "cantidad": cantidad,
                    "metodo_de_pago": metodo,
                })
        import json

        return json.dumps({"gastos": gastos}, ensure_ascii=False)
    except Exception as e:
        return f"Error leyendo gastos: {e}"

@mcp.prompt
def prompt_agregar_gasto():
    return 'Usa la herramienta agregar_gasto para agregar este gasto con'

#def main():
#    print("Hello from mcp-basico!")


if __name__ == "__main__":
    mcp.run()
