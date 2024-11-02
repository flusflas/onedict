<h2 align="center"><b>onedict</b></h3>

<p align="center">A Python library for recursively merging
dictionaries with customizable conflict resolution strategies</p>

<p align="center">
  <a href="https://pypi.org/project/onedict"><img src="https://img.shields.io/badge/pip_install-onedict-orange" alt="pip command"></a>
  <a href="https://pypi.org/project/onedict"><img src="https://img.shields.io/pypi/pyversions/onedict.svg?logo=python" alt="Supported Versions"></a>
  <a href="https://codecov.io/gh/flusflas/onedict"><img src="https://codecov.io/gh/flusflas/onedict/graph/badge.svg" alt="codecov"></a>
</p>

## What is *onedict*?

**onedict** is a Python library that provides a simple way to merge multiple
dictionaries with customizable conflict resolution strategies. It allows you to
merge dictionaries with nested structures and provides built-in solvers for
common conflict resolution strategies.

## Installation

```sh
pip install onedict
```

## Usage

### Basic Usage

To merge two or more dictionaries:

```python
from onedict.merger import merge

dict1 = {"info": {"version": "1.0.0", "author": "Alice"}}
dict2 = {"info": {"license": "MIT"}, "data": {"value": 42}}

merged = merge(dict1, dict2)  # More dictionaries can be added as arguments
print(merged)
# Output: {'info': {'version': '1.0.0', 'author': 'Alice', 'license': 'MIT'}, 'data': {'value': 42}}
```

### Handling Conflicts

When merging dictionaries, conflicts may arise when two dictionaries have the
same key with different values. By default, a `MergeConflictError` exception is
raised when a conflict is detected:

```python
from onedict.merger import merge, MergeConflictError

dict1 = {"foo": "bar"}
dict2 = {"foo": "baz"}

try:
    merged = merge(dict1, dict2)   # Raises MergeConflictError
except MergeConflictError as e:
    print(e)
```

To handle conflicts, you can provide a list of conflict solvers to the `merge` function:

```python
def custom_solver(keys, value1, value2):
    return value1  # Keep the value from the first dictionary

merged = merge(dict1, dict2, conflict_solvers=[custom_solver])
print(merged)  # Output: {'foo': 'bar'}
```

Conflict solvers are added to the `conflict_solvers` list in the order they are
provided. The first solver that returns a non-`Skip` value is used to resolve
the conflict. If none of the solvers can resolve the conflict, a
`MergeConflictError` is raised.

### Built-in Solvers

onedict provides built-in solvers for common conflict resolution strategies:

```python
from onedict.merger import merge
from onedict.solvers import unique_lists

merged = merge(
    {"foo": ["bar", "baz"]},
    {"foo": ["bar", "qux"]},
    conflict_solvers=[unique_lists]
)
print(merged)  # Output: {'foo': ['bar', 'baz', 'qux']}
```

The following built-in solvers are available:

| Solver Name           | Description                                                        |
|-----------------------|--------------------------------------------------------------------|
| `unique_lists`        | Merges lists by combining unique elements from both lists.         |
| `concatenate_strings` | Merges two strings by concatenating them with a separator.         |
| `keep_original`       | Keeps the original value and discards the new one.                 |
| `keep_new`            | Keeps the new value and discards the original one.                 |

### Custom Conflict Solvers

You can create custom conflict solvers to handle specific types of conflicts:

```python
from onedict.merger import merge, Skip

def adder(keys, value1, value2):
    if isinstance(value1, int) and isinstance(value2, int):
        return value1 + value2
    return Skip()

merged = merge(
    {"foo": 1},
    {"foo": 2},
    conflict_solvers=[adder]
)
print(merged)  # Output: {'foo': 3}
```
