from pygame import Vector2 as Vec2, draw

from AST import ASTNode, ASTNodeType
from Containers import HoveredOn

from MyPygameLibrary.App import App
from MyPygameLibrary.Camera import Camera
from MyPygameLibrary.Inputs import Key
from MyPygameLibrary.UI_elements import TextBox, draw_text

from Blocs.ParentBloc import ParentBloc
from Blocs.IfElseBloc import IfElseBloc
from Blocs.VariableAssignmentBloc import VariableAssignmentBloc
from Blocs.SequenceBloc import SequenceBloc
from Blocs.WhileBloc import WhileBloc
from Blocs.VariableReturnBloc import VariableReturnBloc
from Blocs.PrintBloc import PrintBloc

BLOCS = [VariableAssignmentBloc,
         IfElseBloc,
         WhileBloc,
         SequenceBloc,
         VariableReturnBloc,
         PrintBloc]

BLOC_CHOICE_SIZE: Vec2 = Vec2(150, 30)


class DynamicUI(App):
	def __init__(self):
		super().__init__("Dynamic UI", "grey 40", fps=120, quit_on_escape=False)
		
		self.ui_objects["bt_reset"].text = "CLEAR"
		
		self.camera = Camera(self.window_size, zoom_speed=2 ** (1 / 8), vertical_scroll=True,
		                     min_scale=1 / 2, max_scale=2,
		                     left_limit=-2000, right_limit=2000, top_limit=-1000, bottom_limit=4000)
		self.rot = 0
		
		self.blocs: list[tuple[Vec2, ParentBloc]] = [(Vec2(0, 0), SequenceBloc())]
		self.selected_bloc: tuple[Vec2, ParentBloc] = None
		
		self.bloc_hovered = None
		self.mouse_hovered = None
		
		self.text_box: TextBox | None = None
		self.text_box_bloc: int | None = None
		self.AST = self.generateAST()
	
	def reset(self):
		"""Vide la scène de tous les blocs."""
		self.blocs = [(Vec2(0, 0), SequenceBloc())]
		self.selected_bloc = None
		self.text_box = None
		self.text_box_bloc = None
		
		self.bloc_hovered = None
		self.mouse_hovered = None
		
		self.changed = True
	
	def update(self, delta):
		super().update(delta)
		
		if self.input.K_ESCAPE == Key.CLICKED:
			if self.text_box is None:
				self.running = False
				return
			if self.text_box is not None:
				self.text_box.unselect()
				self.text_box = None
			self.text_box_bloc = None
			self.AST = self.generateAST()
			self.changed = True
		elif self.input.K_RETURN == Key.CLICKED:
			if self.text_box is not None and self.text_box_bloc is None:
				self.add_a_bloc()
			elif self.text_box is not None:
				self.text_box.unselect()
			self.text_box = None
			self.text_box_bloc = None
			self.AST = self.generateAST()
			self.changed = True
		
		if self.selected_bloc is None:
			self.camera.update(self.input)
			if self.camera.changed: self.changed = True
		
		if self.input.mouse.K_RIGHT == Key.CLICKED:
			self.mouse_right_click()
			self.changed = True
		elif self.input.mouse.K_LEFT == Key.CLICKED:
			self.mouse_left_click()
			self.mouse_hovered = None
			self.changed = True
		elif self.input.mouse.K_LEFT == Key.UNCLICKED and self.selected_bloc is not None:
			self.release_bloc()
			self.bloc_hovered = None
			self.changed = True
		
		if self.text_box is not None:
			self.text_box.update(delta, self.input)
			if self.text_box.changed:
				self.changed = True
			if self.text_box.size_changed and self.text_box_bloc is not None:
				self.blocs[self.text_box_bloc][1].update_size()
		
		if not ((self.input.mouse.delta and
		         not (self.text_box is not None and self.text_box_bloc is None))
		        or self.input.mouse.K_LEFT in [Key.CLICKED, Key.UNCLICKED]):
			return
		
		if self.selected_bloc is None:
			self.mouse_hover()
		else:
			self.bloc_hover()
			position, _ = self.selected_bloc
			position += self.input.mouse.delta / self.camera.scale
			self.changed = True
			"""
			if self.input.K_CONTROL != Key.DOWN:
				position, _ = self.selected_bloc
				position.y += -20 * self.input.mouse.scroll / self.camera.scale
			"""
	
	def mouse_right_click(self):
		"""Gère le clic droit de la souris."""
		if self.text_box is not None:
			self.text_box.unselect()
			self.text_box = None
			self.text_box_bloc = None
		
		self.text_box = TextBox(
		  self.input.mouse.position - BLOC_CHOICE_SIZE / 2, BLOC_CHOICE_SIZE,
		  default_text="Enter bloc type", selected=True, corner_radius=3)
	
	def mouse_left_click(self):
		"""Gère le clic gauche de la souris."""
		if self.text_box is not None:
			self.text_box.unselect()
			self.text_box = None
			self.text_box_bloc = None
		
		if self.mouse_hovered is None: return
		if self.mouse_hovered == (0, [], (HoveredOn.SEQUENCE, 0)): return
		
		bloc_id, hierarchy, hovered_on = self.mouse_hovered
		position, bloc = self.blocs[bloc_id]
		
		match hovered_on[0]:
			case HoveredOn.SELF | HoveredOn.SEQUENCE:
				container = bloc.get_container(hierarchy)
				
				if container is None:
					removed_bloc = self.blocs.pop(bloc_id)
				elif type(container) is tuple:  # Séquence
					sequence, sequence_bloc_id = container
					removed_bloc = position +\
					               bloc.get_position(hierarchy), sequence.blocs[sequence_bloc_id]
					sequence.set_empty(sequence_bloc_id)
					bloc.update_size()
				else:  # Slot
					removed_bloc = position + bloc.get_position(hierarchy), container.bloc
					container.set_empty(self.camera)
					bloc.update_size()
				
				self.selected_bloc = removed_bloc
				self.text_box = None
				self.text_box_bloc = None
			
			case HoveredOn.INFO:
				hovered_bloc = bloc.get_bloc(hierarchy)
				print()
				print(hovered_bloc.__class__.__name__, ":")
				print(hovered_bloc.__doc__)
			
			case HoveredOn.CROSS:
				container = bloc.get_container(hierarchy)
				
				if container is None:
					self.blocs.pop(bloc_id)
				elif type(container) is tuple:  # Séquence
					sequence, sequence_bloc_id = container
					sequence.set_empty(sequence_bloc_id)
					bloc.update_size()
				else:  # Slot
					container.set_empty(self.camera)
					bloc.update_size()
				
				self.text_box = None
				self.text_box_bloc = None
				self.AST = self.generateAST()
			
			case HoveredOn.SLOT:
				hovered_bloc = bloc.get_bloc(hierarchy)
				hovered_bloc.slots[hovered_on[1]].text_box.select()
				self.text_box = hovered_bloc.slots[hovered_on[1]].text_box
				self.text_box_bloc = bloc_id
			
			case HoveredOn.OTHER:
				hovered_bloc = bloc.get_bloc(hierarchy)
				if hovered_bloc.button_function(hovered_on[1]):
					bloc.update_size()
					self.AST = self.generateAST()
				
				if hovered_bloc.buttons[hovered_on[1]] == "name_box":
					self.text_box = hovered_bloc.name_box
					self.text_box_bloc = bloc_id
	
	def add_a_bloc(self):
		try:
			value = int(self.text_box.text)
		except ValueError:
			return
		
		if 0 < value <= len(BLOCS):
			bloc_type = BLOCS[value - 1]
		else:
			bloc_type = BLOCS[0]
		new_bloc = bloc_type()
		position = self.camera.screen2world(self.text_box.position + self.text_box.size / 2)
		
		if self.mouse_hovered is None:
			self.blocs.append((position - new_bloc.size / 2, new_bloc))
		else:
			bloc_id, hierarchy, hovered_on = self.mouse_hovered
			bloc = self.blocs[bloc_id][1].get_bloc(hierarchy)
			
			match hovered_on[0]:
				case HoveredOn.SEQUENCE:
					sequence = bloc.sequences[hovered_on[1]]
					sequence_bloc_id = sequence.hovered_gap(
						position - bloc.sequence_position(hovered_on[1]))
					sequence.set_hovered(sequence_bloc_id, Vec2(0, 0))
					sequence.set_bloc(sequence_bloc_id, new_bloc)
					self.blocs[bloc_id][1].update_size()
				case HoveredOn.SLOT:
					slot = bloc.slots[hovered_on[1]]
					slot.set_bloc(new_bloc)
					self.blocs[bloc_id][1].update_size()
				case _:
					self.blocs.append((position - new_bloc.size / 2, new_bloc))
		self.AST = self.generateAST()
	
	def release_bloc(self):
		"""Relâche le bloc sélectionné."""
		self.selected_bloc[1].hovered_on = HoveredOn.NONE, None
		
		if self.bloc_hovered is None:
			self.blocs.append(self.selected_bloc)
		else:
			bloc_id, hierarchy = self.bloc_hovered
			_, bloc = self.blocs[bloc_id]
			
			container = bloc.get_container(hierarchy)
			
			if type(container) is tuple:  # Séquence
				sequence, sequence_bloc_id = container
				sequence.set_bloc(sequence_bloc_id, self.selected_bloc[1])
			else:  # Slot
				container.set_bloc(self.selected_bloc[1])
			
			bloc.update_size()
		
		self.selected_bloc = None
		self.AST = self.generateAST()
	
	def mouse_hover(self):
		"""Attribue quel bloc est survolé par la souris."""
		new_mouse_hovered = self.get_mouse_hover()
		if new_mouse_hovered == self.mouse_hovered: return
		
		if new_mouse_hovered == (0, [], (HoveredOn.SELF, None)):
			new_mouse_hovered = None
		# if new_mouse_hovered == (0, [], (HoveredOn.SEQUENCE, 0)): return
		
		if self.mouse_hovered is not None:
			bloc_id, hierarchy, _ = self.mouse_hovered
			bloc = self.blocs[bloc_id][1].get_bloc(hierarchy)
			bloc.hovered_on = HoveredOn.NONE, None
		
		if new_mouse_hovered is not None:
			bloc_id, hierarchy, hovered_on = new_mouse_hovered
			bloc = self.blocs[bloc_id][1].get_bloc(hierarchy)
			bloc.hovered_on = hovered_on
		
		self.mouse_hovered = new_mouse_hovered
		self.changed = True
	
	def get_mouse_hover(self) -> tuple[int, list[int], str | None] | None:
		"""Renvoie la référence du bloc en collision avec la souris et sur quelle partie du bloc elle est."""
		mouse_world_position = self.camera.screen2world(self.input.mouse.position)
		
		for i, (position, bloc) in enumerate(reversed(self.blocs)):
			hierarchy_hovered_on = bloc.collide_point(mouse_world_position - position)
			if hierarchy_hovered_on is not None:
				hierarchy, hovered_on = hierarchy_hovered_on
				return len(self.blocs) - 1 - i, list(reversed(hierarchy)), hovered_on
		return None
	
	def bloc_hover(self):
		"""Attribue quel slot de quel bloc est survolé par le bloc sélectionné."""
		new_bloc_hovered = self.get_bloc_hover()
		if new_bloc_hovered == self.bloc_hovered: return
		
		if self.bloc_hovered is not None:
			bloc_id, hierarchy = self.bloc_hovered
			_, bloc = self.blocs[bloc_id]
			container = bloc.get_container(hierarchy)
			
			if type(container) is tuple:  # Séquence
				sequence, sequence_bloc_id = container
				sequence.set_empty(sequence_bloc_id)
			else:  # Slot
				container.set_empty(self.camera)
			bloc.update_size()
		
		if new_bloc_hovered is not None:
			bloc_id, hierarchy = new_bloc_hovered
			_, bloc = self.blocs[bloc_id]
			container = bloc.get_container(hierarchy)
			
			if type(container) is tuple:  # Séquence
				sequence, sequence_bloc_id = container
				sequence.set_hovered(sequence_bloc_id, self.selected_bloc[1].size)
			else:  # Slot
				container.set_hovered(self.selected_bloc[1].size)
			bloc.update_size()
		
		self.bloc_hovered = new_bloc_hovered
	
	def get_bloc_hover(self) -> tuple[int, list[int]] | None:
		"""Renvoie la référence du slot en collision avec le bloc sélectionné."""
		selected_position, selected = self.selected_bloc
		
		ratio = 0
		bloc_id_hierarchy = None
		for i, (position, bloc) in enumerate(self.blocs):
			hierarchy_ratio = bloc.hovered_slot(selected_position - position, selected.size, ratio)
			
			if hierarchy_ratio is not None and hierarchy_ratio[1] > ratio:
				hierarchy, ratio = hierarchy_ratio
				bloc_id_hierarchy = i, list(reversed(hierarchy))
		
		return bloc_id_hierarchy
	
	def draw_world(self):
		self.draw_grid(draw_border=True)
		
		for position, bloc in self.blocs:
			bloc.draw(self.window_surface, self.camera, position)
		
		if self.selected_bloc is not None:
			position, bloc = self.selected_bloc
			bloc.draw(self.window_surface, self.camera, position, selected=True)
		
		if self.text_box is not None and self.text_box_bloc is None:
			self.text_box.draw(self.window_surface)
		
		self.draw_clock()
		"""
		for i, node in enumerate(self.AST.data):
			draw_text(self.window_surface, node, Vec2(20, 160 + i * 20), size=15, align="left",
			          framed=True, back_framed=True, back_frame_color="grey 80")
		"""
		# print(self.AST)
	
	def draw_ui(self):
		super().draw_ui()
		text = "   ".join([f"({i + 1} {bloc_type.__name__[:-4]})" for i, bloc_type in enumerate(BLOCS)])
		draw_text(self.window_surface, text, Vec2(200, 50), size=15, align="left",
		          framed=True, back_framed=True, back_frame_color="grey 80")
	
	def draw_clock(self):
		n = 12
		center = Vec2(100, 110)
		draw.circle(self.window_surface, "light grey", center, 30)
		[draw.line(self.window_surface, "black", center + Vec2(22, 0).rotate(a * 360 / n),
		           center + Vec2(28, 0).rotate(a * 360 / n), 2) for a in range(n)]
		draw.circle(self.window_surface, "black", center, 30, 2)
		draw.circle(self.window_surface, "red", center, 5)
		draw.line(self.window_surface, "red", center, center + Vec2(24, 0).rotate(self.rot), 3)
		self.rot += 360 / n
	
	def generateAST(self) -> ASTNode:
		"""Retourne l’Abstract Syntax Tree du programme de la séquence parent."""
		abstract_syntax_tree = ASTNode(ASTNodeType.SEQUENCE, [])
		
		for bloc in self.blocs[0][1].sequences[0].blocs:
			abstract_syntax_tree.data.append(bloc.as_ASTNode())
		
		return abstract_syntax_tree


"""
temps = [(time.perf_counter(), "t0")]
add_time(temps, "update")


def add_time(temps: list, name: str = "-"):
	temps.append((time.perf_counter() - temps[0][0], name))


def print_times(temps: list):
	temps = [temps[1]] +\
	        [(temps[i + 2][0] - temps[i + 1][0], temps[i + 2][1])
	         for i in range(len(temps) - 2)]
	
	print(' '.join([f"{name}=[{1000 * t:.3f}]" for t, name in temps]))
"""
