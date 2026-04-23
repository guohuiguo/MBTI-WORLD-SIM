from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Optional


class JsonStateStore:
    def __init__(self, base_dir: str = "runtime_data", filename: str = "sim_state.json") -> None:
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.filepath = self.base_dir / filename

    def exists(self) -> bool:
        return self.filepath.exists()

    def load(self) -> Optional[Dict[str, Any]]:
        if not self.exists():
            return None
        with self.filepath.open("r", encoding="utf-8") as f:
            return json.load(f)

    def save(self, data: Dict[str, Any]) -> None:
        with self.filepath.open("w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def clear(self) -> None:
        if self.exists():
            self.filepath.unlink()