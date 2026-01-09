"""
Copyright © 2026 Lourens Wasserman. All Rights Reserved.
Neurop Block Forge - https://neurop-forge.com
Commercial use requires a license. See LICENSE file.
"""

"""
Array and Matrix Operations - Pure functions for numerical array manipulation.

All functions are:
- Pure (no side effects)
- Deterministic (same input = same output)
- Atomic (one intent per function)

License: MIT
"""


def array_add(a: list, b: list) -> list:
    """Add two arrays element-wise."""
    if len(a) != len(b):
        return []
    return [x + y for x, y in zip(a, b)]


def array_subtract(a: list, b: list) -> list:
    """Subtract two arrays element-wise."""
    if len(a) != len(b):
        return []
    return [x - y for x, y in zip(a, b)]


def array_multiply(a: list, b: list) -> list:
    """Multiply two arrays element-wise."""
    if len(a) != len(b):
        return []
    return [x * y for x, y in zip(a, b)]


def array_divide(a: list, b: list) -> list:
    """Divide two arrays element-wise."""
    if len(a) != len(b):
        return []
    return [x / y if y != 0 else 0 for x, y in zip(a, b)]


def scalar_multiply(arr: list, scalar: float) -> list:
    """Multiply all elements by a scalar."""
    return [x * scalar for x in arr]


def scalar_add(arr: list, scalar: float) -> list:
    """Add a scalar to all elements."""
    return [x + scalar for x in arr]


def dot_product(a: list, b: list) -> float:
    """Calculate the dot product of two vectors."""
    if len(a) != len(b):
        return 0.0
    return sum(x * y for x, y in zip(a, b))


def cross_product_3d(a: list, b: list) -> list:
    """Calculate the cross product of two 3D vectors."""
    if len(a) != 3 or len(b) != 3:
        return []
    return [
        a[1] * b[2] - a[2] * b[1],
        a[2] * b[0] - a[0] * b[2],
        a[0] * b[1] - a[1] * b[0],
    ]


def vector_magnitude(v: list) -> float:
    """Calculate the magnitude of a vector."""
    return sum(x ** 2 for x in v) ** 0.5


def normalize_vector(v: list) -> list:
    """Normalize a vector to unit length."""
    mag = vector_magnitude(v)
    if mag == 0:
        return [0.0] * len(v)
    return [x / mag for x in v]


def matrix_transpose(matrix: list) -> list:
    """Transpose a matrix (list of lists)."""
    if not matrix or not matrix[0]:
        return []
    rows = len(matrix)
    cols = len(matrix[0])
    return [[matrix[r][c] for r in range(rows)] for c in range(cols)]


def matrix_add(a: list, b: list) -> list:
    """Add two matrices."""
    if not a or not b:
        return []
    if len(a) != len(b) or len(a[0]) != len(b[0]):
        return []
    return [[a[i][j] + b[i][j] for j in range(len(a[0]))] for i in range(len(a))]


def matrix_subtract(a: list, b: list) -> list:
    """Subtract two matrices."""
    if not a or not b:
        return []
    if len(a) != len(b) or len(a[0]) != len(b[0]):
        return []
    return [[a[i][j] - b[i][j] for j in range(len(a[0]))] for i in range(len(a))]


def matrix_scalar_multiply(matrix: list, scalar: float) -> list:
    """Multiply a matrix by a scalar."""
    if not matrix:
        return []
    return [[cell * scalar for cell in row] for row in matrix]


def matrix_multiply(a: list, b: list) -> list:
    """Multiply two matrices."""
    if not a or not b:
        return []
    if len(a[0]) != len(b):
        return []
    rows_a, cols_a = len(a), len(a[0])
    cols_b = len(b[0])
    result = [[0 for _ in range(cols_b)] for _ in range(rows_a)]
    for i in range(rows_a):
        for j in range(cols_b):
            for k in range(cols_a):
                result[i][j] += a[i][k] * b[k][j]
    return result


def matrix_identity(size: int) -> list:
    """Create an identity matrix of given size."""
    if size <= 0:
        return []
    return [[1 if i == j else 0 for j in range(size)] for i in range(size)]


