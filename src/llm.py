import time

from langchain_ollama import OllamaLLM

from src.config import LLM_MODELO


class OllamaFallback:
    def __init__(self, modelo: str = LLM_MODELO, reintentos: int = 3, espera: int = 2):
        self.modelo = modelo
        self.reintentos = reintentos
        self.espera = espera
        self._llm = None

    def _conectar(self):
        if self._llm is None:
            self._llm = OllamaLLM(model=self.modelo)
        return self._llm

    def invoke(self, prompt: str) -> str:
        ultimo_error = None
        for intento in range(self.reintentos):
            try:
                llm = self._conectar()
                return llm.invoke(prompt)
            except Exception as e:
                ultimo_error = e
                if intento < self.reintentos - 1:
                    time.sleep(self.espera)
                self._llm = None
        raise ConnectionError(
            f"No se pudo conectar con Ollama tras {self.reintentos} intentos: {ultimo_error}"
        )


_instancia: OllamaFallback | None = None


def obtener_llm(modelo: str = LLM_MODELO) -> OllamaFallback:
    global _instancia
    if _instancia is None:
        _instancia = OllamaFallback(modelo=modelo)
    return _instancia
