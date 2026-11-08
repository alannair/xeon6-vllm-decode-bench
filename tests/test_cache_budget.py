import asyncio
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest import mock

from bench.cache import (GIB, CacheQuotaGuard, cache_size_bytes,
                         evict_active_model, evict_other_models,
                         guard_threshold_bytes, parse_cache_limit)
from bench.client import poll_storage
from bench.control import verify_cache_limit


class CacheTests(unittest.TestCase):
    def test_parsing(self):
        self.assertEqual(parse_cache_limit("20"), 20 * GIB)
        self.assertEqual(parse_cache_limit("0.5"), GIB // 2)
        self.assertIsNone(parse_cache_limit(None))
        for bad in ("0", "-1", "NaN", "infinity", "bogus", ""):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                parse_cache_limit(bad)

    def test_cap_is_persisted(self):
        setup = {"max_hf_cache_size_bytes": 22 * GIB}
        with mock.patch.dict("os.environ", {"MAX_HF_CACHE_SIZE_GB": "22"}):
            verify_cache_limit(setup)
        with mock.patch.dict("os.environ", {"MAX_HF_CACHE_SIZE_GB": "10"}):
            with self.assertRaisesRegex(RuntimeError, "Rerun"):
                verify_cache_limit(setup)
        with mock.patch.dict("os.environ", {}, clear=True):
            verify_cache_limit(setup)

    def test_private_cache_eviction(self):
        with TemporaryDirectory() as d:
            home = Path(d)
            a = home / "hub" / "models--Org--A" / "blobs"
            b = home / "hub" / "models--Org--B" / "blobs"
            a.mkdir(parents=True)
            b.mkdir(parents=True)
            (a / "w").write_bytes(b"a" * 4096)
            (b / "w").write_bytes(b"b" * 4096)
            before = cache_size_bytes(home)
            info = evict_other_models(home, "Org/A")
            self.assertEqual(info["removed_repositories"], ["models--Org--B"])
            self.assertTrue(a.exists())
            self.assertFalse(b.exists())
            self.assertLess(cache_size_bytes(home), before)
            (home / "xet").mkdir()
            evict_active_model(home, "Org/A")
            self.assertFalse(a.exists())
            self.assertFalse((home / "xet").exists())

    def test_guard(self):
        with TemporaryDirectory() as d:
            home = Path(d)
            calls = []
            limit = 128 * 1024**2
            guard = CacheQuotaGuard(home, limit, lambda: calls.append(True), interval_s=.01)
            guard.start()
            with mock.patch("bench.cache.cache_size_bytes", return_value=limit):
                import time
                for _ in range(200):
                    if guard.error:
                        break
                    time.sleep(.01)
            guard.stop()
            self.assertTrue(guard.error)
            self.assertEqual(calls, [True])
            self.assertLess(guard_threshold_bytes(limit), limit)

    def test_storage_csv(self):
        async def run(home, output):
            home.mkdir()
            (home / "weight").write_bytes(b"x" * 4096)
            stop = asyncio.Event()
            errors = []
            await poll_storage(home, .01, 0, output, stop, errors,
                               hf_home=home, max_hf_cache_size_bytes=1)
            return errors
        with TemporaryDirectory() as d:
            root = Path(d)
            errors = asyncio.run(run(root / "hf", root / "logs"))
            self.assertIn("MAX_HF_CACHE_SIZE_GB", errors[0])
            self.assertIn("hf_cache_gib", (root / "logs" / "storage.csv").read_text())


if __name__ == "__main__":
    unittest.main()
