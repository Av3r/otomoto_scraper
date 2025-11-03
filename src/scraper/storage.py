"""Small local storage helpers used by integration tests.

Provides a thin JSONL writer used by the crawler to persist offers.
"""

import json
import os
from pathlib import Path
from typing import Dict, List


class LocalJSONLStorage:
    """Simple JSONL appender for lists of dictionaries."""

    def __init__(self, folder: str = "data"):
        # AWS Lambda can only write to /tmp
        # Check if running in Lambda environment
        if os.environ.get("AWS_LAMBDA_FUNCTION_NAME"):
            self.folder = Path("/tmp") / folder
        else:
            self.folder = Path(folder)
        self.folder.mkdir(parents=True, exist_ok=True)

    def save(self, offers: List[Dict], filename: str = "all_offers.jsonl") -> str:
        """Append `offers` to a JSONL file and return the path."""
        path = self.folder / filename
        with path.open("a", encoding="utf-8") as f:
            for o in offers:
                f.write(json.dumps(o, ensure_ascii=False) + "\n")
        return str(path)
