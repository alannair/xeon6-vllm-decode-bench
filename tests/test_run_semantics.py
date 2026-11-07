import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock

from bench import control
from bench.common import atomic_json, read_json, timestamp_id
from bench.runner import RunTimeout


class StateTests(unittest.TestCase):
    def test_atomic_progress(self):
        with tempfile.TemporaryDirectory() as temp:
            p = Path(temp) / 'progress.json'
            atomic_json(p, {'plan_id': 'abc', 'runs': {'x': {'status': 'done'}}})
            self.assertEqual(read_json(p)['runs']['x']['status'], 'done')
            atomic_json(p, {'plan_id': 'abc', 'runs': {'x': {'status': 'failed'}}})
            self.assertEqual(read_json(p)['runs']['x']['status'], 'failed')

    def test_stop_flag(self):
        with tempfile.TemporaryDirectory() as temp:
            p = Path(temp)
            with mock.patch.object(control, 'STATE', p), mock.patch.object(control, 'running_pid', return_value=None):
                control.stop()
                self.assertTrue((p / 'stop.flag').exists())


if __name__ == '__main__':
    unittest.main()
