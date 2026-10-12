# CoFail-KG

CoFail-KG is a research project studying co-failure of independent local LLM agents answering multi-hop biomedical questions over a knowledge graph (PrimeKG, with questions from BioHopR). See `docs/` for the frozen protocol, decision rules, pipeline runbook, and progress log.

## Reproduce

### Python

- Tested on **Python 3.14.7** (Windows 11).
- S4 partial implementation also verified on **Python 3.13.7** (Windows).
- Supported: **Python >= 3.12** (`requires-python` in `pyproject.toml`). The pinned dependencies in
  `requirements.lock` need 3.12 or newer, and networkx 3.7 does not install on Python 3.14.1
  specifically.

### Setup

From the repository root:

```bash
python -m venv venv
# Windows (PowerShell):  venv\Scripts\Activate.ps1
# Linux / macOS:         source venv/bin/activate
python -m pip install -r requirements.lock
python -m pip install -e .
```

`requirements.lock` holds the exact versions the tests were run with. `requirements.txt` lists
the same packages without versions; use it only if you deliberately want newer versions.

### Run the tests

```bash
python -m pytest -q
```

- One test checks the real BioHopR file and skips until it has been downloaded (next section).
- S4 unit tests use tiny synthetic graphs and do not require the full PrimeKG download.

### Get the data

Downloaded data is not in git (`data/raw/` and `data/cache/` are gitignored).

**BioHopR** (needs internet access to the Hugging Face Hub):

```bash
python scripts/02_download_biohopr.py
```

This downloads `BioHopR.json` and the dataset card from `knowlab-research/BioHopR` at the pinned
revision `08f06692c3900347e7405ba55ff6a6d330f55ddb` into `data/raw/biohopr/`. It checks every file
against the Hub's SHA256, writes `data/raw/biohopr/metadata.json`, and refuses to overwrite files
that differ. The pinned revision is also recorded in `configs/frozen_hashes.yaml`.

**PrimeKG (S4 partial implementation)**: place `kg.csv` and `nodes.csv` from the downloaded
PrimeKG archive into `data/raw/primekg/`. The current inputs are from Harvard Dataverse,
DOI `10.7910/DVN/IXA7BM`; the existing release record names v2.1. Keep release details in
`data/cache/primekg_release.json` separately from machine-written cache metadata.

```bash
python scripts/04_prepare_primekg.py
python scripts/inspect_kg.py node "Troglitazone"
python scripts/inspect_kg.py relations 14813
python scripts/inspect_kg.py neighbors 14813 --relation drug_effect
```

Preparation hashes every raw input, verifies endpoint metadata, and creates node/edge Parquet
tables plus deterministic metadata. Reruns verify the existing cache and refuse changed inputs.
The inspection CLI returns complete JSON and writes load timing to stderr. Name lookup trims
surrounding whitespace and collapses internal whitespace, following the researcher's S4 decision.

S4 protocol confirmation is pending: use `--freeze` on the preparation command only after that
confirmation, to record `kg_fingerprint` in `configs/frozen_hashes.yaml`. See
`docs/S4_implementation.md` for results and the remaining items. Troglitazone has 17 direct
side-effect neighbours; the older runbook's 202 check still awaits correction.

### Regenerate results

Stages are named S0, S1, … as in `docs/pipeline_runbook.md`; `docs/progress.md` shows which are
complete. Scripts are numbered by stage and run from the repository root.

| Stage | Command | Output |
|---|---|---|
| S2 | `python scripts/02_download_biohopr.py` | `data/raw/biohopr/` (not in git) |
| S2 | `python scripts/02_inspect_biohopr.py` | `results/diagnostics/biohopr/inspection_20.md`, `hop1_in_question.csv` |
| S3 | `python scripts/03_biohopr_diagnostics.py` | `results/diagnostics/biohopr/` |
| S4 | `python scripts/04_prepare_primekg.py` | PrimeKG cache and metadata under `data/cache/` (not in git) |

The S2 inspection outputs are committed. After running the script, `git diff` should be empty.

## Contribute / extend

- **Code** lives in the `cofail_kg` package under `src/cofail_kg/` (`data/`, `kg/`, `agents/`,
  `evaluation/`, `analysis/`, `utils/`). Stage entry-point scripts go in `scripts/`, named with
  the stage number.
- **Configs** go in `configs/`. `configs/frozen_hashes.yaml` is written by code only, once per
  entry; never edit it by hand.
- **Tests**: every new module needs tests in `tests/`. Unit tests use tiny synthetic fixtures,
  not the full datasets.
- **Rules**: scientific rules come from `docs/frozen_pilot_protocol.md` and gates from
  `docs/decision_rules.md`; code cites protocol section numbers. `CLAUDE.md` lists the working
  rules for this repository (reproducibility, checkpointing, data handling).

## Data credits

- **BioHopR** — multi-hop biomedical question benchmark, Hugging Face dataset
  `knowlab-research/BioHopR`. Its dataset card declares the **MIT** license. This repository does
  not redistribute the dataset, but `results/diagnostics/biohopr/` quotes a sample of its rows.
- **PrimeKG** — the biomedical knowledge graph that BioHopR is built from and that the agents will
  query. The S4 input source is Harvard Dataverse, DOI `10.7910/DVN/IXA7BM`; raw data and cached
  tables are not redistributed by this repository. Source license terms remain to be recorded.
