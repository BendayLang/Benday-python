from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any
from pygame import Color, Rect, Surface, Vector2 as Vec2

from AST import ASTNodeSequence, ASTNodeValue
from Constantes import RADIUS, SMALL_RADIUS

from MyPygameLibrary.Camera import Camera
from MyPygameLibrary.UI_elements import TextBox, change_color, darker
from MyPygameLibrary.World import draw_rect

SLOT_SIZE: Vec2 = Vec2(80, 25)
SEQUENCE_SIZE: Vec2 = Vec2(120, 80)

SEQUENCE_MARGIN: int = 7


class HoveredOn(Enum):
	NONE = auto()
	SELF = auto()
	CROSS_BT = auto()
	COPY_BT = auto()
	INFO_BT = auto()
	SLOT = auto()
	SEQUENCE = auto()
	OTHER = auto()


@dataclass(slots=True)
class Slot:
	"""Compartiment pouvant contenir du texte, un bloc ou être vide."""
	text_box: TextBox
	bloc: Any | None
	
	def __init__(self, color: Color, default_text: str = ""):
		self.text_box = TextBox(
		  None, SLOT_SIZE,
		  change_color(color, s_fonc=lambda s: s * .3, v_fonc=lambda _: 1),
		  darker(color, .8), default_text=default_text,
		  fixed_size=False, text_size=16, corner_radius=SMALL_RADIUS, border=0)
		self.bloc = None
	
	def __repr__(self):
		if self.bloc is not None:
			return f"{self.bloc}"
		elif self.text_box.text:
			return self.text_box.text
		else:
			return "-"
	
	@property
	def size(self) -> Vec2:
		"""Retourne la taille du slot."""
		if self.bloc is None:
			return self.text_box.size
		return self.bloc.size
	
	def update_size(self):
		"""Met à jour la taille du slot."""
		if self.bloc is None: return
		self.bloc.update_size()
	
	def collide(self, point: Vec2) -> bool:
		"""Retourne si le point donné (en référence au slot) est dans le slot."""
		return 0 <= point.x <= self.size.x and 0 <= point.y <= self.size.y
	
	def collide_point(self, point: Vec2, slot_id: int):
		"""Renvoie la référence du bloc en collision avec un point et sur quelle partie du bloc est ce point."""
		if self.bloc is None:
			if self.collide(point):
				return [], (HoveredOn.SLOT, slot_id)
			return None
		
		bloc_collide = self.bloc.collide_point(point)
		if bloc_collide is None: return None
		
		hierarchy, hovered_on = bloc_collide
		hierarchy.append(slot_id)
		return hierarchy, hovered_on
	
	def hovered_slot(self, position: Vec2, size: Vec2, ratio: float, slot_id: int)\
	  -> tuple[list[int], float] | None:
		"""Renvoie la référence du slot en collision avec un rectangle et la proportion de collision."""
		slot_rect = Rect((0, 0), self.size)
		if not slot_rect.colliderect(Rect(position, size)): return None
		
		if self.bloc is None:
			collision_rect = slot_rect.clip(Rect(position, size))
			new_ratio = collision_rect.height / slot_rect.height
			if new_ratio > ratio:
				return [slot_id], new_ratio
		else:
			slot_hovered = self.bloc.hovered_slot(position, size, ratio)
			if slot_hovered is not None:
				hierarchy, new_ratio = slot_hovered
				if new_ratio > ratio:
					hierarchy.append(slot_id)
					return hierarchy, new_ratio
		return None
	
	def set_empty(self, camera: Camera | None):
		"""Vide le slot de son contenu."""
		self.bloc = None
		self.text_box.size.y = SLOT_SIZE.y
		self.text_box.update_size(camera)
		self.text_box.corner_radius = SMALL_RADIUS
		self.text_box.hovered = False
	
	def set_hovered(self, size: Vec2):
		"""Définit le slot comme étant survolé."""
		self.text_box.size = size.copy()
		self.text_box.corner_radius = RADIUS
		self.text_box.hovered = True
	
	def set_bloc(self, bloc: Any):
		"""Ajoute un bloc donné dans le slot."""
		self.bloc = bloc
	
	def draw(self, surface: Surface, camera: Camera, position: Vec2, hovered: bool = False):
		"""Affiche le slot."""
		if self.bloc is None:
			self.text_box.draw(surface, camera, position)
		else:
			self.bloc.draw(surface, camera, position)
		
		if hovered:
			draw_rect(surface, camera, "black", position, self.size, 1, SMALL_RADIUS)
	
	def as_AST(self) -> ASTNodeValue | Any:
		"""Retourne l’ASTNode de la séquence."""
		if self.bloc is None:
			return ASTNodeValue(self.text_box.text if self.text_box.text else None)
		else:
			return self.bloc.as_ASTNode()


