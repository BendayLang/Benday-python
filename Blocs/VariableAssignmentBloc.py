from dataclasses import dataclass
from pygame import Color, Surface, Vector2 as Vec2

from AST import ASTNodeVariableAssignment
from Constantes import FONT_20, INNER_MARGIN, MARGIN, SLOT_SIZE, SLOT_TEXT_SIZE, SMALL_RADIUS, TYPES
from Blocs.ParentBloc import ParentBloc
from MyPygameLibrary.Camera import Camera
from MyPygameLibrary.UI_elements import TextBox, change_color, darker, draw_text, hsv_color
from MyPygameLibrary.World import draw_rect

COLOR: Color = hsv_color(30, 60, 100)

TEXT_EQUAL: str = "="
TEXT_EQUAL_SIZE: Vec2 = Vec2(FONT_20.size(TEXT_EQUAL))

TEXT_TYPES_SIZES: list[Vec2] = [Vec2(FONT_20.size(text)) for text in TYPES]
TEXT_HEIGHT: int = FONT_20.get_height()

BT_TYPE_SIZE: Vec2 = Vec2(20, 16)

TYPE_COLOR: Color = change_color(COLOR, s_fonc=lambda _: .1, v_fonc=lambda _: .9)


@dataclass(slots=True)
class VariableAssignmentBloc(ParentBloc):
	"""Bloc d’assignation de variable - la variable nommée sur le côté gauche du bloc
	prend la valeur de ce que contient le côté droit."""
	name_box: TextBox
	type: str | None
	
	def __init__(self):
		self.name_box = TextBox(
		  None, SLOT_SIZE,
		  change_color(COLOR, s_fonc=lambda s: s * .1, v_fonc=lambda _: 1),
		  change_color(COLOR, s_fonc=lambda s: s * .4), fixed_size=False,
		  default_text="name", text_size=SLOT_TEXT_SIZE, corner_radius=2, border=0)
		self.type = None
		super(VariableAssignmentBloc, self).__init__(
		  COLOR, ["value"], 0,
		  ["name_box", "choose_type"])
	
	def __repr__(self):
		name_text = self.name_box.text if self.name_box.text else "-"
		return f"VariableAssignment({name_text}: {self.type} = {self.slots[0]})"
	
	def get_size(self) -> Vec2:
		width = max([slot.size.x for slot in self.slots]) +\
		        self.name_box.size.x + self.text_width + TEXT_EQUAL_SIZE.x + 3 * INNER_MARGIN
		height = sum([slot.size.y for slot in self.slots]) + max(len(self.slots) - 1, 0) * INNER_MARGIN
		return Vec2(width, height) + Vec2(2 * MARGIN)
	
	def slot_position(self, slot_id: int) -> Vec2:
		position_x = self.name_box.size.x + self.text_width + TEXT_EQUAL_SIZE.x + 3 * INNER_MARGIN
		position_y = sum([slot.size.y for slot in self.slots[:slot_id]]) + slot_id * INNER_MARGIN
		return Vec2(position_x, position_y) + Vec2(MARGIN)
	
	def post_draw(self, surface: Surface, camera: Camera, origin: Vec2):
		position = Vec2(self.name_box.size.x + self.text_width + 2 * INNER_MARGIN,
		                self.slots[0].size.y / 2) + Vec2(MARGIN)
		draw_text(surface, TEXT_EQUAL, origin + position, 20,
		          "black", align="left", camera=camera, bold=True)
	
	def button_size(self, button_id: int) -> Vec2:
		match self.buttons[button_id]:
			case "name_box":
				return self.name_box.size
			case "choose_type":
				return Vec2(self.text_width, BT_TYPE_SIZE.y)
	
	def button_position(self, button_id: int) -> Vec2:
		match self.buttons[button_id]:
			case "name_box":
				return Vec2(MARGIN, (self.size.y - self.name_box.size.y) / 2)
			case "choose_type":
				return Vec2(MARGIN + self.name_box.size.x + INNER_MARGIN,
				            (self.size.y - BT_TYPE_SIZE.y) / 2)
	
	def draw_button(self, surface: Surface, camera: Camera, origin: Vec2, hovered: bool, button_id: int):
		position = self.button_position(button_id)
		size = self.button_size(button_id)
		
		match self.buttons[button_id]:
			case "name_box":
				self.name_box.draw(surface, camera, origin + position)
				if hovered:
					draw_rect(surface, camera, "black", origin + position, size, 1, 2)
			case "choose_type":
				color = darker(TYPE_COLOR, .7) if hovered else TYPE_COLOR
				draw_rect(surface, camera, color, origin + position, size, border_radius=SMALL_RADIUS)
				
				if self.type is None:
					for i in range(-1, 2):
						draw_rect(surface, camera, "black",
						          origin + position + size / 2 + Vec2(i * 4, 0) - Vec2(1), Vec2(2))
				else:
					draw_text(surface, self.type, origin + position + size / 2, 16, camera=camera)
	
	def button_function(self, button_id: int):
		match self.buttons[button_id]:
			case "name_box":
				self.name_box.select()
				return False
			case "choose_type":
				return False
	
	def always_draw_button(self, button_id: int) -> bool:
		match self.buttons[button_id]:
			case "name_box":
				return True
			case "choose_type":
				return True
	
	@property
	def text_width(self) -> int:
		return int(BT_TYPE_SIZE.x if self.type is None
		           else TEXT_TYPES_SIZES[TYPES.index(self.type)].x)
	
	def as_ASTNode(self) -> ASTNodeVariableAssignment:
		name_text = self.name_box.text if self.name_box.text else "-"
		return ASTNodeVariableAssignment(name_text, self.slots[0].as_AST())
