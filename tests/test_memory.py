import json
from aeris.memory.persistent import PersistentMemory


def test_persistent_memory_creation(tmp_path):
    filepath = tmp_path / "memory.json"
    mem = PersistentMemory(str(filepath))

    # Should create the file
    assert filepath.exists()

    # Add data
    mem.add_fact("User is a developer.")
    mem.add_summary("Session 1: Wrote some tests.")

    # Verify save
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
        assert "User is a developer." in data["facts"]
        assert "Session 1: Wrote some tests." in data["summaries"]


def test_persistent_memory_loading(tmp_path):
    filepath = tmp_path / "memory.json"

    # Pre-populate data
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump({"facts": ["Fact 1"], "summaries": ["Summary 1"]}, f)

    mem = PersistentMemory(str(filepath))

    context = mem.get_context_string()
    assert "Fact 1" in context
    assert "Summary 1" in context


def test_persistent_memory_corrupted(tmp_path):
    filepath = tmp_path / "memory.json"

    # Write invalid JSON
    with open(filepath, "w", encoding="utf-8") as f:
        f.write("{ invalid json")

    # Should not crash, should start fresh
    mem = PersistentMemory(str(filepath))

    # After adding a fact, it should overwrite the corrupted file with valid JSON
    mem.add_fact("New fact")

    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
        assert data["facts"] == ["New fact"]


def test_memory_isolation_between_instances(tmp_path):
    filepath_1 = tmp_path / "memory1.json"
    filepath_2 = tmp_path / "memory2.json"

    mem1 = PersistentMemory(str(filepath_1))
    mem2 = PersistentMemory(str(filepath_2))

    mem1.add_fact("User1 likes Python")
    mem2.add_fact("User2 likes Rust")

    context1 = mem1.get_context_string()
    context2 = mem2.get_context_string()

    assert "User1 likes Python" in context1
    assert "User2 likes Rust" not in context1

    assert "User2 likes Rust" in context2
    assert "User1 likes Python" not in context2
