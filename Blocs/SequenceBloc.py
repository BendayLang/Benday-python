from dataclasses import dataclass

from pygame import Color, Vector2 as Vec2

from AST import ASTNode, ASTNodeType
from Constantes import MARGIN
from Blocs.ParentBloc import ParentBloc
from MyPygameLibrary.UI_elements import hsv_color

COLOR: Color = hsv_color(120, 40, 90)


@dataclass(slots=True)
class ASTNodeSequence:
	elements: list[ASTNode]


@dataclass
class SequenceBloc(ParentBloc):
	"""Bloc de logique - si la variable booléenne sur le côté gauche du bloc est vraie,
	la séquence du haut est exécutée, sinon la séquence du haut est exécutée."""
	
	def __init__(self):
		super().__init__(COLOR, 0, 1)
	
	def __repr__(self):
		return f"Sequence( {self.sequences[0]} )"
	
	def get_size(self) -> Vec2:
		return self.sequences[0].size + Vec2(2, 2) * MARGIN
	
	def sequence_position(self, sequence_id: int) -> Vec2:
		return Vec2(1, 1) * MARGIN
	
	def as_ASTNode(self) -> ASTNode:
		return ASTNode(ASTNodeType.SEQUENCE, ASTNodeSequence(
		  self.sequences[0].as_AST()))
