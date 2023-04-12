from dataclasses import dataclass
from typing import Any
from pygame import Color, Surface, Vector2 as Vec2

from AST import ASTNode
from Constantes import MARGIN, RADIUS, SMALL_RADIUS
from Blocs.Containers import HoveredOn, Slot, Sequence

from MyPygameLibrary.Camera import Camera
from MyPygameLibrary.UI_elements import change_color, darker, hsv_color
from MyPygameLibrary.World import draw_circle, draw_line, draw_rect

TOP_BOX_SIZE: Vec2 = Vec2(100, 25)
TOP_BOX_MARGIN: int = 3

INFO_BT_RADIUS: int = int(TOP_BOX_SIZE.y / 2 - TOP_BOX_MARGIN)
COPY_BT_SIZE: Vec2 = (TOP_BOX_SIZE.y - 2 * TOP_BOX_MARGIN) * Vec2(4 / 5, 1)
PAGE_SIZE: Vec2 = COPY_BT_SIZE / 2
PAGE_DELTA: Vec2 = Vec2(2)
CROSS_BT_SIZE: Vec2 = Vec2(TOP_BOX_SIZE.y - 2 * TOP_BOX_MARGIN)

INFO_BT_COLOR: Color = hsv_color(50, 40, 100)
COPY_BT_COLOR: Color = hsv_color(40, 0, 60)
CROSS_BT_COLOR: Color = hsv_color(10, 75, 100)

SHADOW: Vec2 = Vec2(6, 8)


