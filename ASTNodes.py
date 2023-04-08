from enum import Enum, auto
from dataclasses import dataclass
from typing import Any


class ASTNodeType(Enum):
	VALUE = auto()  # str | None
	SEQUENCE = auto()  # ASTNodeSequence
	IFELSE = auto()  # ASTNodeIfElse
	WHILE = auto()  # ASTNodeWhile
	VARIABLE_ASSIGNMENT = auto()  # ASTNodeVariableAssignment
	VARIABLE_RETURN = auto()  # ASTNodeVariableReturn
	PRINT = auto()  # ASTNodePrint


@dataclass(slots=True)
class ASTNode:
	type: ASTNodeType
	data: str | list | Any
	
	def __repr__(self):
		data = f"'{self.data}'" if type(self.data) is str else self.data
		return f"ASTNode(type=ASTNodeType.{self.type.name}, data={data})"


@dataclass(slots=True)
class ASTNodeIfElse:
	if_condition: ASTNode
	if_sequence: list[ASTNode]
	elifs: dict[ASTNode, list[ASTNode]] | None
	else_sequence: list[ASTNode] | None


@dataclass(slots=True)
class ASTNodeWhile:
	condition: ASTNode
	sequence: list[ASTNode]
	is_do_while: bool


@dataclass(slots=True)
class ASTNodeSequence:
	elements: list[ASTNode]


@dataclass(slots=True)
class ASTNodeVariableAssignment:
	name: str
	value: ASTNode


@dataclass(slots=True)
class ASTNodeVariableReturn:
	value: ASTNode


@dataclass(slots=True)
class ASTNodePrint:
	value: ASTNode


exemple = ASTNode(type=ASTNodeType.SEQUENCE,
                  data=[
                    ASTNode(type=ASTNodeType.VARIABLE_ASSIGNMENT,
                            data=ASTNodeVariableAssignment(name="Bob est vivant",
                                                           value=ASTNode(
	                                                         type=ASTNodeType.VALUE,
	                                                         data="true"))),
                    ASTNode(type=ASTNodeType.VARIABLE_ASSIGNMENT,
                            data=ASTNodeVariableAssignment(name="age de Bob",
                                                           value=ASTNode(
	                                                         type=ASTNodeType.VALUE,
	                                                         data="3"))),
                    ASTNode(type=ASTNodeType.VARIABLE_ASSIGNMENT,
                            data=ASTNodeVariableAssignment(name="Bob est intelligent",
                                                           value=ASTNode(
	                                                         type=ASTNodeType.VALUE,
	                                                         data="false"))),
                    ASTNode(type=ASTNodeType.VARIABLE_ASSIGNMENT,
                            data=ASTNodeVariableAssignment(name="age limite",
                                                           value=ASTNode(
	                                                         type=ASTNodeType.VALUE,
	                                                         data="6"))),
                    ASTNode(type=ASTNodeType.WHILE,
                            data=ASTNodeWhile(
	                          condition=ASTNode(type=ASTNodeType.VALUE,
	                                            data="{age de Bob} < 6"),
	                          sequence=[
	                            ASTNode(type=ASTNodeType.VARIABLE_ASSIGNMENT,
	                                    data=ASTNodeVariableAssignment(name="age de Bob",
	                                                                   value=ASTNode(
		                                                                 type=ASTNodeType.VALUE,
		                                                                 data="age de Bob + 1"))),
	                            ASTNode(type=ASTNodeType.PRINT,
	                                    data=ASTNodePrint(
		                                  value=ASTNode(type=ASTNodeType.VALUE,
		                                                data="Joyeux anniversaire Bob ! Tu a {age} ans !"))),
	                            ASTNode(type=ASTNodeType.IFELSE,
	                                    data=ASTNodeIfElse(
		                                  if_condition=ASTNode(type=ASTNodeType.VALUE,
		                                                       data="bob est intelligent"),
		                                  if_sequence=[
		                                    ASTNode(type=ASTNodeType.VARIABLE_ASSIGNMENT,
		                                            data=ASTNodeVariableAssignment(name="age limite",
		                                                                           value=ASTNode(
			                                                                         type=ASTNodeType.VALUE,
			                                                                         data="age limite + 0.5")))
		                                  ],
		                                  elifs=None,
		                                  else_sequence=None))
	                          ],
	                          is_do_while=False)),
                    ASTNode(type=ASTNodeType.PRINT,
                            data=ASTNodePrint(value=ASTNode(type=ASTNodeType.VALUE,
                                                            data="Bob est allé rejoindre sa famille d'accueil !")))
                  ])

print(exemple)
