"""In-memory rate limits. The Fly app runs a single gunicorn worker, so one
process sees every request and a dict is enough (no Redis needed)."""
import os
import threading
import time
from collections import deque

from flask import request

_lock = threading.Lock()
_hits = {}  # (bucket, key) -> deque of timestamps
_last_prune = 0.0


def client_ip():
    # Fly's proxy sets Fly-Client-IP to the real client address
    return request.headers.get("Fly-Client-IP") or request.remote_addr or "unknown"


def allow(bucket, key, limit, window):
    """Sliding window: True and record the hit if `key` has made fewer than
    `limit` hits in `bucket` over the last `window` seconds."""
    global _last_prune
    now = time.time()
    with _lock:
        if now - _last_prune > 600:
            _prune(now)
            _last_prune = now
        hits = _hits.setdefault((bucket, key), deque())
        while hits and now - hits[0] > window:
            hits.popleft()
        if len(hits) >= limit:
            return False
        hits.append(now)
        return True


def _prune(now, max_window=86400):
    for k in [k for k, hits in _hits.items() if not hits or now - hits[-1] > max_window]:
        del _hits[k]


# Any endpoint: stops floods without getting in the way of a fast sim
REQUESTS_PER_MINUTE = int(os.getenv("REQUESTS_PER_MINUTE", "240"))
# Requests that call OpenAI (each one makes up to 10 calls)
EXPLAIN_PER_MINUTE = int(os.getenv("EXPLAIN_PER_MINUTE", "15"))
EXPLAIN_PER_DAY_PER_IP = int(os.getenv("EXPLAIN_PER_DAY_PER_IP", "150"))
# Backstop for the whole app, whatever the number of IPs
EXPLAIN_PER_DAY_GLOBAL = int(os.getenv("EXPLAIN_PER_DAY_GLOBAL", "2000"))


def allow_request():
    return allow("req", client_ip(), REQUESTS_PER_MINUTE, 60)


def allow_explanations():
    ip = client_ip()
    return (allow("explain_min", ip, EXPLAIN_PER_MINUTE, 60)
            and allow("explain_day", ip, EXPLAIN_PER_DAY_PER_IP, 86400)
            and allow("explain_global", "all", EXPLAIN_PER_DAY_GLOBAL, 86400))
