import ast
import math
import operator

from langchain_core.tools import tool


_ALLOWED_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
    ast.FloorDiv: operator.floordiv,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}

_ALLOWED_FUNCTIONS = {
    "sqrt": math.sqrt,
    "sin": math.sin,
    "cos": math.cos,
    "tan": math.tan,
    "log": math.log,
    "log10": math.log10,
    "exp": math.exp,
    "fabs": math.fabs,
}

_ALLOWED_CONSTANTS = {
    "pi": math.pi,
    "e": math.e,
}


def _evaluate(node: ast.AST) -> float:
    if isinstance(node, ast.Expression):
        return _evaluate(node.body)

    if isinstance(node, ast.Constant):
        if isinstance(node.value, (int, float)) and not isinstance(
            node.value, bool
        ):
            return float(node.value)
        raise ValueError("Only numeric values are allowed.")

    if isinstance(node, ast.BinOp):
        operation = _ALLOWED_OPERATORS.get(type(node.op))

        if operation is None:
            raise ValueError("Unsupported mathematical operator.")

        left = _evaluate(node.left)
        right = _evaluate(node.right)

        if isinstance(node.op, ast.Pow) and abs(right) > 100:
            raise ValueError("Exponent is too large.")

        return operation(left, right)

    if isinstance(node, ast.UnaryOp):
        operation = _ALLOWED_OPERATORS.get(type(node.op))

        if operation is None:
            raise ValueError("Unsupported unary operator.")

        return operation(_evaluate(node.operand))

    if isinstance(node, ast.Call):
        if not isinstance(node.func, ast.Name):
            raise ValueError("Unsupported function.")

        function = _ALLOWED_FUNCTIONS.get(node.func.id)

        if function is None:
            raise ValueError(
                f"Unsupported function: {node.func.id}"
            )

        if node.keywords:
            raise ValueError("Keyword arguments are not supported.")

        arguments = [_evaluate(argument) for argument in node.args]

        try:
            return float(function(*arguments))
        except TypeError as exc:
            raise ValueError(
                f"Invalid arguments for function: {node.func.id}"
            ) from exc

    if isinstance(node, ast.Name):
        if node.id in _ALLOWED_CONSTANTS:
            return _ALLOWED_CONSTANTS[node.id]

        raise ValueError(f"Unsupported identifier: {node.id}")

    raise ValueError(
        f"Unsupported expression: {type(node).__name__}"
    )


def calculate(expression: str) -> float:
    if not expression or not expression.strip():
        raise ValueError("Expression cannot be empty.")

    expression = expression.strip()

    if len(expression) > 500:
        raise ValueError("Expression is too long.")

    try:
        tree = ast.parse(expression, mode="eval")
        result = _evaluate(tree)
    except SyntaxError as exc:
        raise ValueError("Invalid mathematical expression.") from exc

    if not math.isfinite(result):
        raise ValueError("Calculation resulted in a non-finite value.")

    return result


@tool
def calculator_tool(expression: str) -> str:
    """
    Safely evaluate a mathematical expression.
    Supports arithmetic operations, powers, modulo,
    square root, trigonometric and logarithmic functions.
    """

    try:
        result = calculate(expression)

        if result.is_integer():
            formatted_result = str(int(result))
        else:
            formatted_result = f"{result:.10g}"

        return (
            "Calculation successful.\n"
            f"Expression: {expression.strip()}\n"
            f"Result: {formatted_result}"
        )

    except ValueError as exc:
        return f"Calculation failed: {str(exc)}"

    except ZeroDivisionError:
        return "Calculation failed: division by zero."

    except Exception as exc:
        return f"Calculation error: {str(exc)}"
    