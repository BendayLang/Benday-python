from typing import Any

from Blocs.IfElseBloc import ASTNodeIfElse
from Blocs.PrintBloc import ASTNodePrint
from Blocs.VariableAssignmentBloc import ASTNodeVariableAssignment
from Blocs.WhileBloc import ASTNodeWhile
from math_foncs import is_math_parsable, math_expression
from AST import ASTNode, ASTNodeType


g_variables: dict[str, Any] = {}


def exec_sequence(intructions: list[ASTNode]):
	for instr in intructions:
		exec_ast(instr)


def exec_ifelse(node: ASTNodeIfElse):
	if exec_ast(node.if_condition):
		# if node.is_retrun: retrun
		exec_sequence(node.if_sequence)


def exec_var_assignment(node: ASTNodeVariableAssignment):
	g_variables[node.name] = exec_ast(node.value)
	return None


def exec_while(node: ASTNodeWhile):
	count: int = 0
	if node.is_do_while:
		exec_sequence(node.sequence)
	while (exec_ast(node.condition)):
		exec_sequence(node.sequence)
		count += 1
		if count > 100:
			print(f"more than {count} iteration !")
			break
	return None  # TODO


def exec_builtin(node: ASTNodePrint):
	print(exec_ast(node.value))


def exec_value(data):
	if type(data) is str:
		expression = expand_variables(data)
		if is_math_parsable(expression):
			return math_expression(expression)
		return expression
	return data


def exec_ast(node: ASTNode) -> Any | None:
	if node.type == ASTNodeType.VALUE:
		return exec_value(node.data)
	elif node.type == ASTNodeType.SEQUENCE:
		return exec_sequence(node.data)
	elif node.type == ASTNodeType.IFELSE:
		return exec_ifelse(node.data)
	elif node.type == ASTNodeType.WHILE:
		return exec_while(node.data)
	elif node.type == ASTNodeType.VARIABLE_ASSIGNMENT:
		return exec_var_assignment(node.data)
	elif node.type == ASTNodeType.VARIABLE_RETURN:
		print("var return")
		return None
	elif node.type == ASTNodeType.PRINT:
		return exec_builtin(node.data)
	else:
		print("error -> type note found...")
		# exit()
		return None


#####################################################################
#####################################################################
#####################################################################

def expand_variables(expression: str):
	first_curly = expression.find("{")
	if first_curly == -1:
		return expression
	else:
		next_curly = expression[first_curly:].find("}")
		to_replace = expression[first_curly:first_curly + next_curly + 1]
		var_name = to_replace[1:-1]
		return expand_variables(expression.replace(to_replace, str(g_variables[var_name])))
