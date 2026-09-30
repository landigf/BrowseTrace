#!/usr/bin/env python3
"""Replay only released BrowseTrace CSVs; no collection, API keys, or network.

Run from repository root: python tools/replay_public.py
Produces aggregate metrics and input hashes; never exports request URLs.
"""
from __future__ import annotations
import csv
import hashlib
import importlib.metadata
import json
import platform
import subprocess
from pathlib import Path
from libcachesim import ARC, GDSF, LFU, LRU, S3FIFO, WTinyLFU, ReaderInitParam, TraceReader, TraceType

ROOT = Path(__file__).resolve().parents[1]
POLICIES = [('LRU', LRU), ('LFU', LFU), ('ARC', ARC), ('S3-FIFO', S3FIFO), ('W-TinyLFU', WTinyLFU), ('GDSF', GDSF)]
SIZES = [1, 5, 10, 25, 50]

def main():
    params = ReaderInitParam(has_header=True, has_header_set=True, delimiter=',', obj_id_is_num=False, obj_id_is_num_set=True)
    params.time_field, params.obj_id_field, params.obj_size_field = 1, 2, 3
    result = {
        'schema_version': 1,
        'source_repository': 'https://github.com/landigf/BrowseTrace',
        'source_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
        'environment': {'python': platform.python_version(), 'libcachesim': importlib.metadata.version('libcachesim'), 'platform': platform.system(), 'machine': platform.machine()},
        'method': 'Cold cache per policy and size; replay each CSV in stored row order; default libCacheSim policy settings. Request hit ratio = 1 - miss ratio. Byte hit ratio = 1 - byte miss ratio. Cache capacity in MiB (1,048,576 bytes).',
        'limitations': [
            'Offline object-cache simulation; no network latency or live serving throughput is measured.',
            'Trace labels and collection provenance come from the released artifact; collection was not repeated.',
            'Two aggregate traces, not independent randomized trials or a human-control study.',
            'Full URL cache keys from released CSVs; no enforcement of origin HTTP cache-control, freshness, Vary, or authorization rules.',
            'Raw LLM session JSON is not bundled in this public release. Session IDs and replay rows can be checked; collection metadata cannot be independently reconstructed from CSVs alone.',
            'Policy differences are descriptive for this snapshot, not causal claims about LLM choice or deployment gains.'
        ],
        'workloads': [], 'results': []
    }
    for workload, relative in [('scripted', 'data/traces/full_400_sessions.csv'), ('llm', 'data/traces/llm_full_901.csv')]:
        path = ROOT / relative
        sessions = set()
        rows = 0
        with path.open(newline='') as handle:
            for row in csv.DictReader(handle):
                rows += 1
                if row.get('session_id'): sessions.add(row['session_id'])
        result['workloads'].append({'workload': workload, 'path': relative, 'sha256': hashlib.sha256(path.read_bytes()).hexdigest(), 'request_rows': rows, 'unique_session_ids': len(sessions)})
        for size in SIZES:
            for label, cls in POLICIES:
                reader = TraceReader(str(path), trace_type=TraceType.CSV_TRACE, reader_init_params=params)
                miss, byte_miss = cls(size * 1024 * 1024).process_trace(reader)
                result['results'].append({'workload': workload, 'cache_mib': size, 'policy': label, 'request_hit_ratio': 1 - miss, 'byte_hit_ratio': 1 - byte_miss})
    destination = ROOT / 'reports/public-cache-replay.json'
    destination.parent.mkdir(exist_ok=True)
    destination.write_text(json.dumps(result, indent=2) + '\n')
    print(destination.relative_to(ROOT))
    for row in result['results']:
        if row['cache_mib'] == 5 and row['policy'] in ['LRU', 'GDSF']:
            print(row)

if __name__ == '__main__': main()
