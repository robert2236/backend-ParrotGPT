import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.vector_store import indexar
from src.config import RUTA_PDF


def main():
    pdfs = list(RUTA_PDF.glob("*.pdf"))
    if not pdfs:
        print(f"No se encontraron PDFs en {RUTA_PDF}")
        return

    for ruta in pdfs:
        print(f"Indexando {ruta.name}...")
        indexar(str(ruta))
        print(f"  OK")

    print("Indexación completada.")


if __name__ == "__main__":
    main()
