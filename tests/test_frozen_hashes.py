import pytest

from cofail_kg.utils.frozen_hashes import FrozenHashConflict, read_frozen_hashes, write_once


def test_creates_file(tmp_path):
    p = tmp_path / "configs" / "frozen_hashes.yaml"
    assert read_frozen_hashes(p) == {}
    assert write_once(p, "biohopr_revision", "abc") is True
    assert read_frozen_hashes(p) == {"biohopr_revision": "abc"}
    assert p.read_text(encoding="utf-8").startswith("# Frozen hashes")


def test_same_value_is_noop(tmp_path):
    p = tmp_path / "f.yaml"
    write_once(p, "k", "v")
    before = p.read_bytes()
    assert write_once(p, "k", "v") is False
    assert p.read_bytes() == before


def test_different_value_raises(tmp_path):
    p = tmp_path / "f.yaml"
    write_once(p, "k", "v")
    with pytest.raises(FrozenHashConflict):
        write_once(p, "k", "w")
    assert read_frozen_hashes(p) == {"k": "v"}


def test_other_keys_preserved_sorted(tmp_path):
    p = tmp_path / "f.yaml"
    write_once(p, "z_key", "1")
    write_once(p, "a_key", "2")
    assert read_frozen_hashes(p) == {"a_key": "2", "z_key": "1"}
    body = p.read_text(encoding="utf-8")
    assert body.index("a_key") < body.index("z_key")
