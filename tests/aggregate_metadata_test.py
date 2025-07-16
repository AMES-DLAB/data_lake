import sys
sys.path.insert(0,"scripts")

import json
import os
import pytest
import aggregate_metadata as am


def create_submodule(tmp_path, name, metadata):
    subdir = tmp_path / name
    subdir.mkdir()
    metadata_file = subdir / "metadata.json"
    metadata_file.write_text(json.dumps(metadata), encoding="utf-8")
    return subdir

def test_generate_metadata_basic(tmp_path, monkeypatch):
    # Prepare submodules directory
    sub1 = create_submodule(tmp_path, "alpha", {"a": 1})
    sub2 = create_submodule(tmp_path, "beta", {"b": [2, 3]})

    output = tmp_path / "all_metadata.json"

    # Run function under test
    am.generate_metadata(str(tmp_path), str(output))

    # Validate output exists and contents match expectations
    assert output.exists()
    data = json.loads(output.read_text(encoding="utf-8"))
    assert "alpha" in data and data["alpha"] == {"a": 1}
    assert "beta" in data and data["beta"] == {"b": [2, 3]}

def test_skip_invalid_json(tmp_path, capsys):
    sub = tmp_path / "invalid"
    sub.mkdir()
    bad = sub / "metadata.json"
    bad.write_text("not valid json", encoding="utf-8")

    output = tmp_path / "out.json"
    am.generate_metadata(str(tmp_path), str(output))

    captured = capsys.readouterr()
    assert "Error decoding JSON" in captured.out
    assert output.exists()
    data = json.loads(output.read_text(encoding="utf-8"))
    assert "invalid" not in data

def test_ignore_non_dirs(tmp_path):
    # Create file without metadata.json
    f = tmp_path / "random.txt"
    f.write_text("hello", encoding="utf-8")
    output = tmp_path / "om.json"
    am.generate_metadata(str(tmp_path), str(output))

    data = json.loads(output.read_text(encoding="utf-8"))
    assert data == {}

