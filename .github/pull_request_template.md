## Summary
- 

## Verification
- [ ] `uv run --extra dev ruff check src tests`
- [ ] `uv run --extra dev ruff format --check src tests`
- [ ] `uv run python -m compileall -q src tests`
- [ ] `uv run --extra dev pytest tests/ --cov=prompt_tool_regression_ci --cov-report=term-missing`

## Review Notes
- Are regression failures deterministic and reviewable?
- Are tool-call expectations explicit rather than hidden in prompt text?
- Are demo claims local-first and reproducible?
