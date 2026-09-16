"""Exceções do domínio do piloto.

Separar erros de domínio de exceções de biblioteca facilita mensagens úteis
para o usuário final e evita rastreios confusos quando um artefato está ausente
ou uma anotação é inválida.
"""

from __future__ import annotations


class PilotError(Exception):
    """Base para todos os erros de domínio do projeto."""


class ConfigError(PilotError):
    """Configuração inválida ou inconsistente."""


class ValidationError(PilotError):
    """Arquivo de benchmark (metadados/perguntas/qrels/grupos) inválido."""


class MissingArtifactError(PilotError):
    """Artefato necessário ausente (checkpoint, índice, embedding, chunk...).

    A mensagem deve sempre conter a instrução de como obter o artefato.
    """


class FrozenCorpusError(PilotError):
    """Tentativa de usar um corpus/benchmark que foi alterado após o congelamento."""


class NoGoldError(PilotError):
    """Pergunta sem gold válido (sem relevância anotada aprovada).

    Usada para BLOQUEAR a avaliação da pergunta em vez de atribuir zero.
    """


class IncompleteJudgmentError(PilotError):
    """Julgamentos incompletos limitam as métricas (aviso, não fatal por padrão)."""
