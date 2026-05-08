# Architecture

Prompt/Tool Regression CI is a local-first application with deterministic fixtures, a typed FastAPI surface, and a static dashboard served by the backend.

```mermaid
flowchart TB
    subgraph Authoring[Regression Authoring]
        Prompt[Prompt behavior cases]
        Policy[Safety policies]
        ToolExpect[Expected tool inputs and outputs]
    end
    subgraph Persistence[SQLite Demo Store]
        Suites[(suites)]
        Cases[(cases)]
        Runs[(runs)]
        Results[(results and diffs)]
        ToolCalls[(tool calls)]
    end
    subgraph Service[FastAPI Service]
        Summary[/api/summary]
        SuiteAPI[/api/suites]
        RunAPI[/api/runs]
        Reset[/api/demo/reset]
    end
    subgraph Operator[Review Surface]
        UI[Dashboard]
        Diff[Expected vs actual diff cards]
        Gate[CI gate summary]
    end
    Prompt --> Cases
    Policy --> Cases
    ToolExpect --> Cases
    Cases --> Suites
    Suites --> Summary
    Runs --> RunAPI
    Results --> Diff
    ToolCalls --> Diff
    Summary --> UI
    SuiteAPI --> UI
    RunAPI --> UI
    Reset -. reseeds .-> Suites
    UI --> Gate
    classDef author fill:#1d2437,stroke:#f8d36b,color:#fff;
    classDef data fill:#102b3f,stroke:#59e0ff,color:#fff;
    classDef api fill:#12321f,stroke:#7dffb2,color:#fff;
    classDef review fill:#321b1f,stroke:#ff6b7a,color:#fff;
    class Prompt,Policy,ToolExpect author;
    class Suites,Cases,Runs,Results,ToolCalls data;
    class Summary,SuiteAPI,RunAPI,Reset api;
    class UI,Diff,Gate review;
```

## Boundaries

- Tool calls are mocked deterministic records, not live external integrations.
- Regression diffs are stored as structured data so reviewers can inspect why a candidate prompt changed behavior.
- The CI workflow validates code quality and tests, while the application models what a prompt/tool behavior gate would expose.
