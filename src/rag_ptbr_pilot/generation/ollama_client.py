"""Cliente do Ollama (geração local Qwen3 14B) — etapa opcional.

Registra modelo (tag/digest), prompt realmente enviado, parâmetros (temperatura,
seed quando suportada, modo de raciocínio, num_ctx). Temperatura inicial 0;
determinismo absoluto NÃO é prometido.

O prompt trata os documentos como DADOS: instruções encontradas nos artigos não
substituem as instruções do sistema.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from ..errors import MissingArtifactError
from ..timing import Timer


@dataclass
class GenerationResult:
    question_id: str
    config_id: str
    model: str
    response: str
    prompt_sent: str
    context_included: list[str] = field(default_factory=list)
    context_text: str = ""
    parameters: dict = field(default_factory=dict)
    latency_s: float | None = None
    error: str | None = None

    def to_dict(self) -> dict:
        return {
            "question_id": self.question_id,
            "config_id": self.config_id,
            "model": self.model,
            "response": self.response,
            "prompt_sent": self.prompt_sent,
            "context_included": self.context_included,
            "context_text": self.context_text,
            "parameters": self.parameters,
            "latency_s": self.latency_s,
            "error": self.error,
        }


class OllamaClient:
    def __init__(self, host: str, model: str, temperature: float = 0.0,
                 seed: int | None = None, num_ctx: int = 8192,
                 reasoning: bool = False, tag: str | None = None,
                 digest: str | None = None, timeout: int = 600) -> None:
        self.host = host.rstrip("/")
        self.model = model
        self.temperature = temperature
        self.seed = seed
        self.num_ctx = num_ctx
        self.reasoning = reasoning
        self.tag = tag
        self.digest = digest
        self.timeout = timeout

    def _full_model(self) -> str:
        return self.model  # tag/digest são registrados separadamente no manifesto

    def generate(self, question_id: str, config_id: str,
                 prompt: str) -> GenerationResult:
        try:
            import requests
        except ImportError:
            raise MissingArtifactError(
                "Biblioteca 'requests' não instalada. Instale: pip install -e '.[generate]'"
            ) from None

        payload: dict = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "temperature": self.temperature,
            "options": {"num_ctx": self.num_ctx},
        }
        if self.seed is not None:
            payload["seed"] = self.seed
        if self.reasoning:
            payload["think"] = True

        result = GenerationResult(
            question_id=question_id,
            config_id=config_id,
            model=self._full_model(),
            response="",
            prompt_sent=prompt,
            parameters={
                "temperature": self.temperature,
                "seed": self.seed,
                "num_ctx": self.num_ctx,
                "reasoning": self.reasoning,
                "tag": self.tag,
                "digest": self.digest,
            },
        )

        timer = Timer()
        try:
            resp = requests.post(
                f"{self.host}/api/generate", json=payload, timeout=self.timeout
            )
            resp.raise_for_status()
            data = resp.json()
            result.response = data.get("response", "")
            # Registra o modelo efetivamente servido (com digest/tag reais).
            served = data.get("model", self.model)
            result.model = served
            result.parameters["served_model"] = served
        except Exception as exc:
            result.error = str(exc)
        result.latency_s = timer.stop()
        return result
