"""Write the derived tag's Ollama manifest with exactly the source tag's structure.

`ollama create` auto-assigns Ollama's built-in `nemotron-3-nano` renderer/parser to any nemotron_h
GGUF, which renders ChatML instead of the model's embedded jinja template. The pulled source tag has no
renderer/parser, so llama-server applies the embedded template. This copies the source manifest and
config, replacing only the model layer (the derived GGUF) and its diff_id.
"""
import hashlib
import json
from pathlib import Path
import shutil

OUT = Path(__file__).resolve().parent
MODELS = Path(r"D:\Models")
SOURCE = MODELS / "manifests-v2/hf.co/MaziyarPanahi/NVIDIA-Nemotron-Nano-12B-v2-GGUF/Q4_K_M"
TARGET = MODELS / "manifests-v2/ollama.com/cofailkg/nemotron-nano-12b-v2-nothink/q4_k_m"
OLD_LAYER = "sha256:a32e35e74fedf50915ee0b451f9cccebc030e6934f7c197e23bdb06443128586"


def sha256_file(path):
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for block in iter(lambda: handle.read(1 << 24), b""):
            digest.update(block)
    return digest.hexdigest()


def blob(digest):
    return MODELS / "blobs" / digest.replace(":", "-")


def main():
    derivation = json.loads((OUT / "derivation.json").read_text(encoding="utf-8"))
    new_layer = "sha256:" + derivation["derived_gguf_sha256"]
    # 12B: no `ollama create` attempt was made, so place the derived GGUF in the blob store under its own
    # SHA-256 name (what `ollama create` would do) and verify the copied bytes.
    if not blob(new_layer).exists():
        shutil.copyfile(derivation["derived_gguf"], blob(new_layer))
    assert sha256_file(blob(new_layer)) == derivation["derived_gguf_sha256"], "Copied blob bytes differ"
    # 12B: "false" is one byte longer than "true", which here crosses a 32-byte GGUF alignment boundary, so
    # the derived file is 32 bytes larger (9B: same size). derive_model.py verified every tensor identical.
    new_size = blob(new_layer).stat().st_size
    assert 0 <= new_size - blob(OLD_LAYER).stat().st_size <= 32, "Derived size differs beyond one alignment step"
    manifest = json.loads(SOURCE.read_text(encoding="utf-8"))
    config = json.loads(blob(manifest["config"]["digest"]).read_bytes())
    assert config["rootfs"]["diff_ids"].count(OLD_LAYER) == 1 and "renderer" not in config
    config["rootfs"]["diff_ids"] = [new_layer if d == OLD_LAYER else d for d in config["rootfs"]["diff_ids"]]
    config_bytes = json.dumps(config, separators=(",", ":")).encode()
    config_digest = "sha256:" + hashlib.sha256(config_bytes).hexdigest()
    if not blob(config_digest).exists():
        blob(config_digest).write_bytes(config_bytes)
    manifest["config"] = {**manifest["config"], "digest": config_digest, "size": len(config_bytes)}
    layers = [l for l in manifest["layers"] if l["digest"] == OLD_LAYER]
    assert len(layers) == 1
    layers[0]["digest"] = new_layer
    layers[0]["size"] = new_size
    if TARGET.exists():  # Auto-created manifest with the wrong renderer; keep a copy as evidence.
        (OUT / "auto-created-manifest.json").write_bytes(TARGET.read_bytes())
    TARGET.parent.mkdir(parents=True, exist_ok=True)
    TARGET.write_text(json.dumps(manifest, separators=(",", ":")), encoding="utf-8")
    record = {"manifest": str(TARGET), "manifest_sha256": hashlib.sha256(TARGET.read_bytes()).hexdigest(),
              "config_digest": config_digest, "config": config, "layers": manifest["layers"]}
    (OUT / "manifest-record.json").write_text(json.dumps(record, indent=2), encoding="utf-8")
    print(json.dumps(record, indent=2))


if __name__ == "__main__":
    main()
