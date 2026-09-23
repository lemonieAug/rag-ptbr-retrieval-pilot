import os
import subprocess
import sys

import pytest


@pytest.mark.parametrize("stream", ["stdout", "stderr"])
def test_cli_preserves_unicode_evidence_on_redirected_windows_streams(stream):
    evidence = "Evidência: ı → ∑"
    code = (
        "import sys; from rag_ptbr_pilot import cli; "
        f"cli.cmd_matrix = lambda args: print({evidence!r}, file=sys.{stream}); "
        "raise SystemExit(cli.main(['matrix']))"
    )
    env = dict(os.environ, PYTHONIOENCODING="cp1252")
    result = subprocess.run([sys.executable, "-c", code], env=env,
                            capture_output=True, check=False)
    assert result.returncode == 0, result.stderr
    assert getattr(result, stream).decode("utf-8").strip() == evidence
