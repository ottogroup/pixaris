import unittest
from unittest.mock import patch
from pixaris.utils import retry as retry_module

retry_internal = getattr(retry_module, "__retry_internal")


class TestRetryInternal(unittest.TestCase):
    def test_retry_success_after_failures(self):
        call_count = {"count": 0}

        def func():
            call_count["count"] += 1
            if call_count["count"] < 3:
                raise ValueError("fail")
            return "success"

        with patch("time.sleep") as mock_sleep:
            result = retry_internal(
                func,
                exceptions=ValueError,
                tries=3,
                delay=1,
                max_delay=5,
                backoff=2,
            )
            self.assertEqual(result, "success")
            self.assertEqual(mock_sleep.call_count, 2)
            self.assertEqual(mock_sleep.call_args_list[0].args[0], 1)
            self.assertEqual(mock_sleep.call_args_list[1].args[0], 2)

    def test_retry_exhaust_raises(self):
        def func():
            raise RuntimeError("always")

        with patch("time.sleep") as mock_sleep:
            with self.assertRaises(RuntimeError):
                retry_internal(func, exceptions=RuntimeError, tries=2, delay=0.1)
            self.assertEqual(mock_sleep.call_count, 1)


class TestRetryDecorator(unittest.TestCase):
    def test_retry_decorator(self):
        call = {"count": 0}

        @retry_module.retry(exceptions=ValueError, tries=2, delay=0)
        def decorated(x):
            call["count"] += 1
            if call["count"] == 1:
                raise ValueError("first")
            return x * 2

        self.assertEqual(decorated(3), 6)
        self.assertEqual(call["count"], 2)


if __name__ == "__main__":
    unittest.main()
