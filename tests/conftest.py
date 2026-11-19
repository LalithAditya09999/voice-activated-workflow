import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.environ["SAATHI_AGENT"] = "offline"
os.environ.setdefault("SAATHI_DATA_DIR", str(ROOT / "data" / "test"))
