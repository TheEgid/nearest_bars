from __future__ import annotations

import json
from functools import wraps
from pathlib import Path


def storage_json_io_decorator(storage_file_pathname: str):
    def memoize(func):
        @wraps(func)
        def decorate(*args, **kwargs):
            path = Path(storage_file_pathname)
            try:
                return json.loads(path.read_text(encoding="utf-8"))
            except FileNotFoundError:
                result = func(*args, **kwargs)
                path.write_text(json.dumps(result, ensure_ascii=False), encoding="utf-8")
                return result

        return decorate

    return memoize
