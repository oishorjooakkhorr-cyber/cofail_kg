"""Researcher-authorized derived Nemotron-Nano-9B-v2 GGUF with thinking off by default.

The only change is one word in the embedded `tokenizer.chat_template`: the template's own default
`namespace(enable_thinking=true)` becomes `false`, so it emits its native `<think></think>` no-think
prefix. Tensors and every other metadata key are verified byte-identical to the source GGUF.
Ollama 0.40.12 cannot override an embedded jinja template, hence the copy. Writes the derived GGUF,
a Modelfile copying the source tag's Go template layer and stop parameters, and derivation.json.
"""
import hashlib
import json
from pathlib import Path
import sys

import gguf
from gguf.scripts.gguf_new_metadata import MetadataDetails, copy_with_new_metadata

OUT = Path(__file__).resolve().parent
SOURCE_TAG = "hf.co/bartowski/nvidia_NVIDIA-Nemotron-Nano-9B-v2-GGUF:Q4_K_M"
SOURCE_MANIFEST_DIGEST = "b1066467b580f048ef2b3f15890c78f3a1907c8a283f80c6933bc4836aa66ebe"
SOURCE_GGUF = Path(r"D:\Models\blobs\sha256-be84528231457f766a35612386e2638d9af10beb10a9d8d23f0cc73c20818da7")
SOURCE_GGUF_SHA256 = "be84528231457f766a35612386e2638d9af10beb10a9d8d23f0cc73c20818da7"
SOURCE_TEMPLATE_LAYER = Path(r"D:\Models\blobs\sha256-e50819c9c50e5c8f46ffbaf2bb5386fd2e0dacafacf9b124b672829eebc1a147")
SOURCE_PARAMS_LAYER = Path(r"D:\Models\blobs\sha256-72fd1b50d4daa93933017e7c414a9f4a2c6fd7f4f8fa949236fdda64314ce97e")
DERIVED_GGUF = Path(r"D:\cofailKG\.venv\nemotron-nothink\nemotron-nano-9b-v2-nothink-Q4_K_M.gguf")
DERIVED_TAG = "cofailkg/nemotron-nano-9b-v2-nothink:q4_k_m"
KEY = "tokenizer.chat_template"
OLD = "{%- set ns = namespace(enable_thinking=true) %}"
NEW = "{%- set ns = namespace(enable_thinking=false) %}"


def sha256_file(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 24), b""):
            digest.update(block)
    return digest.hexdigest()


def derive_template(template):
    if template.count(OLD) != 1:
        raise ValueError("Expected exactly one thinking-default declaration in the embedded template")
    return template.replace(OLD, NEW)


def field_value(reader, key):
    field = reader.get_field(key)
    return None if field is None else field.contents()


def compare(source, derived):
    """Every tensor and every metadata key except the chat template must be identical."""
    s_keys, d_keys = list(source.fields), list(derived.fields)
    # copy_with_new_metadata re-emits the changed key last; llama.cpp looks keys up by name.
    if sorted(k for k in s_keys if not k.startswith("GGUF.")) != sorted(k for k in d_keys if not k.startswith("GGUF.")):
        raise ValueError("Metadata key sets differ")
    if [k for k in s_keys if k != KEY] != [k for k in d_keys if k != KEY]:
        raise ValueError("Metadata key order differs beyond the changed key")
    for key in s_keys:
        if key.startswith("GGUF.") or key == KEY:
            continue
        if field_value(source, key) != field_value(derived, key):
            raise ValueError(f"Metadata differs: {key}")
    if len(source.tensors) != len(derived.tensors):
        raise ValueError("Tensor count differs")
    for a, b in zip(source.tensors, derived.tensors):
        if (a.name, a.tensor_type, list(a.shape)) != (b.name, b.tensor_type, list(b.shape)):
            raise ValueError(f"Tensor header differs: {a.name}")
        if hashlib.sha256(a.data.tobytes()).digest() != hashlib.sha256(b.data.tobytes()).digest():
            raise ValueError(f"Tensor data differs: {a.name}")
    return len(source.tensors)


def main():
    if sha256_file(SOURCE_GGUF) != SOURCE_GGUF_SHA256:
        raise ValueError("Source GGUF bytes differ from the installed blob digest")
    source = gguf.GGUFReader(SOURCE_GGUF, "r")
    original = field_value(source, KEY)
    derived_template = derive_template(original)
    if DERIVED_GGUF.exists():
        raise FileExistsError(f"Refusing to overwrite {DERIVED_GGUF}")
    DERIVED_GGUF.parent.mkdir(parents=True, exist_ok=True)
    arch = field_value(source, gguf.Keys.General.ARCHITECTURE)
    writer = gguf.GGUFWriter(DERIVED_GGUF, arch=arch, endianess=source.endianess)
    alignment = field_value(source, gguf.Keys.General.ALIGNMENT)
    if alignment is not None:
        writer.data_alignment = alignment
    copy_with_new_metadata(source, writer, {KEY: MetadataDetails(gguf.GGUFValueType.STRING, derived_template)}, [])
    derived = gguf.GGUFReader(DERIVED_GGUF, "r")
    if field_value(derived, KEY) != derived_template:
        raise ValueError("Derived chat template was not written")
    tensors = compare(source, derived)
    stops = json.loads(SOURCE_PARAMS_LAYER.read_text(encoding="utf-8"))["stop"]
    go_template = SOURCE_TEMPLATE_LAYER.read_text(encoding="utf-8")
    if '"""' in go_template:
        raise ValueError("Go template cannot be quoted in a Modelfile")
    modelfile = f'FROM {DERIVED_GGUF}\nTEMPLATE """{go_template}"""\n' + "".join(
        f"PARAMETER stop {json.dumps(s)}\n" for s in stops)
    (OUT / "Modelfile").write_text(modelfile, encoding="utf-8")
    (OUT / "template-original.jinja").write_text(original, encoding="utf-8")
    (OUT / "template-nothink.jinja").write_text(derived_template, encoding="utf-8")
    record = {"source_tag": SOURCE_TAG, "source_manifest_digest": SOURCE_MANIFEST_DIGEST,
              "source_gguf_sha256": SOURCE_GGUF_SHA256, "derived_gguf": str(DERIVED_GGUF),
              "derived_gguf_sha256": sha256_file(DERIVED_GGUF), "derived_tag": DERIVED_TAG,
              "gguf_package": "0.17.1", "changed_key": KEY, "old": OLD, "new": NEW,
              "original_template_sha256": hashlib.sha256(original.encode()).hexdigest(),
              "derived_template_sha256": hashlib.sha256(derived_template.encode()).hexdigest(),
              "tensors_verified_identical": tensors, "other_metadata_identical": True,
              "go_template_layer_sha256": hashlib.sha256(SOURCE_TEMPLATE_LAYER.read_bytes()).hexdigest(),
              "stop": stops}
    (OUT / "derivation.json").write_text(json.dumps(record, indent=2), encoding="utf-8")
    print(json.dumps(record, indent=2))


if __name__ == "__main__":
    sys.exit(main())
