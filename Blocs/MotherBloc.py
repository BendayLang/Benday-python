from dataclasses import dataclass

from pygame import Color, Surface, Vector2 as Vec2

from AST import ASTNodeSequence
from Constantes import MARGIN, RADIUS
from Blocs.ParentBloc import ParentBloc, TOP_BOX_SIZE
from Containers import HoveredOn
from MyPygameLibrary.Camera import Camera
from MyPygameLibrary.UI_elements import hsv_color
from MyPygameLibrary.World import draw_rect

COLOR: Color = hsv_color(180, 10, 100)


@dataclass
class MotherBloc(ParentBloc):
	"""Bloc de logique - si la variable booléenne sur le côté gauche du bloc est vraie,
	la séquence du haut est exécutée, sinon la séquence du haut est exécutée."""
	
	def __init__(self):
		super().__init__(COLOR, 0, 1)
	
	def __repr__(self):
		return f"Mother( {self.sequences[0]} )"
	
	def get_size(self) -> Vec2:
		return self.sequences[0].size + Vec2(2, 2) * MARGIN
	
	def sequence_position(self, sequence_id: int) -> Vec2:
		return Vec2(1, 1) * MARGIN
	
	def collide(self, point: Vec2) -> bool:
		"""Retourne si le point donné (en référence au bloc) est dans le bloc."""
		if not (0 <= point.x <= self.size.x and -TOP_BOX_SIZE.y <= point.y <= self.size.y): return False
		
		if point.y >= 0: return True
		
		if self.hovered_on[0] != HoveredOn.NONE:
			return 0 <= point.x - self.top_box_position.x <= TOP_BOX_SIZE.x
		
		if self.sequences[0].blocs and type(self.sequences[0].blocs[0]) is not Vec2:
			return self.sequences[0].blocs[0].collide(point - self.sequence_position(0))
		
		return False
	
	def draw(self, surface: Surface, camera: Camera, origin: Vec2, selected: bool = False):
		"""Affiche le bloc."""
		draw_rect(surface, camera, self.color, origin, self.size, 0, RADIUS)
		
		hovered = self.hovered_on[0] is not HoveredOn.NONE
		self.sequences[0].draw(surface, camera, origin + self.sequence_position(0), hovered)
	
	def as_ASTNode(self) -> ASTNodeSequence:
		return self.sequences[0].as_AST()
