from src.vector_store import buscar


def main():
    print("Motor de búsqueda semántica (escribe 'salir' para terminar)")
    while True:
        pregunta = input("\nPregunta: ")
        if pregunta.lower().strip() == "salir":
            break
        resultados = buscar(pregunta, k=1)
        if resultados:
            print(f"\nFragmento:\n{resultados[0].page_content}")


if __name__ == "__main__":
    main()
