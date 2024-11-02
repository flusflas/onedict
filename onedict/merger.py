"""
This module provides functionality to merge multiple dictionaries recursively.
It includes conflict resolution mechanisms to handle cases where dictionary keys
have conflicting values. The module defines a custom exception for merge
conflicts and allows the use of custom conflict solvers.
"""

from typing import Callable, Any, Optional, List

from onedict.solvers import Skip


class MergeConflictException(Exception):
    """
    Custom exception to represent a conflict between two values in a dictionary.
    """

    def __init__(self, key, value1, value2):
        if isinstance(key, list):
            key = ".".join(key)
        super().__init__(f"Conflict detected for key '{key}'")
        self.key = key
        self.value1 = value1
        self.value2 = value2

    def __str__(self):
        return f"{super().__str__()}: {self.value1} != {self.value2}"


def merge(
    *dicts: dict,
    conflict_solvers: Optional[List[Callable[[List[str], Any, Any], Any]]] = None,
) -> dict:
    """
    Merge an arbitrary number of dictionaries recursively. If there is a
    conflict between the values of identical keys, an exception is raised unless
    the values are identical.

    :param dicts: An arbitrary number of dictionaries to be merged.
    :param conflict_solvers: Optional. A list of functions to handle conflicts
            between values. Each function should take three arguments: the
            dictionary key of the conflict, the two conflicting values, and
            return the resolved value. If the conflict cannot be resolved, the
            function should raise a MergeConflictException or return
            _solver_skip to try the next conflict solver.
    :return: A new dictionary that is the result of merging all the provided
             dictionaries.
    :raises MergeConflictException: If a conflict is detected between the
            dictionaries.
    """

    def merge_two_dicts(dict1, dict2, current_key: List[str] = None) -> dict:
        """
        Merge two dictionaries recursively.
        :param dict1: The first dictionary to merge.
        :param dict2: The second dictionary to merge.
        :param current_key: The current key being merged.
        :return: A new dictionary that is the result of merging the two provided
                 dictionaries.
        """
        if current_key is None:
            current_key = []

        merged = {}

        ordered_keys = list(dict1.keys()) + [
            key for key in dict2.keys() if key not in dict1
        ]

        for key in ordered_keys:
            full_key = current_key + [key]
            conflict = False

            if key in dict1 and key in dict2:
                if dict1[key] == dict2[key]:
                    merged[key] = dict1[key]
                elif isinstance(dict1[key], dict) and isinstance(dict2[key], dict):
                    merged[key] = merge_two_dicts(dict1[key], dict2[key], full_key)
                else:
                    conflict = True
            elif key in dict1:
                merged[key] = dict1[key]
            else:
                merged[key] = dict2[key]

            if conflict and conflict_solvers:
                for solver in conflict_solvers:
                    solution = solver(full_key, dict1[key], dict2[key])
                    if not isinstance(solution, Skip):
                        conflict = False
                        merged[key] = solution
                        break

            if conflict:
                raise MergeConflictException(full_key, dict1[key], dict2[key])

        return merged

    # Start with an empty dictionary and merge all provided dictionaries into it
    result = {}
    for dictionary in dicts:
        result = merge_two_dicts(result, dictionary)

    return result
