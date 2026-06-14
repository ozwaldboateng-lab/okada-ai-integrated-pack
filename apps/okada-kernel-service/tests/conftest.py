from __future__ import annotations

import sys
from pathlib import Path

LOCAL_APP_ROOT = Path(__file__).resolve().parents[1]
if str(LOCAL_APP_ROOT) not in sys.path:
    sys.path.insert(0, str(LOCAL_APP_ROOT))
