from __future__ import annotations

from weaponassambly._mapping import sorted_dict_copy


def test_sorted_dict_copy_fast_path_preserves_empty_and_single_item_dicts():
    assert sorted_dict_copy({}) == {}
    assert list(sorted_dict_copy({"only": 1})) == ["only"]


def test_sorted_dict_copy_sorts_multi_item_dicts_deterministically():
    result = sorted_dict_copy({"z": 3, "a": 1, "m": 2})

    assert list(result) == ["a", "m", "z"]
    assert result == {"a": 1, "m": 2, "z": 3}


def test_sorted_dict_copy_returns_a_fresh_dict():
    original = {"only": {"nested": True}}
    result = sorted_dict_copy(original)

    assert result is not original
