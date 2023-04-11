from dataclasses import dataclass
from benday_rust import is_math_parsable, math_expression

variables: dict[str, str | float | int | bool] = {}


def expand_variables(expression: str):
	"""Remplace le nom des variables par leur valeur."""
	first_curly = expression.find("{")
	if first_curly == -1:
		return expression
	else:
		next_curly = expression[first_curly:].find("}")
		to_replace = expression[first_curly:first_curly + next_curly + 1]
		var_name = to_replace[1:-1]
		return expand_variables(expression.replace(to_replace, str(variables[var_name])))


class ASTNode:
	"""Nœud de l’Abstract Syntax Tree - Correspond également à un bloc et à une fonction."""
	
	def execute(self) -> str | float | int | bool | None:
		"""Exécute la fonction de ce nœud et renvoie (où non) une valeur"""


@dataclass(slots=True)
class ASTNodeValue(ASTNode):
	value: str
	
	def execute(self) -> str | float | int | bool | None:
		if type(self.value) is str:
			expression = expand_variables(self.value)
			if is_math_parsable(expression):
				return math_expression(expression)
			return expression
		return self.value


@dataclass(slots=True)
class ASTNodeSequence(ASTNode):
	elements: list[ASTNode]
	
	def execute(self) -> str | float | int | bool | None:
		for element in self.elements:
			if type(element) is ASTNodeVariableReturn:
				element: ASTNodeVariableReturn
				return element.value.execute()
			element.execute()


@dataclass(slots=True)
class ASTNodeIfElse(ASTNode):
	if_condition: ASTNode
	if_sequence: ASTNodeSequence
	elifs: list[tuple[ASTNode, ASTNodeSequence]]
	else_sequence: ASTNodeSequence | None
	
	def execute(self) -> str | float | int | bool | None:
		if self.if_condition.execute():
			return self.if_sequence.execute()
		
		for condition, sequence in self.elifs:
			if condition.execute():
				return sequence.execute()
		
		if self.else_sequence is not None:
			return self.else_sequence.execute()


@dataclass(slots=True)
class ASTNodeWhile(ASTNode):
	condition: ASTNode
	sequence: ASTNodeSequence
	is_do: bool
	
	def execute(self) -> str | float | int | bool | None:
		count: int = 0
		
		if self.is_do:
			value = self.sequence.execute()
			if value is not None: return value
		
		while self.condition.execute():
			value = self.sequence.execute()
			if value is not None: return value
			count += 1
			if count >= 99:
				print(f"more than {count} iteration !")
				break


@dataclass(slots=True)
class ASTNodeVariableAssignment(ASTNode):
	name: str
	value: ASTNode
	
	def execute(self) -> None:
		variables[self.name] = self.value.execute()


@dataclass(slots=True)
class ASTNodePrint(ASTNode):
	value: ASTNode
	
	def execute(self) -> None:
		print(self.value.execute())


@dataclass(slots=True)
class ASTNodeVariableReturn(ASTNode):
	value: ASTNode
