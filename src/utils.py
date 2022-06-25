from hashlib import md5
import time
from typing import Dict, Optional, Tuple
from zlib import crc32


class GOSSolver:

    DEFAULT_A = 1800
    MAX_RPC = 100

    _path = bytes.fromhex("68747470733a2f2f7777772e676f7375736c7567692e72752f5f5f6a7363682f736368656d612e6a736f6e").decode()
    _verifier = bytes.fromhex("5f5f6a7363682f7374617469632f7363726970742e6a73")

    # this is going to be shared between all tasks
    # but only within a single process. we rely on
    # async execution being done on the same thread
    # to avoid necessity to keep locks around
    _cache = {}

    @property
    def path(self) -> str:
        return self._path

    def _challenge(self, value: str) -> str:
        return md5(value.encode()).digest().hex()

    def bypass(self, resp: bytes) -> bool:
        return self._verifier not in resp

    def time_bucket(self, a):
        ts = int(time.time())
        return ts - ts%a

    def lookup(self, a, ip) -> Optional[Tuple[int, str, Dict[str, str]]]:
        current = self._cache.get(ip)
        if current is None: return None
        bucket, _, _= current
        new_bucket = self.time_bucket(a)
        if bucket > new_bucket: return current
        # evict from the cache
        del self._cache[ip]
        return None

    def cache(self, ip, bucket, ua, cookies) -> None:
        self._cache[ip] = (bucket, ua, cookies)

    def solve(self, ua, resp) -> Tuple[int, Dict[str, str]]:
        a, ip, cn = resp["a"], resp["ip"], resp["cn"]
        bucket = self.time_bucket(a)
        value = f"{ua}:{ip}:{bucket}"
        for pos in range(10_000_000):
            response = self._challenge(f"{value}{pos}")
            if response[6:10] == "3fe3":
                cookies = {
                    cn: response.upper(),
                    f"{cn}_2": pos,
                    f"{cn}_3": crc32(value.encode())
                }
                self.cache(ip, bucket+a, ua, cookies)
                return (bucket+a, cookies)
        raise ValueError("invalid input")
