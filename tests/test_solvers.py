from onedict.solvers import (
    Skip,
    unique_lists,
    concatenate_strings,
    keep_original,
    keep_new,
)


def test_unique_lists_merges_and_removes_duplicates():
    result = unique_lists("key", [1, 2, 3], [3, 4, 5])
    assert result == [1, 2, 3, 4, 5]


def test_unique_lists_returns_skip_for_non_lists():
    result = unique_lists("key", [1, 2, 3], "not a list")
    assert isinstance(result, Skip)


def test_concatenate_strings_with_default_separator():
    solver = concatenate_strings()
    result = solver("key", "hello", "world")
    assert result == "hello world"


def test_concatenate_strings_with_custom_separator():
    solver = concatenate_strings(separator="-")
    result = solver("key", "hello", "world")
    assert result == "hello-world"


def test_concatenate_strings_returns_skip_for_non_strings():
    solver = concatenate_strings()
    result = solver("key", "hello", 123)
    assert isinstance(result, Skip)


def test_keep_original_returns_first_value():
    result = keep_original("key", "original", "new")
    assert result == "original"


def test_keep_new_returns_second_value():
    result = keep_new("key", "original", "new")
    assert result == "new"
