"""
This module provides solvers for handling conflicts during dictionary merging.
Each solver should take three arguments: the dictionary key of the conflict,
the two conflicting values, and return the resolved value. If the conflict
cannot be resolved, the function should raise a MergeConflictException or return
an instance of the Skip class to try the next conflict solver.
"""


class Skip:
    """
    Unique class to signal that the conflict cannot be resolved and the next
    solver should be tried."""

    pass


def unique_lists(keys, value1, value2):
    """Merge two lists by concatenating them and removing duplicates."""
    if not isinstance(value1, list) or not isinstance(value2, list):
        return Skip()
    return value1 + [item for item in value2 if item not in value1]


def concatenate_strings(separator: str = " "):
    """
    Merge two strings by concatenating them with a separator.
    :param separator: The separator to use when concatenating the strings.

    Example:
    >>> from onedict.merger import merge
    >>> merge({"key": "hello"}, {"key": "world"}, conflict_solvers=[concatenate_strings(' & ')])
    {'key': 'hello & world'}
    """

    def solver(keys, value1, value2):
        if not isinstance(value1, str) or not isinstance(value2, str):
            return Skip()
        return f"{value1}{separator}{value2}"

    return solver


def keep_original(keys, value1, value2):
    """Keep the original value and discard the new one."""
    return value1


def keep_new(keys, value1, value2):
    """Keep the new value and discard the original one."""
    return value2
