import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.environ["VELAN_AGENT"] = "offline"
os.environ.setdefault("VELAN_DATA_DIR", str(ROOT / "data" / "test"))