@dataclass(slots=True)
class Sequence:
	"""Séquence de blocs."""
	color: Color
	blocs: list[Any | Vec2] = field(default_factory=list)
	
	def __repr__(self):
		return " , ".join([f"{bloc}" for bloc in self.blocs])
	
	@property
	def size(self) -> Vec2:
		"""Retourne la taille de la séquence."""
		if not self.blocs: return SEQUENCE_SIZE
		
		width = max([self.bloc_size(i).x for i in range(len(self.blocs))])
		height = max(sum([self.bloc_size(i).y for i in range(len(self.blocs))]), SEQUENCE_SIZE.y)
		
		return Vec2(width, height) + Vec2(1, len(self.blocs)) * SEQUENCE_MARGIN
	
	def bloc_size(self, bloc_id: int) -> Vec2:
		"""Retourne la taille du bloc donné."""
		return self.blocs[bloc_id] if type(self.blocs[bloc_id]) is Vec2 else self.blocs[bloc_id].size
	
	def bloc_position(self, bloc_id: int) -> Vec2:
		"""Renvoie la position du bloc donné en référence à la séquence parent."""
		return Vec2(0, sum([self.bloc_size(i).y + SEQUENCE_MARGIN for i in range(bloc_id)]))
	
	def update_size(self):
		"""Met à jour la taille de la séquence."""
		for bloc in self.blocs:
			if type(bloc) is Vec2: continue
			bloc.update_size()
	
	def collide(self, point: Vec2) -> bool:
		"""Retourne si le point donné (en référence à la séquence) est dans la séquence."""
		return 0 <= point.x <= self.size.x and 0 <= point.y <= self.size.y
	
	def collide_point(self, point: Vec2, sequence_id: int):
		"""Renvoie la référence du bloc en collision avec un point et sur quelle partie du bloc est ce point."""
		for i, bloc in enumerate(reversed(self.blocs)):
			if type(bloc) is Vec2: continue
			
			bloc_id = len(self.blocs) - 1 - i
			bloc_position = self.bloc_position(bloc_id)
			
			bloc_collide = bloc.collide_point(point - bloc_position)
			if bloc_collide is None: continue
			
			hierarchy, hovered_on = bloc_collide
			hierarchy.append((sequence_id, bloc_id))
			return hierarchy, hovered_on
		
		if self.collide(point):
			return [], (HoveredOn.SEQUENCE, sequence_id)
		return None
	
	def hovered_slot(self, position: Vec2, size: Vec2, ratio: float, sequence_id: int)\
	  -> tuple[list[int], float] | None:
		"""Renvoie la référence du slot en collision avec un rectangle et la proportion de collision."""
		sequence_rect = Rect((0, 0), self.size)
		if not sequence_rect.colliderect(Rect(position, size)): return None
		hierarchy_ratio = None
		
		hovered_where = self.is_hovered_where()
		
		if not self.blocs:
			delta = position.y - self.bloc_position(0).y
			new_ratio = max(1 - abs(delta / size.y), .1)
			if new_ratio > ratio:
				ratio = new_ratio
				hierarchy_ratio = [(sequence_id, 0)], new_ratio
		
		for i in range(len(self.blocs) + 1):
			if i - 1 == hovered_where: continue
			delta = position.y - self.bloc_position(i).y
			
			if i + 1 == len(self.blocs):
				gap_size = sequence_rect.height + SEQUENCE_MARGIN - self.bloc_position(i).y
			elif i == hovered_where:
				gap_size = self.bloc_position(i + 1).y - self.bloc_position(i).y
			else:
				gap_size = SEQUENCE_MARGIN
			
			if delta + size.y >= 0 and delta <= gap_size:
				new_ratio = max(1 - abs(delta / size.y), .1)
				if new_ratio > ratio:
					ratio = new_ratio
					bloc_id = i
					if hovered_where is not None and i > hovered_where: bloc_id -= 1
					hierarchy_ratio = [(sequence_id, bloc_id)], new_ratio
		
		for i, bloc in enumerate(self.blocs):
			if hovered_where is not None and i == hovered_where: continue
			hovered_slot_result = bloc.hovered_slot(position - self.bloc_position(i), size, ratio)
			if hovered_slot_result is None: continue
			
			hierarchy, new_ratio = hovered_slot_result
			if new_ratio > ratio:
				ratio = new_ratio
				bloc_id = i
				if hovered_where is not None and i > hovered_where: bloc_id -= 1
				hierarchy.append((sequence_id, bloc_id))
				hierarchy_ratio = hierarchy, new_ratio
		
		return hierarchy_ratio
	
	def hovered_gap(self, point: Vec2) -> int:
		"""Retourne l’id du gap survolé par un point donné."""
		if not self.blocs: return 0
		
		for bloc_id, bloc in enumerate(self.blocs):
			if point.y < self.bloc_position(bloc_id).y:
				return bloc_id
		return len(self.blocs)
	
	def is_hovered_where(self) -> int:
		"""Renvoie l’id de l’espace au-dessus duquel le bloc est survolé."""
		for gap_id, bloc in enumerate(self.blocs):
			if type(bloc) is Vec2: return gap_id
		return None
	
	def set_empty(self, bloc_id: int):
		"""Enlève le bloc donné de la séquence."""
		self.blocs.pop(bloc_id)
	
	def set_hovered(self, gap_id: int, size: Vec2):
		"""Ajoute un espace à une position donnée."""
		self.blocs.insert(gap_id, size)
	
	def set_bloc(self, gap_id: int, bloc: Any):
		"""Ajoute un bloc donné à une position donnée dans la séquence."""
		if gap_id == len(self.blocs):
			self.blocs[-1] = bloc
		else:
			self.blocs[gap_id] = bloc
	
	def draw(self, surface: Surface, camera: Camera, position: Vec2, hovered: bool = False):
		"""Affiche la séquence."""
		draw_rect(surface, camera, darker(self.color), position, self.size, 0, RADIUS)
		
		for i, bloc in enumerate(self.blocs):
			if type(bloc) is Vec2:
				draw_rect(surface, camera, darker(self.color, .5),
				          position + self.bloc_position(i),
				          self.bloc_size(i), 0, RADIUS)
			else:
				bloc.draw(surface, camera, position + self.bloc_position(i))
		
		if hovered:
			draw_rect(surface, camera, "black", position, self.size, 1, RADIUS)
	
	def as_AST(self) -> ASTNodeSequence:
		"""Retourne la list contenant les ASTNodes de la séquence."""
		return ASTNodeSequence([bloc.as_ASTNode() for bloc in self.blocs])
