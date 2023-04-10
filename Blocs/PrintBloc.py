from dataclasses import dataclass

from pygame import Color, Surface, Vector2 as Vec2

from AST import ASTNodePrint
from Constantes import FONT_20, INNER_MARGIN, MARGIN
from Blocs.ParentBloc import ParentBloc
from MyPygameLibrary.Camera import Camera
from MyPygameLibrary.UI_elements import draw_text, hsv_color

COLOR: Color = hsv_color(330, 30, 100)

TEXT_PRINT: str = "PRINT"
TEXT_PRINT_SIZE: Vec2 = Vec2(FONT_20.size(TEXT_PRINT))


@dataclass(slots=True)
class PrintBloc(ParentBloc):
	"""Retourne la valeur de la variable donnée."""
	
	def __init__(self):
		super(PrintBloc, self).__init__(COLOR, 1)
	
	def __repr__(self):
		return f"Print({self.slots[0]})"
	
	def get_size(self) -> Vec2:
		return self.slots[0].size + Vec2(TEXT_PRINT_SIZE.x + INNER_MARGIN, 0) + Vec2(2 * MARGIN)
	
	def slot_position(self, slot_id: int) -> Vec2:
		return Vec2(TEXT_PRINT_SIZE.x + INNER_MARGIN, 0) + Vec2(MARGIN)
	
	def post_draw(self, surface: Surface, camera: Camera, origin: Vec2):
		position = Vec2(0, TEXT_PRINT_SIZE.y / 2) + Vec2(MARGIN)
		draw_text(surface, TEXT_PRINT, origin + position, 20,
		          "black", align="left", camera=camera)
	
	def as_ASTNode(self) -> ASTNodePrint:
		return ASTNodePrint(self.slots[0].as_AST())
