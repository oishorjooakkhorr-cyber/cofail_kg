"""Write the derived tag's Ollama manifest with exactly the source tag's structure.

`ollama create` auto-assigns Ollama's built-in `nemotron-3-nano` renderer/parser to any nemotron_h
GGUF, which renders ChatML instead of the model's embedded jinja template. The pulled source tag has no
renderer/parser, so llama-server applies the embedded template. This copies the source manifest and
config, replacing only the model layer (the derived GGUF) and its diff_id.
"""
import hashlib
import json
from pathlib import Path

OUT = Path(__file__).resolve().parent
MODELS = Path(r"D:\Models")
SOURCE = MODELS / "manifests-v2/hf.co/bartowski/nvidia_NVIDIA-Nemotron-Nano-9B-v2-GGUF/Q4_K_M"
TARGET = MODELS / "manifests-v2/ollama.com/cofailkg/nemotron-nano-9b-v2-nothink/q4_k_m"
OLD_LAYER = "sha256:be84528231457f766a35612386e2638d9af10beb10a9d8d23f0cc73c20818da7"


def blob(digest):
    return MODELS / "blobs" / digest.replace(":", "-")


def main():
    derivation = json.loads((OUT / "derivation.json").read_text(encoding="utf-8"))
    new_layer = "sha256:" + derivation["derived_gguf_sha256"]
    assert blob(new_layer).stat().st_size == blob(OLD_LAYER).stat().st_size
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
