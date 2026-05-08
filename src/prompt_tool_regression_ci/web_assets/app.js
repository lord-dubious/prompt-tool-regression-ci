const state = { suites: [], runs: [], activeSuite: null, activeRun: null };

const statusPill = (status) => `<span class="status ${status}">${status}</span>`;

async function json(path, options = {}) {
  const response = await fetch(path, options);
  if (!response.ok) throw new Error(`Request failed: ${response.status}`);
  return response.json();
}

function renderMetrics(summary) {
  document.querySelector('#metrics').innerHTML = [
    ['Suites', summary.suite_count], ['Cases', summary.case_count], ['Runs', summary.run_count], ['Passing', summary.passing_runs], ['Failing', summary.failing_runs], ['Changed', summary.changed_results]
  ].map(([label, value]) => `<article class="metric"><strong>${value}</strong><span>${label}</span></article>`).join('');
  document.querySelector('#gate-score').textContent = summary.changed_results;
  document.querySelector('#hero-title').textContent = `${summary.run_count} deterministic CI runs`;
  document.querySelector('#hero-copy').textContent = 'Review prompt diffs, tool expectations, and failing gates before deployment.';
}

function renderSuites() {
  document.querySelector('#suite-list').innerHTML = state.suites.map((suite) => `<article class="suite-card ${suite.id === state.activeSuite ? 'active' : ''}" data-suite="${suite.id}"><strong>${suite.name}</strong><p>${suite.description}</p></article>`).join('');
  document.querySelectorAll('[data-suite]').forEach((node) => node.addEventListener('click', () => selectSuite(node.dataset.suite)));
}

async function selectSuite(suiteId) {
  state.activeSuite = suiteId;
  const detail = await json(`/api/suites/${suiteId}`);
  state.runs = detail.runs;
  renderSuites();
  renderRuns();
  if (detail.runs[0]) await selectRun(detail.runs[0].id);
}

function renderRuns() {
  document.querySelector('#run-list').innerHTML = state.runs.map((run) => `<article class="run-card ${run.id === state.activeRun ? 'active' : ''}" data-run="${run.id}"><strong>${run.label}</strong><p>${run.passed} passed · ${run.failed} failed · ${run.changed} changed</p>${statusPill(run.status)}</article>`).join('');
  document.querySelectorAll('[data-run]').forEach((node) => node.addEventListener('click', () => selectRun(node.dataset.run)));
}

async function selectRun(runId) {
  state.activeRun = runId;
  renderRuns();
  const detail = await json(`/api/runs/${runId}`);
  document.querySelector('#detail-title').textContent = detail.run.label;
  document.querySelector('#detail-status').textContent = detail.run.status;
  document.querySelector('#result-list').innerHTML = detail.results.map((result) => `<article class="result-card"><h4>${result.case_id}</h4>${statusPill(result.status)}<p>${result.actual_response}</p>${result.diff ? `<div class="diff"><strong>${result.diff.reason}</strong><br>Expected: ${result.diff.expected}<br>Actual: ${result.diff.actual}</div>` : ''}<div class="tools">${result.tool_calls.map((tool) => `<span class="tool">${tool.tool_name}:${tool.status}</span>`).join('')}</div></article>`).join('');
}

async function load() {
  const [summary, suites] = await Promise.all([json('/api/summary'), json('/api/suites')]);
  state.suites = suites;
  renderMetrics(summary);
  if (!state.activeSuite && suites[0]) state.activeSuite = suites[0].id;
  renderSuites();
  if (state.activeSuite) await selectSuite(state.activeSuite);
}

document.querySelector('#reset-btn').addEventListener('click', async () => { await json('/api/demo/reset', { method: 'POST' }); await load(); });
load().catch((error) => { document.querySelector('#hero-title').textContent = 'Dashboard failed to load'; document.querySelector('#hero-copy').textContent = error.message; });
