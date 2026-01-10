"""
Copyright © 2026 Lourens Wasserman. All Rights Reserved.
Neurop Block Forge - https://neurop-forge.com
Commercial use requires a license. See LICENSE file.
"""

"""
Expression Parser - Pure functions for parsing and evaluating expressions.
All functions are pure, deterministic, and atomic.
"""

def tokenize_expression(expr: str) -> list:
    """Tokenize a mathematical expression."""
    tokens = []
    i = 0
    while i < len(expr):
        char = expr[i]
        if char.isspace():
            i += 1
            continue
        if char.isdigit() or char == ".":
            j = i
            while j < len(expr) and (expr[j].isdigit() or expr[j] == "."):
                j += 1
            tokens.append({"type": "number", "value": float(expr[i:j])})
            i = j
        elif char.isalpha():
            j = i
            while j < len(expr) and (expr[j].isalnum() or expr[j] == "_"):
                j += 1
            tokens.append({"type": "identifier", "value": expr[i:j]})
            i = j
        elif char in "+-*/%^":
            tokens.append({"type": "operator", "value": char})
            i += 1
        elif char in "()":
            tokens.append({"type": "paren", "value": char})
            i += 1
        elif char == ",":
            tokens.append({"type": "comma", "value": ","})
            i += 1
        else:
            i += 1
    return tokens


def get_operator_precedence(op: str) -> int:
    """Get operator precedence."""
    precedences = {"+": 1, "-": 1, "*": 2, "/": 2, "%": 2, "^": 3}
    return precedences.get(op, 0)


def is_right_associative(op: str) -> bool:
    """Check if operator is right associative."""
    return op == "^"


def infix_to_postfix(tokens: list) -> list:
    """Convert infix tokens to postfix notation."""
    output = []
    operators = []
    for token in tokens:
        if token["type"] == "number" or token["type"] == "identifier":
            output.append(token)
        elif token["type"] == "operator":
            while (operators and operators[-1]["type"] == "operator" and
                   ((not is_right_associative(token["value"]) and
                     get_operator_precedence(token["value"]) <= get_operator_precedence(operators[-1]["value"])) or
                    (is_right_associative(token["value"]) and
                     get_operator_precedence(token["value"]) < get_operator_precedence(operators[-1]["value"])))):
                output.append(operators.pop())
            operators.append(token)
        elif token["value"] == "(":
            operators.append(token)
        elif token["value"] == ")":
            while operators and operators[-1]["value"] != "(":
                output.append(operators.pop())
            if operators:
                operators.pop()
    while operators:
        output.append(operators.pop())
    return output


def evaluate_postfix(tokens: list, variables: dict) -> float:
    """Evaluate postfix expression."""
    stack = []
    for token in tokens:
        if token["type"] == "number":
            stack.append(token["value"])
        elif token["type"] == "identifier":
            stack.append(variables.get(token["value"], 0))
        elif token["type"] == "operator":
            if len(stack) < 2:
                return 0
            b = stack.pop()
            a = stack.pop()
            op = token["value"]
            if op == "+":
                stack.append(a + b)
            elif op == "-":
                stack.append(a - b)
            elif op == "*":
                stack.append(a * b)
            elif op == "/":
                stack.append(a / b if b != 0 else 0)
            elif op == "%":
                stack.append(a % b if b != 0 else 0)
            elif op == "^":
                stack.append(a ** b)
    return stack[0] if stack else 0


def evaluate_expression(expr: str, variables: dict) -> float:
    """Evaluate an expression string."""
    tokens = tokenize_expression(expr)
    postfix = infix_to_postfix(tokens)
    return evaluate_postfix(postfix, variables)


def parse_expression_tree(tokens: list) -> dict:
    """Parse tokens into expression tree."""
    postfix = infix_to_postfix(tokens)
    stack = []
    for token in postfix:
        if token["type"] == "number" or token["type"] == "identifier":
            stack.append({"type": "value", "token": token})
        elif token["type"] == "operator":
            if len(stack) >= 2:
                right = stack.pop()
                left = stack.pop()
                stack.append({"type": "binary", "operator": token["value"], "left": left, "right": right})
    return stack[0] if stack else {"type": "value", "token": {"type": "number", "value": 0}}


def evaluate_tree(tree: dict, variables: dict) -> float:
    """Evaluate expression tree."""
    if tree["type"] == "value":
        token = tree["token"]
        if token["type"] == "number":
            return token["value"]
        return variables.get(token["value"], 0)
    left = evaluate_tree(tree["left"], variables)
    right = evaluate_tree(tree["right"], variables)
    op = tree["operator"]
    if op == "+":
        return left + right
    elif op == "-":
        return left - right
    elif op == "*":
        return left * right
    elif op == "/":
        return left / right if right != 0 else 0
    elif op == "^":
        return left ** right
    return 0


def simplify_tree(tree: dict) -> dict:
    """Simplify constant expressions in tree."""
    if tree["type"] == "value":
        return tree
    left = simplify_tree(tree["left"])
    right = simplify_tree(tree["right"])
    if (left["type"] == "value" and left["token"]["type"] == "number" and
        right["type"] == "value" and right["token"]["type"] == "number"):
        result = evaluate_tree({"type": "binary", "operator": tree["operator"], "left": left, "right": right}, {})
        return {"type": "value", "token": {"type": "number", "value": result}}
    return {"type": "binary", "operator": tree["operator"], "left": left, "right": right}


def tree_to_infix(tree: dict) -> str:
    """Convert expression tree to infix string."""
    if tree["type"] == "value":
        token = tree["token"]
        if token["type"] == "number":
            return str(token["value"])
        return token["value"]
    left = tree_to_infix(tree["left"])
    right = tree_to_infix(tree["right"])
    return f"({left} {tree['operator']} {right})"


def extract_variables(tokens: list) -> list:
    """Extract variable names from tokens."""
    return list(set(t["value"] for t in tokens if t["type"] == "identifier"))


def substitute_variables(tokens: list, substitutions: dict) -> list:
    """Substitute variables with values."""
    result = []
    for token in tokens:
        if token["type"] == "identifier" and token["value"] in substitutions:
            result.append({"type": "number", "value": substitutions[token["value"]]})
        else:
            result.append(token)
    return result


def is_valid_expression(expr: str) -> bool:
    """Check if expression is syntactically valid."""
    tokens = tokenize_expression(expr)
    paren_count = 0
    prev_type = None
    for token in tokens:
        if token["value"] == "(":
            paren_count += 1
        elif token["value"] == ")":
            paren_count -= 1
        if paren_count < 0:
            return False
        if token["type"] == "operator" and prev_type == "operator":
            return False
        prev_type = token["type"]
    return paren_count == 0


def apply_function(func_name: str, args: list) -> float:
    """Apply a mathematical function."""
    import math
    functions = {
        "sin": lambda x: math.sin(x[0]),
        "cos": lambda x: math.cos(x[0]),
        "tan": lambda x: math.tan(x[0]),
        "sqrt": lambda x: math.sqrt(x[0]),
        "abs": lambda x: abs(x[0]),
        "log": lambda x: math.log(x[0]),
        "log10": lambda x: math.log10(x[0]),
        "exp": lambda x: math.exp(x[0]),
        "floor": lambda x: math.floor(x[0]),
        "ceil": lambda x: math.ceil(x[0]),
        "max": lambda x: max(x),
        "min": lambda x: min(x),
        "sum": lambda x: sum(x),
        "avg": lambda x: sum(x) / len(x) if x else 0,
    }
    if func_name in functions:
        return functions[func_name](args)
    return 0
