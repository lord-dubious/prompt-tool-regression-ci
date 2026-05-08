# Demo

Run the dashboard locally:

```bash
uv run --extra dev prompt-tool-regression-ci
```

Open `http://127.0.0.1:8030`.

Suggested walkthrough:

1. Open the dashboard and point out the suite cards.
2. Select **Support Prompt Gate** and compare baseline vs candidate prompt rewrite.
3. Open the changed shipping-delay result and explain the expected-vs-actual diff.
4. Switch to **Tool Planning Gate** and show the failed stale-policy tool call.
5. Explain how this kind of deterministic harness can run in CI before prompt/tool changes are merged.

The demo is intentionally local and deterministic. It does not claim live LLM benchmarking or hosted provider integration.
