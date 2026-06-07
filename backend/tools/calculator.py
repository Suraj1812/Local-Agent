import ast
import operator
import re
from typing import Any, Dict

OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.Mod: operator.mod,
    ast.USub: operator.neg,
}


def format_number(value):
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return str(value)


def _eval(node):
    if isinstance(node, ast.Num):
        return node.n
    if isinstance(node, ast.BinOp) and type(node.op) in OPS:
        return OPS[type(node.op)](_eval(node.left), _eval(node.right))
    if isinstance(node, ast.UnaryOp) and type(node.op) in OPS:
        return OPS[type(node.op)](_eval(node.operand))
    raise ValueError("Unsupported expression")


class CalculatorTool:
    name = "calculator"
    description = "Math operations and statistics"

    async def execute(self, payload: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        raw_expression = str(payload.get("expression") or "0")
        percent_of = re.search(
            r"(\d+(?:\.\d+)?)\s*%\s*(?:of|x|\*)\s*(\d+(?:\.\d+)?)",
            raw_expression,
            flags=re.IGNORECASE,
        )
        if percent_of:
            percent, base = percent_of.groups()
            expression = f"({percent}/100)*{base}"
            parsed = ast.parse(expression, mode="eval")
            result = _eval(parsed.body)
            return {"expression": expression, "result": result, "display_result": format_number(result)}

        match = re.search(r"[-+*/().\d\s%]+", raw_expression)
        expression = (match.group(0) if match else raw_expression).replace("%", "/100")
        parsed = ast.parse(expression, mode="eval")
        result = _eval(parsed.body)
        return {"expression": expression, "result": result, "display_result": format_number(result)}
