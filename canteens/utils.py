from __future__ import annotations

import asyncio
from functools import wraps


def native_coroutine(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        return asyncio.run(f(*args, **kwargs))

    return wrapper
