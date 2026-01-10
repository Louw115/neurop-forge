"""
Copyright © 2026 Lourens Wasserman. All Rights Reserved.
Neurop Block Forge - https://neurop-forge.com
Commercial use requires a license. See LICENSE file.
"""

"""
Matrix Utilities - Pure functions for matrix operations.
All functions are pure, deterministic, and atomic.
"""

def create_matrix(rows: list) -> dict:
    """Create a matrix from rows."""
    return {
        "rows": [list(row) for row in rows],
        "num_rows": len(rows),
        "num_cols": len(rows[0]) if rows else 0
    }


def matrix_get(m: dict, row: int, col: int) -> float:
    """Get element at position."""
    return m["rows"][row][col]


def matrix_set(m: dict, row: int, col: int, value: float) -> dict:
    """Set element at position."""
    new_rows = [list(r) for r in m["rows"]]
    new_rows[row][col] = value
    return create_matrix(new_rows)


def matrix_add(m1: dict, m2: dict) -> dict:
    """Add two matrices."""
    rows = [[m1["rows"][i][j] + m2["rows"][i][j] for j in range(m1["num_cols"])] for i in range(m1["num_rows"])]
    return create_matrix(rows)


def matrix_subtract(m1: dict, m2: dict) -> dict:
    """Subtract two matrices."""
    rows = [[m1["rows"][i][j] - m2["rows"][i][j] for j in range(m1["num_cols"])] for i in range(m1["num_rows"])]
    return create_matrix(rows)


def matrix_scale(m: dict, scalar: float) -> dict:
    """Scale matrix by scalar."""
    rows = [[cell * scalar for cell in row] for row in m["rows"]]
    return create_matrix(rows)


def matrix_multiply(m1: dict, m2: dict) -> dict:
    """Multiply two matrices."""
    rows = []
    for i in range(m1["num_rows"]):
        row = []
        for j in range(m2["num_cols"]):
            val = sum(m1["rows"][i][k] * m2["rows"][k][j] for k in range(m1["num_cols"]))
            row.append(val)
        rows.append(row)
    return create_matrix(rows)


def matrix_transpose(m: dict) -> dict:
    """Transpose a matrix."""
    rows = [[m["rows"][i][j] for i in range(m["num_rows"])] for j in range(m["num_cols"])]
    return create_matrix(rows)


def matrix_identity(size: int) -> dict:
    """Create identity matrix."""
    rows = [[1 if i == j else 0 for j in range(size)] for i in range(size)]
    return create_matrix(rows)


def matrix_zeros(num_rows: int, num_cols: int) -> dict:
    """Create zero matrix."""
    rows = [[0 for _ in range(num_cols)] for _ in range(num_rows)]
    return create_matrix(rows)


def matrix_ones(num_rows: int, num_cols: int) -> dict:
    """Create matrix of ones."""
    rows = [[1 for _ in range(num_cols)] for _ in range(num_rows)]
    return create_matrix(rows)


def matrix_diagonal(values: list) -> dict:
    """Create diagonal matrix."""
    n = len(values)
    rows = [[values[i] if i == j else 0 for j in range(n)] for i in range(n)]
    return create_matrix(rows)


def matrix_get_diagonal(m: dict) -> list:
    """Get diagonal elements."""
    return [m["rows"][i][i] for i in range(min(m["num_rows"], m["num_cols"]))]


def matrix_trace(m: dict) -> float:
    """Calculate trace (sum of diagonal)."""
    return sum(matrix_get_diagonal(m))


def matrix_determinant_2x2(m: dict) -> float:
    """Calculate determinant of 2x2 matrix."""
    r = m["rows"]
    return r[0][0] * r[1][1] - r[0][1] * r[1][0]


def matrix_minor(m: dict, row: int, col: int) -> dict:
    """Get minor matrix (remove row and column)."""
    rows = [[m["rows"][i][j] for j in range(m["num_cols"]) if j != col] for i in range(m["num_rows"]) if i != row]
    return create_matrix(rows)


