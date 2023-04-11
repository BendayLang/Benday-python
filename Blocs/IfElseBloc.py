from dataclasses import dataclass
from pygame import Color, Surface, Vector2 as Vec2

from AST import ASTNodeIfElse
from Constantes import FONT_20, INNER_MARGIN, MARGIN, SMALL_RADIUS
from Blocs.ParentBloc import ParentBloc
from Containers import Sequence, Slot
from MyPygameLibrary.Camera import Camera
from MyPygameLibrary.UI_elements import darker, draw_text, hsv_color
from MyPygameLibrary.World import draw_line, draw_rect

COLOR: Color = hsv_color(230, 10, 100)

TEXT_IF: str = "IF"
TEXT_IF_SIZE: Vec2 = Vec2(FONT_20.size(TEXT_IF))

TEXT_ELIF: str = "ELIF"
TEXT_ELIF_SIZE: Vec2 = Vec2(FONT_20.size(TEXT_ELIF))

TEXT_ELSE: str = "ELSE"
TEXT_ELSE_SIZE: Vec2 = Vec2(FONT_20.size(TEXT_ELSE))

BT_SIZE: Vec2 = Vec2(16)

IF_COLOR: Color = hsv_color(100, 30, 90)
ELIF_COLOR: Color = hsv_color(30, 30, 90)
ELSE_COLOR: Color = hsv_color(0, 30, 90)


