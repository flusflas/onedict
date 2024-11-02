from collections import defaultdict, OrderedDict, Counter

import pytest

from onedict.merger import merge, MergeConflictException
from onedict.solvers import Skip, unique_lists


def test_merge_dict():
    """
    Test merging two dictionaries with overlapping keys but no conflicts.
    """
    merged = merge(
        {"foo": {"bar": "baz"}, "number": 42, "list": [1, 2, 3]},
        {"foo": {"bar": "baz"}, "number": 42},
    )
    assert merged == {"foo": {"bar": "baz"}, "number": 42, "list": [1, 2, 3]}


def test_merge_conflict_array():
    """Test merging two dictionaries with a conflict on array elements."""

    def on_conflict(keys, value1, value2):
        if isinstance(value1, list) and isinstance(value2, list):
            return value1 + [item for item in value2 if item not in value1]

    merged = merge(
        {"foo": ["bar", "baz"]}, {"foo": ["bar", "qux"]}, conflict_solvers=[on_conflict]
    )

    assert merged == {"foo": ["bar", "baz", "qux"]}


def test_merge_conflict_string():
    """Test merging two dictionaries with a conflict on string values."""

    def on_conflict(keys, value1, value2):
        if keys == ["foo"]:
            return f"{value1} & {value2}"

    merged = merge({"foo": "bar"}, {"foo": "baz"}, conflict_solvers=[on_conflict])

    assert merged == {"foo": "bar & baz"}


def test_merge_conflict_nested():
    """Test merging two dictionaries with a conflict on nested values."""

    def on_conflict(keys, value1, value2):
        if keys == ["info", "version"]:
            return f"{value1} & {value2}"
        elif keys == ["info", "title"]:
            return f"{value1} + {value2}"

    merged = merge(
        {"info": {"title": "Test API 1", "version": "1.0.0"}},
        {"info": {"title": "Test API 2", "version": "1.0.1"}},
        conflict_solvers=[on_conflict],
    )

    assert merged == {
        "info": {"title": "Test API 1 + Test API 2", "version": "1.0.0 & 1.0.1"}
    }


def test_merge_conflict_exception():
    """Test merging two dictionaries with a conflict on a single key."""
    with pytest.raises(MergeConflictException) as e:
        merge({"info": {"version": "1.0.0"}}, {"info": {"version": "1.0.1"}})

    assert str(e.value) == "Conflict detected for key 'info.version': 1.0.0 != 1.0.1"


def test_merge_custom_conflict_exception():
    """Test merging two dictionaries with a custom conflict exception."""

    def on_conflict(keys, value1, value2):
        raise MergeConflictException(keys, f"'{value1}'", f"'{value2}'")

    with pytest.raises(MergeConflictException) as e:
        merge(
            {"info": {"version": "1.0.0"}},
            {"info": {"version": "1.0.1"}},
            conflict_solvers=[on_conflict],
        )

    assert (
        str(e.value) == "Conflict detected for key 'info.version': '1.0.0' != '1.0.1'"
    )


def test_merge_with_unique_lists_solver():
    """
    Test merging two dictionaries with a conflict on lists using the
    unique_lists solver.
    """
    merged = merge(
        {"foo": ["bar", "baz"]},
        {"foo": ["bar", "qux"]},
        conflict_solvers=[unique_lists],
    )

    assert merged == {"foo": ["bar", "baz", "qux"]}


def test_merge_with_unique_lists_solver_complex():
    """
    Test merging two dictionaries with a conflict on lists using the
    unique_lists solver with more complex list elements.
    """
    merged = merge(
        {"foo": [{"bar": "baz"}, {"baz": "qux"}]},
        {"foo": [{"qux": "foo"}, {"bar": "baz"}]},
        conflict_solvers=[unique_lists],
    )

    assert merged == {"foo": [{"bar": "baz"}, {"baz": "qux"}, {"qux": "foo"}]}


def test_merge_with_multiple_solvers():
    """
    Test merging two dictionaries with multiple conflict solvers.
    This test also tests the Skip mechanism that allows chaining solvers.
    """
    solver_strings_hits = 0
    solver_unique_lists_hits = 0
    solver_default_hits = 0

    def solver_strings(keys, value1, value2):
        nonlocal solver_strings_hits
        solver_strings_hits += 1
        if isinstance(value1, str) and isinstance(value2, str):
            return f"{value1} & {value2}"
        return Skip()

    def solver_default(keys, value1, value2):
        nonlocal solver_default_hits
        solver_default_hits += 1
        return None

    def _unique_lists(keys, value1, value2):
        nonlocal solver_unique_lists_hits
        solver_unique_lists_hits += 1
        return unique_lists(keys, value1, value2)

    merged = merge(
        {"foo": ["alpha", "bravo"], "bar": "baz", "baz": 0},
        {"foo": ["alpha", "charlie"], "bar": "qux", "baz": 1},
        conflict_solvers=[solver_strings, _unique_lists, solver_default],
    )

    assert merged == {
        "foo": ["alpha", "bravo", "charlie"],
        "bar": "baz & qux",
        "baz": None,
    }

    assert solver_strings_hits == 3
    assert solver_unique_lists_hits == 2
    assert solver_default_hits == 1


def test_merge_counter():
    """Test merging two Counters with a conflict."""
    dict1 = Counter({"foo": 1, "bar": 2})
    dict2 = Counter({"foo": 2, "baz": 3})

    def on_conflict(keys, value1, value2):
        return value1 + value2

    merged = merge(dict1, dict2, conflict_solvers=[on_conflict])
    assert merged == Counter({"foo": 3, "bar": 2, "baz": 3})


def test_merge_conflict_defaultdict():
    """Test merging two defaultdicts with a conflict."""
    dict1 = defaultdict(list, {"foo": [1, 2]})
    dict2 = defaultdict(list, {"foo": [3, 4]})

    def on_conflict(keys, value1, value2):
        if isinstance(value1, list) and isinstance(value2, list):
            return value1 + value2

    merged = merge(dict1, dict2, conflict_solvers=[on_conflict])
    assert merged == {"foo": [1, 2, 3, 4]}


def test_merge_conflict_ordereddict():
    """Test merging two OrderedDicts with a conflict."""
    dict1 = OrderedDict({"foo": 1})
    dict2 = OrderedDict({"foo": 2})

    def on_conflict(keys, value1, value2):
        return value1 + value2

    merged = merge(dict1, dict2, conflict_solvers=[on_conflict])
    assert merged == OrderedDict({"foo": 3})
