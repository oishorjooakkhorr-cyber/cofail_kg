# Repository navigation graph

Open `graph.html` in a browser to inspect the committed graph. Its graph data is embedded;
the visualization library loads from unpkg.com, so viewing requires internet access.
`graph.json` also supports Graphify's local query and path commands.

This is a navigation aid for project code and documentation, not the biomedical PrimeKG.
Historical reports remain in the graph. For the current S6 decision, consult the newest
entry in `docs/decision_log.md` and `results/semantics/relation_mapping.json`.

## Rebuild from a checkout

The refresh was verified with Python 3.13 and `graphifyy` 0.9.64. Install the CLI in an
isolated tool environment, for example with `uv tool install graphifyy==0.9.64`.
Run these commands from the repository root, using the project's Python environment:

```powershell
graphify update . --no-cluster
python graphify-out/include_documentation.py
graphify cluster-only . --no-label
```

The first command refreshes code symbols locally. The second regenerates documentation
sections and explicit links from README, CLAUDE.md, docs, results/diagnostics and
results/semantics, retaining the code graph. The last regenerates communities, the report
and HTML. These commands do not require an LLM API key or send the corpus to an LLM.
Community names remain generic `Community N` labels.

Commit the generated `graph.json`, `graph.html`, `GRAPH_REPORT.md`,
`.graphify_analysis.json` and `documentation-extraction.json`, together with any changed
extraction script. The portable `.graphify_root` marker contains `.`. The cache and manifest
are local generated state, ignored by Git; a fresh checkout regenerates them.

`GRAPH_REPORT.md` records the source HEAD at generation time. The following commit that
stores the generated artifacts naturally has a different ID; compare changes since the
recorded source commit to distinguish artifact-only changes from new source changes.

To check navigation:

```powershell
graphify query "relation mapping" --budget 1000
```

The full graph is structural code extraction plus deterministic document links. It does
not claim exhaustive semantic interpretation or replace the frozen scientific protocol.
