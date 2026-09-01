import os
import time
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_ollama import OllamaLLM
from src.config import GEMINI_API_KEY, LLM_MODELO


class LLMManager:
    def __init__(
        self,
        modelo_local: str = LLM_MODELO,
        modelo_remoto: str = "gemini-2.5-flash",
        reintentos: int = 3,
        espera: int = 2,
    ):
        self.modelo_local = modelo_local
        self.modelo_remoto = modelo_remoto
        self.reintentos = reintentos
        self.espera = espera
        self._llm = None
        self.modo_actual = None
        self.ultimo_usage = None

    def _conectar(self):
        if self._llm is not None:
            return self._llm

        # 1. Intentar conectar con Gemini API si la clave existe
        api_key = GEMINI_API_KEY or os.getenv("GEMINI_API_KEY")
        if api_key:
            try:
                print(f"🟢 Inicializando Gemini API ({self.modelo_remoto})...")
                self._llm = ChatGoogleGenerativeAI(
                    model=self.modelo_remoto,
                    google_api_key=api_key,
                    temperature=0.2,
                    max_output_tokens=2048,
                )
                self.modo_actual = "gemini"
                return self._llm
            except Exception as e:
                print(f"⚠️ Error al instanciar Gemini: {e}. Probando Ollama...")

        # 2. Modo local con Ollama
        print(f"🟠 Inicializando Ollama local ({self.modelo_local})...")
        self._llm = OllamaLLM(model=self.modelo_local)
        self.modo_actual = "ollama"
        return self._llm

    def invoke(self, prompt: str) -> str:
        ultimo_error = None
        for intento in range(self.reintentos):
            try:
                llm = self._conectar()
                respuesta = llm.invoke(prompt)

                # Extraer tokens si está disponible (Gemini API)
                if hasattr(respuesta, "response_metadata"):
                    try:
                        usage = respuesta.response_metadata.get("usage", {})
                        self.ultimo_usage = {
                            "entrada": usage.get("prompt_tokens", 0),
                            "salida": usage.get("candidates_tokens", 0) or usage.get("output_tokens", 0),
                        }
                    except Exception:
                        pass

                # Si usamos ChatGoogleGenerativeAI, la respuesta puede ser un objeto AIMessage.
                # Extraemos el contenido textual limpio:
                if hasattr(respuesta, "content"):
                    return respuesta.content
                return str(respuesta)

            except Exception as e:
                ultimo_error = e
                print(
                    f"⚠️ Fallo en intento {intento + 1}/{self.reintentos} "
                    f"({self.modo_actual}): {e}"
                )
                if intento < self.reintentos - 1:
                    time.sleep(self.espera)
                # Si falla, reiniciamos para reintentar la conexión
                self._llm = None

        raise ConnectionError(
            f"No se pudo obtener respuesta tras {self.reintentos} intentos. "
            f"Último error: {ultimo_error}"
        )
    
    def obtener_ultimo_usage(self) -> dict:
        """Obtener estadísticas de tokens del último invoke."""
        if self.ultimo_usage:
            return self.ultimo_usage
        return {"entrada": 0, "salida": 0}


_instancia: LLMManager | None = None


def obtener_llm(modelo: str = LLM_MODELO) -> LLMManager:
    global _instancia
    if _instancia is None:
        _instancia = LLMManager(modelo_local=modelo)
    return _instancia