def matrix_cofactor(m: dict, row: int, col: int) -> float:
    """Calculate cofactor at position."""
    minor = matrix_minor(m, row, col)
    sign = 1 if (row + col) % 2 == 0 else -1
    if minor["num_rows"] == 2:
        return sign * matrix_determinant_2x2(minor)
    return sign * matrix_determinant(minor)


def matrix_determinant(m: dict) -> float:
    """Calculate determinant recursively."""
    if m["num_rows"] == 1:
        return m["rows"][0][0]
    if m["num_rows"] == 2:
        return matrix_determinant_2x2(m)
    det = 0
    for j in range(m["num_cols"]):
        det += m["rows"][0][j] * matrix_cofactor(m, 0, j)
    return det


def matrix_row(m: dict, row: int) -> list:
    """Get a row from matrix."""
    return list(m["rows"][row])


def matrix_column(m: dict, col: int) -> list:
    """Get a column from matrix."""
    return [m["rows"][i][col] for i in range(m["num_rows"])]


def matrix_swap_rows(m: dict, row1: int, row2: int) -> dict:
    """Swap two rows."""
    new_rows = [list(r) for r in m["rows"]]
    new_rows[row1], new_rows[row2] = new_rows[row2], new_rows[row1]
    return create_matrix(new_rows)


def matrix_scale_row(m: dict, row: int, scalar: float) -> dict:
    """Scale a row by scalar."""
    new_rows = [list(r) for r in m["rows"]]
    new_rows[row] = [x * scalar for x in new_rows[row]]
    return create_matrix(new_rows)


def matrix_add_rows(m: dict, target_row: int, source_row: int, scalar: float) -> dict:
    """Add scaled source row to target row."""
    new_rows = [list(r) for r in m["rows"]]
    for j in range(m["num_cols"]):
        new_rows[target_row][j] += scalar * new_rows[source_row][j]
    return create_matrix(new_rows)


def matrix_is_square(m: dict) -> bool:
    """Check if matrix is square."""
    return m["num_rows"] == m["num_cols"]


def matrix_is_symmetric(m: dict) -> bool:
    """Check if matrix is symmetric."""
    if not matrix_is_square(m):
        return False
    for i in range(m["num_rows"]):
        for j in range(i + 1, m["num_cols"]):
            if m["rows"][i][j] != m["rows"][j][i]:
                return False
    return True


def matrix_is_diagonal(m: dict) -> bool:
    """Check if matrix is diagonal."""
    for i in range(m["num_rows"]):
        for j in range(m["num_cols"]):
            if i != j and m["rows"][i][j] != 0:
                return False
    return True


def matrix_element_wise_multiply(m1: dict, m2: dict) -> dict:
    """Element-wise multiplication (Hadamard product)."""
    rows = [[m1["rows"][i][j] * m2["rows"][i][j] for j in range(m1["num_cols"])] for i in range(m1["num_rows"])]
    return create_matrix(rows)


def matrix_sum(m: dict) -> float:
    """Sum of all elements."""
    return sum(sum(row) for row in m["rows"])


def matrix_mean(m: dict) -> float:
    """Mean of all elements."""
    total = m["num_rows"] * m["num_cols"]
    return matrix_sum(m) / total if total > 0 else 0


def matrix_max(m: dict) -> float:
    """Maximum element."""
    return max(max(row) for row in m["rows"])


def matrix_min(m: dict) -> float:
    """Minimum element."""
    return min(min(row) for row in m["rows"])


def matrix_flatten(m: dict) -> list:
    """Flatten matrix to 1D list."""
    return [cell for row in m["rows"] for cell in row]


def matrix_reshape(values: list, num_rows: int, num_cols: int) -> dict:
    """Reshape 1D list into matrix."""
    rows = [values[i * num_cols:(i + 1) * num_cols] for i in range(num_rows)]
    return create_matrix(rows)
