from dataclasses import dataclass

from pygame import Color, Vector2 as Vec2

from AST import ASTNodeVariableReturn
from Constantes import MARGIN
from Blocs.ParentBloc import ParentBloc
from MyPygameLibrary.UI_elements import hsv_color

COLOR: Color = hsv_color(180, 40, 90)


@dataclass(slots=True)
class ReturnBloc(ParentBloc):
	"""Retourne la valeur de la variable donnée."""
	
	def __init__(self):
		super(ReturnBloc, self).__init__(COLOR, ["value"])
	
	def __repr__(self):
		return f"VariableReturn({self.slots[0]})"
	
	def get_size(self) -> Vec2:
		return self.slots[0].size + Vec2(2, 2) * MARGIN
	
	def slot_position(self, slot_id: int) -> Vec2:
		return Vec2(1, 1) * MARGIN
	
	def as_ASTNode(self) -> ASTNodeVariableReturn:
		return ASTNodeVariableReturn(self.slots[0].as_AST())
