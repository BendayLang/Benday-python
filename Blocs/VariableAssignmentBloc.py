from dataclasses import dataclass
from pygame import Color, Surface, Vector2 as Vec2

from AST import ASTNodeVariableAssignment
from Constantes import FONT_20, INNER_MARGIN, MARGIN, SLOT_SIZE, SLOT_TEXT_SIZE, SMALL_RADIUS
from Blocs.ParentBloc import ParentBloc
from MyPygameLibrary.Camera import Camera
from MyPygameLibrary.UI_elements import TextBox, change_color, darker, draw_text, hsv_color
from MyPygameLibrary.World import draw_line, draw_rect

COLOR: Color = hsv_color(30, 60, 100)

TEXT_EQUAL: str = "="
TEXT_EQUAL_SIZE: Vec2 = Vec2(FONT_20.size(TEXT_EQUAL))

TEXT_TYPES: list[str] = ["Int", "Float", "Bool", "String"]
TEXT_TYPES_SIZES: list[Vec2] = [Vec2(FONT_20.size(text)) for text in TEXT_TYPES]
TEXT_HEIGHT: int = FONT_20.get_height()

BT_TYPE_SIZE: Vec2 = Vec2(20, 16)

TYPE_COLOR: Color = change_color(COLOR, s_fonc=lambda _: .1, v_fonc=lambda _: .9)


@dataclass(slots=True)
class VariableAssignmentBloc(ParentBloc):
	"""Bloc d’assignation de variable - la variable nommée sur le côté gauche du bloc
	prend la valeur de ce que contient le côté droit."""
	name_box: TextBox
	type: str | None
	open_type: bool
	
	def __init__(self):
		self.name_box = TextBox(
		  None, SLOT_SIZE,
		  change_color(COLOR, s_fonc=lambda s: s * .1, v_fonc=lambda _: 1),
		  change_color(COLOR, s_fonc=lambda s: s * .4), fixed_size=False,
		  default_text="name", text_size=SLOT_TEXT_SIZE, corner_radius=2, border=0)
		self.type = None
		self.open_type = False
		super(VariableAssignmentBloc, self).__init__(
		  COLOR, ["value"], 0,
		  ["name_box", "type"])
	
	def __repr__(self):
		name_text = self.name_box.text if self.name_box.text else "-"
		return f"VariableAssignment({name_text} = {self.slots[0]})"
	
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
		position = Vec2(self.name_box.size.x + BT_TYPE_SIZE.x + 2 * INNER_MARGIN,
		                self.slots[0].size.y / 2) + Vec2(MARGIN)
		draw_text(surface, TEXT_EQUAL, origin + position, 20,
		          "black", align="left", camera=camera, bold=True)
	
	def button_size(self, button_id: int) -> Vec2:
		match self.buttons[button_id]:
			case "type":
				return Vec2(self.text_width, BT_TYPE_SIZE.y)
			case "name_box":
				return self.name_box.size
	
	def button_position(self, button_id: int) -> Vec2:
		match self.buttons[button_id]:
			case "type":
				return Vec2(MARGIN + self.name_box.size.x + INNER_MARGIN,
				            (self.size.y - BT_TYPE_SIZE.y) / 2)
			case "name_box":
				return Vec2(MARGIN, (self.size.y - self.name_box.size.y) / 2)
	
	def draw_button(self, surface: Surface, camera: Camera, origin: Vec2, hovered: bool, button_id: int):
		position = self.button_position(button_id)
		size = self.button_size(button_id)
		
		match self.buttons[button_id]:
			case "type":
				color = darker(TYPE_COLOR, .7) if hovered else TYPE_COLOR
				draw_rect(surface, camera, color, origin + position, size, border_radius=SMALL_RADIUS)
				if self.type is None:
					for i in range(-1, 2):
						draw_rect(surface, camera, "black",
						          origin + position + size / 2 + Vec2(i * 4, 0) - Vec2(1), Vec2(2))
				else:
					draw_text(surface, self.type, origin + position + size / 2, 16, camera=camera)
				
				if self.open_type:
					self.draw_types_list(surface, camera,
					                     origin + position + Vec2(size.x / 2, size.y), hovered)
			case "name_box":
				self.name_box.draw(surface, camera, origin + position)
				if hovered:
					draw_rect(surface, camera, "black", origin + position, size, 1, 2)
	
	def draw_types_list(self, surface: Surface, camera: Camera, origin: Vec2, hovered: bool):
		color = darker("white", .7) if hovered else "white"
		width = self.types_list_size.x
		draw_rect(surface, camera, color, origin - Vec2(width / 2, 0),
		          self.types_list_size, border_radius=SMALL_RADIUS)
		draw_rect(surface, camera, "black", origin - Vec2(width / 2, 0),
		          self.types_list_size, 1, SMALL_RADIUS)
		for i, text_type in enumerate(TEXT_TYPES):
			if i:
				draw_line(surface, camera, "black",
				          origin + Vec2(-width / 2, i * TEXT_HEIGHT),
				          origin + Vec2(width / 2 - 1, i * TEXT_HEIGHT))
			draw_text(surface, text_type, origin + Vec2(0, (i + .5) * TEXT_HEIGHT), 16, camera=camera)
	
	def button_function(self, button_id: int):
		match self.buttons[button_id]:
			case "type":
				if self.open_type:
					self.type = TEXT_TYPES[0]  # TODO collide_func
				self.open_type = not self.open_type
				return not self.open_type
			case "name_box":
				self.name_box.select()
				return False
	
	def always_draw_button(self, button_id: int) -> bool:
		match self.buttons[button_id]:
			case "type":
				return True
			case "name_box":
				return True
	
	@property
	def text_width(self) -> int:
		return int(BT_TYPE_SIZE.x if self.type is None
		           else TEXT_TYPES_SIZES[TEXT_TYPES.index(self.type)].x)
	
	@property
	def types_list_size(self) -> Vec2:
		return Vec2(max([text_type_size.x for text_type_size in TEXT_TYPES_SIZES]),
		            len(TEXT_TYPES) * FONT_20.get_height())
	
	def as_ASTNode(self) -> ASTNodeVariableAssignment:
		name_text = self.name_box.text if self.name_box.text else "-"
		return ASTNodeVariableAssignment(name_text, self.slots[0].as_AST())
