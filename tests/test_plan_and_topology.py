import json
import unittest
from pathlib import Path

from bench.common import ROOT
from bench.plan import make_plan, load_config
from bench.topology import choose_node, cpulist, parse_cpu_list, select_cores
from bench.runner import docker_args, kv_gb_for_node, safe_docker_name


class PlanningTests(unittest.TestCase):
    def test_parse_cpu_list_and_roundtrip(self):
        self.assertEqual(parse_cpu_list('5,1-3,2,19'), [1, 2, 3, 5, 19])
        self.assertEqual(parse_cpu_list(cpulist([1, 2, 6])), [1, 2, 6])
        with self.assertRaises(ValueError):
            parse_cpu_list('3-1')

    def test_plan_is_one_factor_at_time(self):
        cfg = load_config()
        node = choose_node()
        if len(node['physical_cpus']) < 3:
            self.skipTest('Not enough physical cores')
        plan = make_plan(cfg, ['Qwen/Qwen2.5-0.5B-Instruct'], None, None, 'auto')
        self.assertGreater(len(plan['runs']), 2)
        self.assertEqual(len({r['config_id'] for r in plan['runs']}), len(plan['runs']))
        baseline = plan['runs'][0]
        for r in plan['runs']:
            diffs = sum(r[k] != baseline[k] for k in ('cores', 'concurrency', 'output_tokens'))
            self.assertLessEqual(diffs, 1, r)
            self.assertEqual(r['numa_node'], node['node'])
            self.assertEqual(r['model'], baseline['model'])

    def test_runs_sorted_by_size_and_stable(self):
        cfg = load_config()
        first = make_plan(cfg, None, ['baseline'], None, 'auto')
        second = make_plan(cfg, None, ['baseline'], None, 'auto')
        self.assertEqual(first['plan_id'], second['plan_id'])
        self.assertEqual(len(first['runs']), 8)
        self.assertEqual([r['size_b'] for r in first['runs']], sorted(r['size_b'] for r in first['runs']))

    def test_docker_recipe_and_pin(self):
        cfg = load_config()
        cpus = {'infer': [3, 5], 'reserved': [7, 9], 'all': [3, 5, 7, 9]}
        run = {'model': 'Qwen/Qwen3-4B', 'recipe': True, 'numa_node': 2}
        from tempfile import TemporaryDirectory
        with TemporaryDirectory() as temp:
            path = Path(temp)
            command = docker_args(cfg, run, path, cpus, 'xeon6-bench-test', 6, path)
            joined = ' '.join(command)
            self.assertIn('--cpuset-cpus 3,5,7,9', joined)
            self.assertIn('--cpuset-mems 2', joined)
            self.assertIn('VLLM_CPU_OMP_THREADS_BIND=3,5', joined)
            self.assertIn('recipe_json_to_vllm_config.py', joined)
            self.assertIn('xeon6', joined)
            run['recipe'] = False
            command = docker_args(cfg, run, path, cpus, 'xeon6-bench-test2', 6, path)
            self.assertNotIn('recipe_json_to_vllm_config.py', ' '.join(command))


if __name__ == '__main__':
    unittest.main()
