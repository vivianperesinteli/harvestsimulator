"""Configura sys.path para que todos os testes encontrem backend e frontend."""

import sys
from pathlib import Path

ROOT    = Path(__file__).parent.parent
BACKEND = ROOT / "backend"

for p in (str(ROOT), str(BACKEND)):
    if p not in sys.path:
        sys.path.insert(0, p)
