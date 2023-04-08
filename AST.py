from enum import Enum, auto
from dataclasses import dataclass
from typing import Any


class ASTNodeType(Enum):
	VALUE = auto()
	SEQUENCE = auto()
	IFELSE = auto()
	WHILE = auto()
	VARIABLE_ASSIGNMENT = auto()
	VARIABLE_RETURN = auto()
	PRINT = auto()


@dataclass(slots=True)
class ASTNode:
	type: ASTNodeType
	data: str | list | Any
	
	def __repr__(self):
		data = f"'{self.data}'" if type(self.data) is str else self.data
		return f"ASTNode(type=ASTNodeType.{self.type.name}, data={data})"
