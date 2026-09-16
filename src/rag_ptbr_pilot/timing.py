"""Medição de tempo com sincronização de GPU quando aplicável.

Distingue carregamento, aquecimento e inferência (nos módulos que os executam).
Medidas não coletadas ficam AUSENTES (None), nunca zero.
"""

from __future__ import annotations

import time


def now() -> float:
    return time.perf_counter()


def elapsed(t0: float) -> float:
    return time.perf_counter() - t0


def sync_gpu() -> None:
    """Sincroniza o device CUDA para medidas corretas de tempo de GPU."""
    try:
        import torch

        if torch.cuda.is_available():
            torch.cuda.synchronize()
    except Exception:
        # Sem torch/cuda: nada a sincronizar.
        pass


class Timer:
    """Cronômetro com sync opcional de GPU no stop."""

    def __init__(self) -> None:
        self.reset()

    def reset(self) -> None:
        self._t0 = now()

    def stop(self, sync: bool = True) -> float:
        if sync:
            sync_gpu()
        return elapsed(self._t0)
