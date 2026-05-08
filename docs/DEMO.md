# Demo

Run the dashboard locally:

```bash
uv run --extra dev prompt-tool-regression-ci
```

Open `http://127.0.0.1:8030`.

Suggested walkthrough:

1. Open the dashboard and point out the suite cards.
2. Select **Support Prompt Gate** and compare baseline vs candidate prompt rewrite.
3. Click **Run selected suite** to create a fresh local CI run from deterministic fixtures.
4. Open the changed shipping-delay result and explain the expected-vs-actual diff.
5. Switch to **Tool Planning Gate** and show the failed stale-policy tool call.
6. Explain how this kind of deterministic harness can run in CI before prompt/tool changes are merged.

## Run by API

```bash
curl -X POST http://127.0.0.1:8030/api/runs/execute \
  -H 'content-type: application/json' \
  -d '{"suite_id":"suite_support","label":"demo local execution"}'
```

The response includes the run summary plus the result diffs and mocked tool call records that were persisted to SQLite.

The demo is intentionally local and deterministic. It does not claim live LLM benchmarking or hosted provider integration.
