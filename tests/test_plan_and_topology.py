import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import mock

from bench.plan import make_plan, load_config
from bench.topology import cpulist, parse_cpu_list, select_cores, contiguous_node0_cores
from bench.runner import docker_args

NODE0 = {'node': 0, 'socket': 0, 'physical_cpus': list(range(96)),
         'logical_cpus': list(range(96)), 'memory_gib': 384}


class PlanningTests(unittest.TestCase):
    def test_cpu_lists(self):
        self.assertEqual(parse_cpu_list('5,1-3,2,19'), [1, 2, 3, 5, 19])
        self.assertEqual(parse_cpu_list(cpulist([1, 2, 6])), [1, 2, 6])
        with self.assertRaises(ValueError):
            parse_cpu_list('3-1')

    def test_baseline_and_one_factor_sweeps(self):
        cfg = load_config()
        with mock.patch('bench.plan.choose_node', return_value=NODE0):
            plan = make_plan(cfg, ['Qwen/Qwen2.5-0.5B-Instruct'])
        self.assertGreater(len(plan['runs']), 2)
        self.assertEqual(plan['runs'][0]['cores'], 96)
        self.assertEqual({r['cores'] for r in plan['runs']}, {24, 48, 72, 96})
        self.assertEqual(len({r['config_id'] for r in plan['runs']}), len(plan['runs']))
        base = plan['runs'][0]
        for r in plan['runs']:
            diffs = sum(r[k] != base[k] for k in ('cores', 'concurrency', 'output_tokens'))
            self.assertLessEqual(diffs, 1)
            self.assertEqual(r['numa_node'], 0)

    def test_plan_stability_and_model_sizes(self):
        cfg = load_config()
        with mock.patch('bench.plan.choose_node', return_value=NODE0):
            first = make_plan(cfg, None, ['baseline'])
            second = make_plan(cfg, None, ['baseline'])
        self.assertEqual(first['plan_id'], second['plan_id'])
        self.assertEqual(len(first['runs']), 8)
        self.assertTrue(all(r['cores'] == 96 for r in first['runs']))
        self.assertEqual([r['size_b'] for r in first['runs']],
                         sorted(r['size_b'] for r in first['runs']))

    def test_max_model_size_drops_larger_models(self):
        cfg = load_config()
        cfg["max_model_size_b"] = 33
        cfg["models"] = list(cfg["models"]) + [
            {"id": "meta-llama/Llama-3.3-70B-Instruct", "size_b": 70.0, "recipe": True}]
        with mock.patch('bench.plan.choose_node', return_value=NODE0):
            plan = make_plan(cfg, None, ['baseline'])
        self.assertEqual(len(plan['runs']), 8)
        self.assertNotIn('meta-llama/Llama-3.3-70B-Instruct', plan['models'])

    def test_queue_order_overrides_size_order(self):
        cfg = load_config()
        cfg["models"] = [
            {"id": "a/small", "size_b": 1.0, "queue_order": 2},
            {"id": "b/large", "size_b": 30.0, "queue_order": 1},
            {"id": "c/mid", "size_b": 8.0, "queue_order": 3},
        ]
        with mock.patch('bench.plan.choose_node', return_value=NODE0):
            plan = make_plan(cfg, None, ['baseline'])
        self.assertEqual(plan['models'], ['b/large', 'a/small', 'c/mid'])
        self.assertEqual([r['queue_order'] for r in plan['runs']], [1, 2, 3])
        cfg["models"][0].pop("queue_order")
        with mock.patch('bench.plan.choose_node', return_value=NODE0):
            plan = make_plan(cfg, None, ['baseline'])
        self.assertEqual(plan['models'], ['a/small', 'c/mid', 'b/large'])

    def test_strict_node0_baseline(self):
        cfg = load_config()
        fewer = {**NODE0, 'physical_cpus': list(range(72)), 'logical_cpus': list(range(72))}
        with mock.patch('bench.plan.choose_node', return_value=fewer):
            with self.assertRaisesRegex(RuntimeError, 'not silently shrink'):
                make_plan(cfg)
        with mock.patch('bench.plan.choose_node', return_value=NODE0):
            with self.assertRaisesRegex(ValueError, 'node 0'):
                make_plan(cfg, node_override='1')
        gap = {**NODE0, 'physical_cpus': [i for i in range(96) if i != 52]}
        self.assertEqual(contiguous_node0_cores(gap), 52)

    def test_exact_server_cpus_and_mem(self):
        cfg = load_config()
        with TemporaryDirectory() as tmp:
            for n in (24, 48, 72, 96):
                cpus = select_cores(NODE0, n, 2, contiguous_from_zero=True)
                self.assertEqual(cpus['infer'], list(range(n)))
                self.assertEqual(cpus['all'], list(range(n)))
                self.assertFalse(set(cpus['reserved']) & set(cpus['infer']))
                run = {'model': 'Qwen/Qwen3-4B', 'recipe': True, 'numa_node': 0}
                cmd = docker_args(cfg, run, Path(tmp), cpus, 'xeon6-bench-test', 6, Path(tmp))
                self.assertEqual(cmd[cmd.index('--cpuset-mems')+1], '0')
                self.assertEqual(parse_cpu_list(cmd[cmd.index('--cpuset-cpus')+1]), list(range(n)))
                joined = ' '.join(cmd)
                self.assertIn(f'OMP_NUM_THREADS={n}', joined)
                self.assertIn(f'--physcpubind=0-{n - 1}', joined)
                self.assertIn('--numa-bind', joined)
                self.assertIn(f'--numa-bind-cpus 0-{n - 1}', joined)
                self.assertIn('--membind=0', joined)
                self.assertNotIn('KMP_AFFINITY=', joined)
                self.assertNotIn('OMP_PLACES=cores', joined)
                self.assertIn('recipe_json_to_vllm_config.py', joined)
                run['recipe'] = False
                cmd = docker_args(cfg, run, Path(tmp), cpus, 'xeon6-bench-test2', 6, Path(tmp))
                self.assertNotIn('recipe_json_to_vllm_config.py', ' '.join(cmd))
            with self.assertRaisesRegex(ValueError, 'node 0'):
                docker_args(cfg, {'model': 'x', 'recipe': False, 'numa_node': 1},
                            Path(tmp), cpus, 'xeon6-bench-bad', 4, Path(tmp))


if __name__ == '__main__':
    unittest.main()