def matrix_zeros(rows: int, cols: int) -> list:
    """Create a zero matrix of given dimensions."""
    if rows <= 0 or cols <= 0:
        return []
    return [[0 for _ in range(cols)] for _ in range(rows)]


def matrix_ones(rows: int, cols: int) -> list:
    """Create a matrix of ones of given dimensions."""
    if rows <= 0 or cols <= 0:
        return []
    return [[1 for _ in range(cols)] for _ in range(rows)]


def matrix_diagonal(values: list) -> list:
    """Create a diagonal matrix from a list of values."""
    if not values:
        return []
    n = len(values)
    return [[values[i] if i == j else 0 for j in range(n)] for i in range(n)]


def get_matrix_diagonal(matrix: list) -> list:
    """Extract the diagonal elements of a matrix."""
    if not matrix:
        return []
    n = min(len(matrix), len(matrix[0]))
    return [matrix[i][i] for i in range(n)]


def matrix_trace(matrix: list) -> float:
    """Calculate the trace (sum of diagonal elements) of a matrix."""
    diagonal = get_matrix_diagonal(matrix)
    return sum(diagonal)


def matrix_row_sum(matrix: list) -> list:
    """Sum each row of a matrix."""
    if not matrix:
        return []
    return [sum(row) for row in matrix]


def matrix_column_sum(matrix: list) -> list:
    """Sum each column of a matrix."""
    if not matrix or not matrix[0]:
        return []
    cols = len(matrix[0])
    return [sum(matrix[r][c] for r in range(len(matrix))) for c in range(cols)]


def flatten_matrix(matrix: list) -> list:
    """Flatten a matrix to a 1D list."""
    if not matrix:
        return []
    return [cell for row in matrix for cell in row]


def reshape_to_matrix(arr: list, rows: int, cols: int) -> list:
    """Reshape a 1D array to a matrix."""
    if len(arr) != rows * cols:
        return []
    return [arr[i * cols:(i + 1) * cols] for i in range(rows)]


def array_cumulative_sum(arr: list) -> list:
    """Calculate cumulative sum of an array."""
    if not arr:
        return []
    result = []
    total = 0
    for x in arr:
        total += x
        result.append(total)
    return result


def array_cumulative_product(arr: list) -> list:
    """Calculate cumulative product of an array."""
    if not arr:
        return []
    result = []
    total = 1
    for x in arr:
        total *= x
        result.append(total)
    return result


def array_diff(arr: list) -> list:
    """Calculate differences between consecutive elements."""
    if len(arr) < 2:
        return []
    return [arr[i + 1] - arr[i] for i in range(len(arr) - 1)]


def array_abs(arr: list) -> list:
    """Get absolute values of all elements."""
    return [abs(x) for x in arr]


def array_negate(arr: list) -> list:
    """Negate all elements."""
    return [-x for x in arr]


def array_reciprocal(arr: list) -> list:
    """Get reciprocal of all elements."""
    return [1 / x if x != 0 else 0 for x in arr]


def array_square(arr: list) -> list:
    """Square all elements."""
    return [x ** 2 for x in arr]


def array_sqrt(arr: list) -> list:
    """Square root of all non-negative elements."""
    return [x ** 0.5 if x >= 0 else 0 for x in arr]


def array_power(arr: list, exponent: float) -> list:
    """Raise all elements to a power."""
    return [x ** exponent for x in arr]


def linspace(start: float, stop: float, num: int) -> list:
    """Create evenly spaced numbers over an interval."""
    if num <= 0:
        return []
    if num == 1:
        return [start]
    step = (stop - start) / (num - 1)
    return [start + i * step for i in range(num)]


def arange(start: float, stop: float, step: float) -> list:
    """Create array of values from start to stop with given step."""
    if step == 0:
        return []
    if (step > 0 and start >= stop) or (step < 0 and start <= stop):
        return []
    result = []
    current = start
    while (step > 0 and current < stop) or (step < 0 and current > stop):
        result.append(current)
        current += step
    return result
