from dataclasses import dataclass
from pygame import Color, Surface, Vector2 as Vec2

from AST import ASTNode, ASTNodeType, ASTNodeVariableAssignment
from Constantes import FONT_20, INNER_MARGIN, MARGIN
from Blocs.ParentBloc import ParentBloc
from MyPygameLibrary.Camera import Camera
from MyPygameLibrary.UI_elements import TextBox, change_color, draw_text, hsv_color
from MyPygameLibrary.World import draw_rect

COLOR: Color = hsv_color(30, 60, 100)

TEXT_EQUAL: str = "="
TEXT_EQUAL_SIZE: Vec2 = Vec2(FONT_20.size(TEXT_EQUAL))

NAME_BOX_SIZE: Vec2 = Vec2(60, 25)


@dataclass(slots=True)
class VariableAssignmentBloc(ParentBloc):
	"""Bloc d’assignation de variable - la variable nommée sur le côté gauche du bloc
	prend la valeur de ce que contient le côté droit."""
	name_box: TextBox
	
	def __init__(self):
		self.name_box = TextBox(
		  None, NAME_BOX_SIZE,
		  change_color(COLOR, s_fonc=lambda s: s * .1, v_fonc=lambda _: 1),
		  change_color(COLOR, s_fonc=lambda s: s * .4),
		  fixed_size=False, default_text="none", text_size=18, corner_radius=2, border=0)
		super(VariableAssignmentBloc, self).__init__(COLOR, 1, 0, ["name_box"])
	
	def __repr__(self):
		name_text = self.name_box.text if self.name_box.text else "-"
		return f"VariableAssignment({name_text} = {self.slots[0]})"
	
	def get_size(self) -> Vec2:
		width = max([slot.size.x for slot in self.slots]) +\
		        self.name_box.size.x + TEXT_EQUAL_SIZE.x + 2 * INNER_MARGIN
		height = sum([slot.size.y for slot in self.slots]) + max(len(self.slots) - 1, 0) * INNER_MARGIN
		return Vec2(width, height) + Vec2(2 * MARGIN)
	
	def slot_position(self, slot_id: int) -> Vec2:
		position_x = self.name_box.size.x + TEXT_EQUAL_SIZE.x + 2 * INNER_MARGIN
		position_y = sum([slot.size.y for slot in self.slots[:slot_id]]) + slot_id * INNER_MARGIN
		return Vec2(position_x, position_y) + Vec2(MARGIN)
	
	def post_draw(self, surface: Surface, camera: Camera, origin: Vec2):
		position = Vec2(self.name_box.size.x + INNER_MARGIN, self.slots[0].size.y / 2) + Vec2(MARGIN)
		draw_text(surface, TEXT_EQUAL, origin + position, 20,
		          "black", align="left", camera=camera, bold=True)
	
	def button_size(self, button_id: int) -> Vec2:
		match self.buttons[button_id]:
			case "name_box":
				return self.name_box.size
	
	def button_position(self, button_id: int) -> Vec2:
		match self.buttons[button_id]:
			case "name_box":
				return Vec2(MARGIN, (self.size.y - self.name_box.size.y) / 2)
	
	def draw_button(self, surface: Surface, camera: Camera, origin: Vec2, hovered: bool, button_id: int):
		position = self.button_position(button_id)
		size = self.button_size(button_id)
		
		match self.buttons[button_id]:
			case "name_box":
				self.name_box.draw(surface, camera, origin + position)
				if hovered:
					draw_rect(surface, camera, "black", origin + position, size, 1, 2)
	
	def button_function(self, button_id: int):
		match self.buttons[button_id]:
			case "name_box":
				self.name_box.select()
				return False
	
	def always_draw_button(self, button_id: int) -> bool:
		match self.buttons[button_id]:
			case "name_box":
				return True
	
	def as_ASTNode(self) -> ASTNode:
		name_text = self.name_box.text if self.name_box.text else "-"
		return ASTNode(ASTNodeType.VARIABLE_ASSIGNMENT, ASTNodeVariableAssignment(
		  name_text, self.slots[0].as_AST()
		))
