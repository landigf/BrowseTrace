# Dataset card: BrowseTrace

## Identity and status

- **Curator:** Gennaro Francesco Landi
- **Canonical repository:** https://github.com/landigf/BrowseTrace
- **Code:** [Apache 2.0](LICENSE)
- **Released data:** [CC BY 4.0](LICENSE-DATA)
- **Status:** research artifact. The historical manuscript is not an accepted IMC publication.
- **Current evidence:** [September 2026 replay and input hashes](reports/public-cache-replay.json).

## Public snapshot scope

The repository contains browser collection code, task definitions, scripted release artifacts and two stitched cache-replay CSVs. The raw LLM session JSON bundles are not included in this snapshot.

| File | Request rows | Distinct nonempty session IDs |
|---|---:|---:|
| `data/traces/full_400_sessions.csv` | 82,455 | 400 |
| `data/traces/llm_full_901.csv` | 357,782 | 100 |

These counts were recomputed from the files. The legacy LLM filename is not a verified count of independent collection sessions. Labels can be reused across collections; the distinct-ID count does not reconstruct the missing session inventory. Historical claims of 901 LLM sessions, 1,301 total sessions and per-model amplification require evidence not supplied by these CSVs alone.

The workload labels are inherited from the release. The September recheck reruns offline simulation, not browser collection or model inference.

## Intended uses

- Compare object-cache policies on fixed request sequences.
- Inspect request-level schemas and the collection/release pipeline.
- Develop replay tooling with known, hashed inputs.

The scripted-random control is a reproducible driver, **not a human traffic baseline**. These traces do not establish deployment latency improvements, production cost savings, or population-level differences between humans and AI agents.

## Task definitions and collection background

[collection/tasks.yaml](collection/tasks.yaml) defines ten task families: API comparison, documentation lookup, fact checking, job market, literature review, news aggregation, product comparison, real estate, regulatory lookup and travel planning. Model configuration and browser orchestration live in [collection/runner.py](collection/runner.py).

The historical collection documentation describes local BrowserUse/macOS and cloud Playwright/Linux substrates. These environments differ; a geographic comparison is not automatically a controlled experiment. The current replay does not independently verify historical collection metadata or task completion.

## Formats

| File type | Purpose |
|---|---|
| `traces.json` | Full request context, response metadata, headers and timing |
| `access_log.jsonl` | Request log export |
| `cache_trace.csv` | Simulator projection |
| `summary.json` | Collection summaries and provenance where bundled |

See [schema/trace_schema.py](schema/trace_schema.py). Replay columns are `timestamp_us`, `cache_key`, `object_size_bytes`, `session_id`, `agent_type`.

## Sanitization and reuse

[tools/sanitize_release.py](tools/sanitize_release.py) implements removal of `Authorization`, `Cookie`, `Set-Cookie` and `Proxy-Authorization` headers, query-value redaction in full traces and access logs, and project-brand scrubbing.

The historical replay CSVs preserve full URL key uniqueness and are not query-redacted like the full trace exports. Do not assume a sanitization rule for one format applies to all formats. The new replay results and charts contain aggregate statistics and file hashes only, with no request URLs.

Collection should use public pages with appropriate access and rate limits. The release is not evidence of an institutional ethics determination or permission to collect arbitrary websites. No new collection was performed for this update.

## Evaluation protocol

[tools/replay_public.py](tools/replay_public.py) runs libCacheSim 0.3.3.post4, cold cache per policy and size, in stored CSV row order. It evaluates LRU, LFU, ARC, S3-FIFO, W-TinyLFU and GDSF at 1, 5, 10, 25 and 50 MiB. Request hit ratio is one minus request miss ratio; byte hit ratio is one minus byte miss ratio.

This is an object-cache simulation. It does not enforce origin HTTP cache-control, freshness, `Vary` or authorization, and does not measure live network latency. Differences between policies are descriptive for these two aggregate sequences. There are no independent randomized trials or confidence intervals in this replay.

See [README.md](README.md) for reproduction commands and the request-hit/byte-hit tradeoff. Plotting the committed results requires Matplotlib; recomputing the replay requires libCacheSim.

## Citation and contact

Use [CITATION.cff](CITATION.cff) to cite the artifact. Please report issues via [GitHub](https://github.com/landigf/BrowseTrace/issues). Historical manuscript citation fields should not be used to imply conference acceptance.