@dataclass(slots=True)
class IfElseBloc(ParentBloc):
	"""Bloc de logique - si la variable booléenne sur le côté gauche du bloc est vraie,
	la séquence du haut est exécutée, sinon la séquence du haut est exécutée."""
	is_else: bool
	
	def __init__(self):
		self.is_else = False
		super(IfElseBloc, self).__init__(
		  COLOR,
		  [Slot(COLOR, "False")],
		  [Sequence(IF_COLOR)],
		  ["elif_add", "else"])
	
	def __repr__(self):
		return f"If({self.slots}:  {self.sequences})"
	
	def get_size(self) -> Vec2:
		width = max([sequence.size.x for sequence in self.sequences]) +\
		        max([slot.size.x for slot in self.slots]) + self.text_width + BT_SIZE.x
		height = sum([self.line_height(line) for line in range(len(self.slots))])
		if self.is_else: height += self.sequences[-1].size.y
		return Vec2(width, height) + Vec2(2 * MARGIN) + Vec2(3, len(self.sequences) - 1) * INNER_MARGIN
	
	def slot_position(self, slot_id: int) -> Vec2:
		position_x = max([slot.size.x for slot in self.slots]) -\
		             self.slots[slot_id].size.x + self.text_width + MARGIN + INNER_MARGIN
		position_y = self.line_position_y(slot_id) - self.slots[slot_id].size.y / 2
		return Vec2(position_x, position_y)
	
	def sequence_position(self, sequence_id: int) -> Vec2:
		position_x = max([slot.size.x for slot in self.slots]) + self.text_width + BT_SIZE.x
		position_y = self.line_position_y(sequence_id) - self.sequences[sequence_id].size.y / 2
		return Vec2(position_x, position_y) + Vec2(MARGIN + 3 * INNER_MARGIN, 0)
	
	def post_draw(self, surface: Surface, camera: Camera, origin: Vec2):
		for line_id in range(len(self.sequences)):
			position = Vec2(MARGIN + self.text_width + max([slot.size.x for slot in self.slots]),
			                self.line_position_y(line_id))
			if line_id == 0:
				text = TEXT_IF
				position.x -= self.slots[0].size.x
			elif line_id == len(self.slots):
				text = TEXT_ELSE
			else:
				text = TEXT_ELIF
				position.x -= self.slots[line_id].size.x
			draw_text(surface, text, origin + position, 20, align="right", camera=camera)
	
	def button_size(self, button_id: int) -> Vec2:
		button_name = self.buttons[button_id]
		match button_name:
			case "elif_add" | "elif_remove" | "else":
				return BT_SIZE
	
	def button_position(self, button_id: int) -> Vec2:
		button_name = self.buttons[button_id]
		position_x = max([slot.size.x for slot in self.slots]) +\
		             self.text_width + MARGIN + 2 * INNER_MARGIN
		match button_name:
			case "elif_add":
				line_id = button_id // 2
				position_y = self.line_position_y(line_id) +\
				             (self.line_height(line_id) - BT_SIZE.y + INNER_MARGIN) / 2
				if line_id + 1 == len(self.sequences): position_y -= (BT_SIZE.y + INNER_MARGIN) / 2
				return Vec2(position_x, position_y)
			case "elif_remove":
				line_id = (button_id + 1) // 2
				return Vec2(position_x, self.line_position_y(line_id) - BT_SIZE.y / 2)
			case "else":
				line_id = len(self.sequences) - 1
				return Vec2(position_x, self.line_position_y(line_id) - BT_SIZE.y / 2)\
					if self.is_else else\
					Vec2(position_x - BT_SIZE.x - INNER_MARGIN, self.line_position_y(line_id) +
					     self.line_height(line_id) / 2 - BT_SIZE.y)
	
	def draw_button(self, surface: Surface, camera: Camera, origin: Vec2, hovered: bool, button_id: int):
		button_name = self.buttons[button_id]
		position = self.button_position(button_id)
		size = self.button_size(button_id)
		
		match button_name:
			case "elif_add":
				color = darker(ELIF_COLOR, .7) if hovered else ELIF_COLOR
				draw_rect(surface, camera, color, origin + position, size, border_radius=SMALL_RADIUS)
				
				color = darker(ELIF_COLOR, .7 * .6) if hovered else darker(ELIF_COLOR, .6)
				draw_line(surface, camera, color,
				          origin + position + Vec2(3, size.y / 2),
				          origin + position + Vec2(size.x - 3, size.y / 2), 2)
				draw_line(surface, camera, color,
				          origin + position + Vec2(size.x / 2, 3),
				          origin + position + Vec2(size.x / 2, size.y - 3), 2)
			case "elif_remove":
				color = darker(ELIF_COLOR, .7) if hovered else ELIF_COLOR
				draw_rect(surface, camera, color, origin + position, size, border_radius=SMALL_RADIUS)
				
				color = darker(ELIF_COLOR, .7 * .6) if hovered else darker(ELIF_COLOR, .6)
				draw_line(surface, camera, color,
				          origin + position + Vec2(3, size.y / 2),
				          origin + position + Vec2(size.x - 3, size.y / 2), 2)
			case "else":
				color = darker(ELSE_COLOR, .7) if hovered else ELSE_COLOR
				draw_rect(surface, camera, color, origin + position, size, border_radius=SMALL_RADIUS)
				
				color = darker(ELSE_COLOR, .7 * .6) if hovered else darker(ELSE_COLOR, .6)
				draw_line(surface, camera, color,
				          origin + position + Vec2(3, size.y / 2),
				          origin + position + Vec2(size.x - 3, size.y / 2), 2)
				if not self.is_else:
					draw_line(surface, camera, color,
					          origin + position + Vec2(size.x / 2, 3),
					          origin + position + Vec2(size.x / 2, size.y - 3), 2)
	
	def button_function(self, button_id: int) -> bool:
		button_name = self.buttons[button_id]
		match button_name:
			case "elif_add":
				line_id = button_id // 2
				self.sequences.insert(line_id + 1, Sequence(ELIF_COLOR))
				self.slots.insert(line_id + 1, Slot(COLOR, "False"))
				self.buttons.insert(button_id, "elif_remove")
				self.buttons.insert(button_id, "elif_add")
				return True
			case "elif_remove":
				line_id = (button_id + 1) // 2
				self.sequences.pop(line_id)
				self.slots.pop(line_id)
				
				self.buttons.pop(button_id)
				self.buttons.pop(button_id)
				return True
			case "else":
				self.is_else = not self.is_else
				if self.is_else:
					self.sequences.append(Sequence(ELSE_COLOR))
				else:
					self.sequences.pop(-1)
				return True
	
	def line_height(self, line_id: int) -> int:
		if line_id == len(self.slots):
			return int(self.sequences[line_id].size.y)
		return int(max(self.slots[line_id].size.y, self.sequences[line_id].size.y))
	
	def line_position_y(self, line_id: int) -> int:
		return int(sum([self.line_height(line) for line in range(line_id + 1)]) +\
		           line_id * INNER_MARGIN - self.line_height(line_id) / 2 + MARGIN)
	
	@property
	def text_width(self) -> int:
		return int(TEXT_ELIF_SIZE.x if len(self.slots) > 1 else TEXT_IF_SIZE.x)
	
	def as_ASTNode(self) -> ASTNodeIfElse:
		elifs = [(slot.as_AST(), sequence.as_AST())
		         for slot, sequence in zip(self.slots[1:], self.sequences[1:])]
		else_sequence = self.sequences[-1].as_AST() if self.is_else else None
		
		return ASTNodeIfElse(self.slots[0].as_AST(), self.sequences[0].as_AST(), elifs, else_sequence)