@dataclass(slots=True)
class ParentBloc:
	"""Tout bloc hérite du ParentBloc pour en récupérer ses méthodes de base."""
	color: Color
	slots: list[Slot]
	sequences: list[Sequence]
	
	size: Vec2
	hovered_on: tuple[HoveredOn, int | None]
	buttons: list[str]
	
	def __init__(self, color: Color, slots: list[Slot] | list[str] | int = 0,
	             sequences: list[Sequence] | int = 0, buttons: list[str] = None):
		self.color = color
		if type(slots) is int:
			self.slots = [Slot(color) for _ in range(slots)]
		elif type(slots[0]) is str:
			self.slots = [Slot(color, default_text) for default_text in slots]
		else:
			self.slots = slots
		self.sequences = [Sequence(color)
		                  for _ in range(sequences)] if type(sequences) is int else sequences
		self.size = self.get_size()
		self.hovered_on = HoveredOn.NONE, None
		self.buttons = buttons if buttons is not None else []
	
	def update_size(self):
		"""Met à jour la taille du bloc et celles de ses enfants."""
		for slot in self.slots:
			slot.update_size()
		for sequence in self.sequences:
			sequence.update_size()
		
		self.size = self.get_size()
	
	def get_size(self) -> Vec2:
		"""Retourne la taille du bloc."""
		raise NotImplementedError(f"'get_size' is not implemented in "
		                          f"'{self.__class__.__name__}' class")
	
	def slot_position(self, slot_id: int) -> Vec2:
		"""Retourne la position d’un slot donné en référence à son bloc parent."""
		raise NotImplementedError(f"'slot_position' is not implemented in "
		                          f"'{self.__class__.__name__}' class")
	
	def sequence_position(self, sequence_id: int) -> Vec2:
		"""Retourne la position d’une séquence donnée en référence à son bloc parent."""
		raise NotImplementedError(f"'sequence_position' is not implemented in "
		                          f"'{self.__class__.__name__}' class")
	
	def get_position(self, hierarchy: list[int | tuple[int, int]]) -> Vec2:
		"""Retourne la position d’un bloc selon une hiérarchie.
		Exemple de hiérarchie: [A, (B, C), D] -> Slot A, (Sequence B, Bloc C), Slot D"""
		position = Vec2(0, 0)
		bloc = self
		
		for container_id in hierarchy:
			if type(container_id) is tuple:
				sequence_id, bloc_id = container_id
				
				position += bloc.sequence_position(sequence_id)
				bloc = bloc.sequences[sequence_id]
				
				position += bloc.bloc_position(bloc_id)
				bloc = bloc.blocs[bloc_id]
			else:
				position += bloc.slot_position(container_id)
				bloc = bloc.slots[container_id].bloc
		
		return position
	
	def get_bloc(self, hierarchy: list[int | tuple[int, int]]) -> Any:
		"""Retourne le bloc selon une hiérarchie.
		Exemple de hiérarchie: [A, (B, C), D] -> Slot A, (Sequence B, Bloc C), Slot D"""
		bloc = self
		
		for container_id in hierarchy:
			if type(container_id) is tuple:
				sequence_id, bloc_id = container_id
				bloc = bloc.sequences[sequence_id]
				bloc = bloc.blocs[bloc_id]
			else:
				bloc = bloc.slots[container_id].bloc
		
		return bloc
	
	def get_container(self, hierarchy: list[int | tuple[int, int]])\
	  -> Slot | tuple[Sequence, int] | None:
		"""Retourne le conteneur selon une hiérarchie et None si la hiérarchie est vide.
		Exemple de hiérarchie: [A, (B, C), D] -> Slot A, (Sequence B, Bloc C), Slot D"""
		if not hierarchy: return None
		bloc = self
		
		for container_id in hierarchy[:-1]:
			if type(container_id) is tuple:
				sequence_id, bloc_id = container_id
				bloc = bloc.sequences[sequence_id]
				bloc = bloc.blocs[bloc_id]
			else:
				bloc = bloc.slots[container_id].bloc
		
		if type(hierarchy[-1]) is tuple:
			sequence_id, bloc_id = hierarchy[-1]
			return bloc.sequences[sequence_id], bloc_id
		else:
			return bloc.slots[hierarchy[-1]]
	
	def collide(self, point: Vec2) -> bool:
		"""Retourne si le point donné (en référence au bloc) est dans le bloc."""
		if not (0 <= point.x <= self.size.x and -TOP_BOX_SIZE.y <= point.y <= self.size.y): return False
		
		if point.y >= 0: return True
		
		if self.hovered_on[0] != HoveredOn.NONE:
			return 0 <= point.x - self.top_box_position.x <= TOP_BOX_SIZE.x
		
		if self.slots:
			slot = self.slots[0]
			if slot.bloc is not None:
				return slot.bloc.collide(point - self.slot_position(0))
		
		if self.sequences:
			sequence = self.sequences[0]
			if sequence.blocs:
				bloc = sequence.blocs[0]
				if type(bloc) is not Vec2:
					return bloc.collide(point - self.sequence_position(0))
		
		return False
	
	def collide_point(self, point: Vec2)\
	  -> tuple[list[int | tuple[int, int]], tuple[HoveredOn, int | None]] | None:
		"""Retourne la référence du bloc en collision avec un point (hiérarchie)
		et sur quelle partie du bloc est ce point (hovered on)."""
		if not self.collide(point): return None
		
		for button_id in range(len(self.buttons)):
			if self.collide_button(point, button_id):
				return [], (HoveredOn.OTHER, button_id)
		
		for i, slot in enumerate(reversed(self.slots)):
			slot_id = len(self.slots) - 1 - i
			slot_collide = slot.collide_point(point - self.slot_position(slot_id), slot_id)
			if slot_collide is not None:
				return slot_collide
		
		for i, sequence in enumerate(reversed(self.sequences)):
			sequence_id = len(self.sequences) - 1 - i
			slot_collide = sequence.collide_point(point - self.sequence_position(sequence_id),
			                                      sequence_id)
			if slot_collide is not None:
				return slot_collide
		
		if self.collide_info_bt(point):
			return [], (HoveredOn.INFO_BT, None)
		
		if self.collide_copy_bt(point):
			return [], (HoveredOn.COPY_BT, None)
		
		if self.collide_cross_bt(point):
			return [], (HoveredOn.CROSS_BT, None)
		
		return [], (HoveredOn.SELF, None)
	
	def hovered_slot(self, position: Vec2, size: Vec2, ratio: float)\
	  -> tuple[list[int | tuple[int, int]], float] | None:
		"""Retourne la référence du slot ou de la séquence en collision avec un rectangle (hiérarchie)
		et la proportion de collision en hauteur (float)."""
		if not (MARGIN - size.x < position.x < self.size.x - 2 * MARGIN and
		        MARGIN - size.y < position.y < self.size.y - 2 * MARGIN): return None
		hierarchy_ratio = None
		
		for slot_id, slot in enumerate(self.slots):
			slot_position = self.slot_position(slot_id)
			
			slot_hovered = slot.hovered_slot(position - slot_position, size, ratio, slot_id)
			if slot_hovered is not None:
				hierarchy, ratio = slot_hovered
				hierarchy_ratio = hierarchy, ratio
		
		for sequence_id, sequence in enumerate(self.sequences):
			sequence_position = self.sequence_position(sequence_id)
			
			sequence_hovered = sequence.hovered_slot(position - sequence_position, size, ratio,
			                                         sequence_id)
			if sequence_hovered is not None:
				hierarchy, ratio = sequence_hovered
				hierarchy_ratio = hierarchy, ratio
		
		return hierarchy_ratio
	
	def draw(self, surface: Surface, camera: Camera, origin: Vec2, selected: bool = False):
		"""Affiche le bloc."""
		if selected:  # SHADOW
			draw_rect(surface, camera, "black", origin, self.size, 0, RADIUS, alpha=80)
			draw_rect(surface, camera, "black", origin + self.top_box_position, TOP_BOX_SIZE, 0,
			          0, RADIUS, RADIUS, 0, alpha=80)
		
		if selected: origin = origin - SHADOW
		
		# Main body
		if self.hovered_on[0] != HoveredOn.NONE:
			self.draw_top_box(surface, camera, origin + self.top_box_position)
			draw_rect(surface, camera, "black", origin + self.top_box_position,
			          TOP_BOX_SIZE + Vec2(0, 3), 1, RADIUS, -1, -1, 0, 0)
		
		draw_rect(surface, camera, self.color, origin, self.size, 0, RADIUS)
		draw_rect(surface, camera, darker(self.color, .8), origin, self.size, 2, RADIUS)
		
		if self.hovered_on[0] != HoveredOn.NONE:
			draw_rect(surface, camera, "black", origin, self.size, 1, RADIUS)
		
		# Slots
		hovered_slot_id = self.hovered_on[1] if self.hovered_on[0] == HoveredOn.SLOT else None
		for i, slot in enumerate(self.slots):
			hovered = i == hovered_slot_id
			slot.draw(surface, camera, origin + self.slot_position(i), hovered)
		
		# Sequences
		hovered_sequence_id = self.hovered_on[1] if self.hovered_on[0] == HoveredOn.SEQUENCE else None
		for i, sequence in enumerate(self.sequences):
			hovered = i == hovered_sequence_id
			sequence.draw(surface, camera, origin + self.sequence_position(i), hovered)
		
		hovered_button_id = self.hovered_on[1] if self.hovered_on[0] == HoveredOn.OTHER else None
		for button_id in range(len(self.buttons)):
			if self.always_draw_button(button_id) or self.hovered_on[0] != HoveredOn.NONE:
				hovered = button_id == hovered_button_id
				self.draw_button(surface, camera, origin, hovered, button_id)
		
		self.post_draw(surface, camera, origin)
	
	def post_draw(self, surface: Surface, camera: Camera, origin: Vec2):
		"""Affiche par-dessus le bloc."""
	
	def draw_top_box(self, surface: Surface, camera: Camera, origin: Vec2):
		color = change_color(self.color, s_fonc=lambda s: s * 0.2, v_fonc=lambda _: .9)
		draw_rect(surface, camera, color, origin, TOP_BOX_SIZE + Vec2(0, 3), 0, RADIUS, -1, -1, 0, 0)
		
		border_width = 1 / camera.scale
		
		# Info button
		color = darker(INFO_BT_COLOR, .7) if self.hovered_on[0] == HoveredOn.INFO_BT else INFO_BT_COLOR
		position = origin + self.info_bt_position
		draw_circle(surface, camera, color, position, INFO_BT_RADIUS)
		draw_circle(surface, camera, "black", position, INFO_BT_RADIUS, border_width)
		draw_line(surface, camera, "black",
		          position + Vec2(-1 / camera.scale, 2 / 4 * INFO_BT_RADIUS),
		          position + Vec2(-1 / camera.scale, -1 / 5 * INFO_BT_RADIUS), 1.5)
		draw_circle(surface, camera, "black", position + Vec2(0, -1 / 2 * INFO_BT_RADIUS), 1.5)
		
		# Copy button
		color = darker(COPY_BT_COLOR, .7) if self.hovered_on[0] == HoveredOn.COPY_BT else COPY_BT_COLOR
		position = origin + self.copy_bt_position
		draw_rect(surface, camera, color, position, COPY_BT_SIZE, border_radius=SMALL_RADIUS)
		color = darker("white", .7) if self.hovered_on[0] == HoveredOn.COPY_BT else "white"
		draw_rect(surface, camera, color, position + PAGE_DELTA, PAGE_SIZE)
		draw_rect(surface, camera, "black", position + PAGE_DELTA, PAGE_SIZE, border_width)
		draw_rect(surface, camera, color, position + PAGE_SIZE - PAGE_DELTA, PAGE_SIZE)
		draw_rect(surface, camera, "black", position + PAGE_SIZE - PAGE_DELTA, PAGE_SIZE, border_width)
		
		# Cross button
		color = darker(CROSS_BT_COLOR, .7) if self.hovered_on[
			                                      0] == HoveredOn.CROSS_BT else CROSS_BT_COLOR
		position = origin + self.cross_bt_position
		draw_rect(surface, camera, color, position, CROSS_BT_SIZE, border_radius=SMALL_RADIUS)
		h = CROSS_BT_SIZE.y / 2 * (1 / 2)
		center = position + CROSS_BT_SIZE / 2
		draw_line(surface, camera, "black", center + (h, h), center + (-h, -h), 1)
		draw_line(surface, camera, "black", center + (-h, h), center + (h, -h), 1)
	
	@property
	def top_box_position(self) -> Vec2:
		return Vec2((self.size.x - TOP_BOX_SIZE.x) / 2, - TOP_BOX_SIZE.y)
	
	@property
	def info_bt_position(self) -> Vec2:
		return Vec2(TOP_BOX_SIZE.y / 2 + 1)
	
	def collide_info_bt(self, point: Vec2) -> bool:
		delta = point - (self.top_box_position + self.info_bt_position)
		return delta.x ** 2 + delta.y ** 2 <= INFO_BT_RADIUS ** 2
	
	@property
	def copy_bt_position(self) -> Vec2:
		return Vec2((TOP_BOX_SIZE.x - COPY_BT_SIZE.x) / 2, TOP_BOX_MARGIN + 1)
	
	def collide_copy_bt(self, point: Vec2) -> bool:
		delta = point - (self.top_box_position + self.copy_bt_position)
		return 0 <= delta.x <= COPY_BT_SIZE.x and 0 <= delta.y <= COPY_BT_SIZE.y
	
	@property
	def cross_bt_position(self) -> Vec2:
		return Vec2(TOP_BOX_SIZE.x - CROSS_BT_SIZE.x - TOP_BOX_MARGIN - 1, TOP_BOX_MARGIN + 1)
	
	def collide_cross_bt(self, point: Vec2) -> bool:
		delta = point - (self.top_box_position + self.cross_bt_position)
		return 0 <= delta.x <= CROSS_BT_SIZE.x and 0 <= delta.y <= CROSS_BT_SIZE.y
	
	def collide_button(self, point: Vec2, button_id: int) -> bool:
		"""Retourne si le point est sur le bouton donné."""
		size = self.button_size(button_id)
		position = self.button_position(button_id)
		return 0 <= point.x - position.x <= size.x and 0 <= point.y - position.y <= size.y
	
	def button_size(self, button_id: int) -> Vec2:
		"""Retourne la taille du bouton donné."""
		raise NotImplementedError(f"'button_size' is not implemented in "
		                          f"'{self.__class__.__name__}' class")
	
	def button_position(self, button_id: int) -> Vec2:
		"""Retourne la position du bouton donné."""
		raise NotImplementedError(f"'button_position' is not implemented in "
		                          f"'{self.__class__.__name__}' class")
	
	def button_function(self, button_id: int) -> bool:
		"""Exécute une fonction selon le bouton donné et renvois si la taille du bloc change."""
		raise NotImplementedError(f"'button_function' is not implemented in "
		                          f"'{self.__class__.__name__}' class")
	
	def draw_button(self, surface: Surface, camera: Camera, origin: Vec2, hovered: bool, button_id: int):
		"""Affiche le bouton donné."""
		raise NotImplementedError(f"'draw_button' is not implemented in "
		                          f"'{self.__class__.__name__}' class")
	
	def always_draw_button(self, button_id: int) -> bool:
		"""Renvoie si le bouton doit toujours être affiché ou seulement quand la souris est par-dessus."""
		return False
	
	def as_ASTNode(self) -> ASTNode:
		"""Retourne l’ASTNode du bloc."""
		raise NotImplementedError(f"'as_ASTNode' is not implemented in "
		                          f"'{self.__class__.__name__}' class")
