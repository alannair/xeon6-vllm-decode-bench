import math
import unittest

from bench.client import percentile, metric_lines
from bench.perf import parse_perf_line


class ParserTests(unittest.TestCase):
    def test_parse_perf_simple(self):
        expected = {'cycles': 'cycles', 'instructions': 'instructions'}
        raw = '0.100123;1,234;;cycles;99999999;100.00;'
        p = parse_perf_line(raw, expected)
        self.assertIsNotNone(p)
        self.assertAlmostEqual(p[0], .100123)
        self.assertEqual(p[1], 'cycles')
        self.assertEqual(p[2], 1234)
        self.assertEqual(p[4], 100.0)
        self.assertIsNone(parse_perf_line('perf stat invalid permission', expected))
        self.assertIsNone(parse_perf_line('0.200;<not counted>;;cycles;', expected))

    def test_parse_perf_uncore(self):
        key = 'uncore_imc_0/cas_count_read_sch0/'
        raw = '1.200;320;;' + key + ';10000000;100.00;'
        p = parse_perf_line(raw, {key: 'cas_read'})
        self.assertEqual(p[1], key)
        self.assertEqual(p[2], 320)

    def test_metric_lines(self):
        values = list(metric_lines('''# HELP vllm:num_requests_running Number running
vllm:num_requests_running{model_name="Qwen/Qwen3-4B"} 3
vllm:num_requests_waiting 7
vllm:generation_tokens_total 1.5e3
'''))
        self.assertEqual([x[0] for x in values], ['vllm:num_requests_running', 'vllm:num_requests_waiting', 'vllm:generation_tokens_total'])
        self.assertEqual([x[2] for x in values], [3, 7, 1500])

    def test_percentile(self):
        self.assertEqual(percentile([1, 2, 3, 4, 5], .5), 3)
        self.assertEqual(percentile([1, 2, 3, 4], .75), 3.25)
        self.assertIsNone(percentile([], .5))


if __name__ == '__main__':
    unittest.main()
