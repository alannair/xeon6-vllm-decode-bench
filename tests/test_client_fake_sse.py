"""Actual HTTP/SSE integration test, without Docker or CPU PMU access."""
import asyncio
import csv
import json
import tempfile
from pathlib import Path
import unittest

try:
    from aiohttp import web
except ImportError:
    web = None

if web:
    from bench.client import run_measurement


@unittest.skipUnless(web is not None, 'aiohttp not installed (run pip install -r requirements.txt)')
class ClientSSETests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.prompts = []
        app = web.Application()
        app.router.add_post('/tokenize', self.tokenize)
        app.router.add_post('/v1/completions', self.completions)
        app.router.add_get('/metrics', self.metrics)
        async def health(request):
            return web.Response(text='ok')
        app.router.add_get('/health', health)
        self.runner = web.AppRunner(app)
        await self.runner.setup()
        self.site = web.TCPSite(self.runner, '127.0.0.1', 0)
        await self.site.start()
        self.url = f'http://127.0.0.1:{self.site._server.sockets[0].getsockname()[1]}'

    async def asyncTearDown(self):
        await self.runner.cleanup()
        self.temp.cleanup()

    async def tokenize(self, request):
        data = await request.json()
        self.assertEqual(data['model'], 'test-model')
        return web.json_response({'tokens': list(range(256))})

    async def metrics(self, request):
        return web.Response(text='''# TYPE vllm:num_requests_running gauge
vllm:num_requests_running{model="test"} 2
vllm:num_requests_waiting{model="test"} 1
vllm:generation_tokens_total 100
''', content_type='text/plain')

    async def completions(self, request):
        body = await request.json()
        self.prompts.append(body)
        self.assertEqual(len(body['prompt']), 32)
        self.assertEqual(body['min_tokens'], body['max_tokens'])
        self.assertTrue(body['ignore_eos'])
        self.assertTrue(body['return_token_ids'])
        self.assertTrue(body['stream'])
        n = body['max_tokens']
        response = web.StreamResponse(status=200, headers={'Content-Type': 'text/event-stream'})
        await response.prepare(request)
        try:
            # First 2 tokens in a single chunk: our token CSV must expose this coalescing.
            remaining = n
            while remaining:
                count = min(2, remaining)
                remaining -= count
                blob = {'choices': [{'index': 0, 'text': 'xx', 'token_ids': list(range(count)),
                                     'finish_reason': 'length' if remaining == 0 else None}]}
                await response.write(f'data: {json.dumps(blob)}\n\n'.encode())
                await asyncio.sleep(.008)
            await response.write(f'data: {json.dumps({"usage": {"completion_tokens": n}, "choices": []})}\n\n'.encode())
            await response.write(b'data: [DONE]\n\n')
        except ConnectionResetError:
            pass
        return response

    async def test_streaming_logs(self):
        summary = await run_measurement(
            self.url, 'test-model', self.root, self.root,
            concurrency=2, output_tokens=6, prompt_tokens=32,
            duration_s=1, drain_s=0.2, request_timeout_s=5,
            warmup_requests=1, warmup_output_tokens=4,
            metrics_interval_s=.10, storage_interval_s=.10,
            storage_min_free_gib=0, stopped=lambda: False)
        with (self.root/'requests.csv').open() as f:
            reqs = list(csv.DictReader(f))
        with (self.root/'token_events.csv').open() as f:
            tokens = list(csv.DictReader(f))
        with (self.root/'metrics.csv').open() as f:
            metrics = list(csv.DictReader(f))
        self.assertGreater(len(reqs), 5)
        self.assertGreater(len(tokens), 10)
        self.assertGreater(len(metrics), 3)
        self.assertTrue(all(int(r['prompt_tokens']) == 32 for r in reqs))
        self.assertTrue(all(int(r['tokens_within_window']) <= int(r['output_tokens']) for r in reqs))
        self.assertTrue(any(t['index_in_chunk'] == '1' for t in tokens))
        self.assertEqual(float(metrics[0]['num_requests_waiting']), 1)
        self.assertEqual(summary['finished_request_records'], len(reqs))
        self.assertGreater(summary['delivered_tokens_per_s'], 1)
        self.assertGreater(summary['mean_tpot_median_s'], 0)
        self.assertTrue(all(p['min_tokens'] == p['max_tokens'] for p in self.prompts))


if __name__ == '__main__':
    unittest.main()
