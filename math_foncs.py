from dataclasses import dataclass
from typing import Any

@dataclass()
class MathNode:
    operator: str
    left: Any
    right: Any


def parse_math_expression(tokens: list[str]) -> MathNode:
    if len(tokens) == 1:
        return tokens[0]
    return MathNode(tokens[1], tokens[0], parse_math_expression(tokens[2:]))


def get_math_expression(ast) -> int | float:
    if type(ast) == str:
        return float(ast)
    if type(ast) != MathNode:
        print("wtf is this type ??")
        exit(1)
    match ast.operator:
        case "+":
            return get_math_expression(ast.left) + get_math_expression(ast.right)
        case "-":
            return get_math_expression(ast.left) - get_math_expression(ast.right)
        case "*":
            return get_math_expression(ast.left) * get_math_expression(ast.right)
        case "/":
            return get_math_expression(ast.left) / get_math_expression(ast.right)
        case ">":
            return get_math_expression(ast.left) > get_math_expression(ast.right)
        case "<":
            return get_math_expression(ast.left) < get_math_expression(ast.right)


def math_expression(expression: str) -> float | int:
    ast: MathNode = parse_math_expression(expression.split(" "))
    res: float = get_math_expression(ast)
    if res == int(res):
        return int(res)
    return res


def is_math_parsable(expression: str) -> bool:
    for token in expression.split(" "):
        if token in ["+", "-", "*", "/", ">", "<"]:
            continue
        try:
            float(token)
        except:
            return False
    return True
