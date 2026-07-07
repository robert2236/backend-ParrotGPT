from pathlib import Path

import pdfplumber
from langchain_core.documents import Document


def cargar_pdf(ruta: str | Path) -> list[Document]:
    documentos = []
    with pdfplumber.open(ruta) as pdf:
        for i, pagina in enumerate(pdf.pages):
            texto_principal = pagina.extract_text() or ""

            tablas = pagina.extract_tables()
            texto_tablas = ""
            for tabla in tablas:
                for fila in tabla:
                    texto_tablas += " | ".join(celda or "" for celda in fila) + "\n"

            contenido = texto_principal
            if texto_tablas:
                contenido += "\n[Tabla]\n" + texto_tablas

            if contenido.strip():
                documentos.append(Document(
                    page_content=contenido,
                    metadata={"pagina": i + 1, "fuente": str(ruta)}
                ))
    return documentos
