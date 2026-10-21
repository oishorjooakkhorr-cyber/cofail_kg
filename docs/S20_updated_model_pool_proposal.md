# S20 updated model shortlist (2026-10-19)

## Current status note — 2026-10-21

This is the historical October 19 proposal, not the current execution schedule.
Granite 4.1 is no longer deferred: its complete 8K block passes D3. Ministral 3,
OLMo 3 and Granite 4.2 have also completed their blocks and fail D3; they are no
longer pending preflights. Gemma and Qwen pass their separate complete 16K
reassessments, while Ministral still fails at 16K. See the
[complete status and all failure reasons](S20_screening_status.md).
The original proposal below is retained as dated history; pool/round accounting
and final S21 selection remain researcher decisions.

## Original proposal — 2026-10-19

Status: researcher endorsed the direction of using updated models at a similar
parameter scale. The exact list below is a proposal for review, not an S21 panel
selection or authorization to launch inference. Granite 4.1 testing was explicitly
deferred by the researcher. No model was downloaded or run for this review.

## Direction and comparison constraints

Researcher: "i think we should work with the updated models but similar parameter
size". Retain the previously accepted 7B-9B model class, the primary RTX 3060 Ti
8 GB host, native Ollama tool calls and think=false. Keep the existing frozen
S20 queries, P1/T1, evaluators and runtime settings. This proposal changes no
protocol, D3 threshold, frozen configuration or completed result.

Use advertised model size as the initial shortlist filter and record exact
installed parameter metadata before eligibility is decided. Multimodal packages
can include extra vision components: record those separately. Parameter count,
download size, loaded VRAM and active parameters are different quantities;
an MoE with 8B active parameters is not automatically in the same size class.

The aim is recent developer releases with plausible tool support and usable
local packaging. This is a researched initial shortlist, not a claim to enumerate
every current 7B-9B release or a ranking by biomedical performance.

## Initial shortlist

| Model | Class / family | Candidate Ollama tag | Evidence and remaining checks |
|---|---|---|---|
| Qwen3.5 9B | 9B / Qwen | `qwen3.5:9b` | Already screened: 20 outcomes, D3 PASS. Preserve the exact installed digest and accepted 32/33 GPU-layer placement; reuse is proposed only with unchanged frozen identities. Do not repull a moving tag over the completed model. |
| Ministral 3 8B Instruct | 8B / Mistral | `ministral-3:8b` | Registry advertises native tools; Q4_K_M, 8.92B metadata and about 6.0 GB download. Local tools, non-thinking behavior and context-8192 GPU fit remain untested. Recommended next preflight. |
| OLMo 3 7B Instruct | 7B / OLMo (Ai2) | `olmo-3:7b-instruct` | Developer separates Instruct and Think weights. Registry lists 7.3B Q4_K_M, about 4.5 GB, and tools for the family. Verify this exact Instruct tag locally; do not substitute the default or Think variant. Adds a fourth developer family. |
| Granite 4.2 8B | 8B / Granite | `granite4.2:8b` | Developer describes tools and configurable thinking. Registry lists 8.79B Q4_K_M, about 5.3 GB. The inspected tag page lacks an explicit tools badge, so native-tools eligibility is unresolved. Must pass /api/show and an unchanged-client synthetic check with think=false before official inference. |

Qwen's completed artifact is pinned at digest
`56671c2ab9385f9cfcb404638e32cd62d88e3501d44822208363c010179a3c90`.
The registry currently displays multiple backend artifacts for its tag; the
completed local Q4_K_M identity is the authority for these saved results. Model
family-wide marketing or default backend selection does not replace that pin.

## Fallback and other reviewed possibilities

**Granite 4.1 8B**, `ibm/granite4.1:8b`: same Granite family, registry tools badge,
8.79B Q4_K_M and about 5.3 GB. Appropriate fallback/additional candidate for local
preflight; the researcher plans to test it later. It does not add family diversity.
Prefer 4.2's recency only if the unchanged runtime can actually satisfy the
non-thinking/native-tools policy. Neither has a local eligibility result yet.

Other reviewed possibilities were not promoted into this initial shortlist:

