import json
from pathlib import Path
from typing import List, Dict

class LocalJSONLStorage:
    def __init__(self, folder: str = "data"):
        self.folder = Path(folder)
        self.folder.mkdir(parents=True, exist_ok=True)

    def save(self, offers: List[Dict], filename: str = "all_offers.jsonl") -> str:
        """
        Appends a list of offers to a JSONL file (each as a new JSON line).
        Returns the path to the file.
        """
        path = self.folder / filename
        with path.open("a", encoding="utf-8") as f:
            for o in offers:
                f.write(json.dumps(o, ensure_ascii=False) + "\n")
        return str(path)