- Qwen3-VL 8B Instruct has published tool packaging, but is an earlier generation
  within the already represented Qwen family. It offers less additional family
  diversity than OLMo for this first review.
- Nemotron Nano 9B v2 supports reasoning control and tools at the developer level,
  but uses a Mamba-Transformer hybrid architecture and documented /no_think
  signals. Compatibility with the unchanged P1 prompt, Ollama transport and
  native parser is unresolved; no custom prompt/template workaround is approved.
- GLM-4-9B-0414 has a developer tool example, but is an older 2025 release with
  unverified native Ollama packaging here. It is not evidence of a newest-model
  pool merely because the wider GLM family has newer large releases.

## Local eligibility before each new official block

Use the existing operational procedure: verify exact installed tag/digest,
parameter metadata, quantization, native tools, actual disabled-thinking
behavior and GPU placement at the unchanged context size. Use synthetic tools
before biomedical inference. Freeze the identity once accepted; retain the same
S20 generation settings, request timeout, one-episode invocations, hash checks,
stop conditions and write-once outcomes. Download size alone does not establish
full GPU residency. Model-author sampling recommendations do not replace the
frozen S20 settings.

No live eligibility, memory or latency claim is made for the new candidates.

## Researcher decisions before a revised official schedule

The project assigns scientific choices to the researcher. Confirm the exact
candidate membership, whether Granite 4.1 is an additional candidate or fallback,
and how the refreshed schedule replaces or defers the remaining older candidates.
Record whether it amends the initial pool or constitutes a D3 additional round;
D3 permits at most two more rounds. This document does not choose that accounting
or silently expand the allowed number of rounds.

The shortlist is not the final four-agent panel. D3 still requires four passing
models, maximizing developer-family diversity with at least three families,
then competence and latency tie-breaks. More eligible candidates may be needed;
do not fill four slots with models that fail D3.

All three completed candidate blocks remain in the official screening history:
Llama 3.1 8B FAIL, Granite 3.3 8B FAIL and Qwen3.5 9B PASS. Their 60 episodes and
three pinned configurations are retained unchanged. Do not delete failures,
relabel them as never planned, or rewrite the chronological original-pool
decisions. The latest recency preference is recorded after those outcomes were
seen and must be described as such. No old candidate is removed automatically
based on its observed score.

## Sources checked on 2026-10-19

- [Qwen3.5 9B developer card](https://huggingface.co/Qwen/Qwen3.5-9B) and
  [Ollama packaging](https://ollama.com/library/qwen3.5:9b).
- [Ministral 3 developer announcement](https://mistral.ai/news/mistral-3/) and
  [exact Ollama tag](https://ollama.com/library/ministral-3:8b).
- [OLMo 3 7B Instruct developer card](https://huggingface.co/allenai/Olmo-3-7B-Instruct)
  and [exact Ollama tag](https://ollama.com/library/olmo-3:7b-instruct).
- [Granite 4.2 developer documentation](https://www.ibm.com/granite/docs/models/granite4-2)
  and [exact Ollama tag](https://ollama.com/library/granite4.2:8b).
- [Granite 4.1 developer card](https://huggingface.co/ibm-granite/granite-4.1-8b)
  and [IBM's Ollama tag](https://ollama.com/ibm/granite4.1:8b).
- [Qwen3-VL 8B Instruct packaging](https://ollama.com/library/qwen3-vl:8b-instruct),
  [Nemotron developer card](https://huggingface.co/nvidia/NVIDIA-Nemotron-Nano-9B-v2),
  and [GLM developer card](https://huggingface.co/zai-org/GLM-4-9B-0414).

## Verification and design choices

This is a documentation-only planning update. Reviewed current developer/registry
sources, the frozen protocol section 9.1 and D3, and the existing decisions.
Verified all 63 saved run-file hashes, 122 protected identities and 43 pinned
source/input hashes after the update. No code/test/config/data, frozen rule,
metric or episode changed; no inference or model installation occurred.

Engineering choices: dated source links, exact candidate tag names, and explicit
separation of published capability from local eligibility. Proposed membership,
selection order and round accounting remain researcher choices. No automated
new scientific selection rule was introduced.
