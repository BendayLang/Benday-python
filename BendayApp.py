from pygame import Vector2 as Vec2, draw

from AST import ASTNode, ASTNodeType
from Constantes import FONT_20
from Containers import HoveredOn

from MyPygameLibrary.App import App
from MyPygameLibrary.Camera import Camera
from MyPygameLibrary.Inputs import Key
from MyPygameLibrary.UI_elements import Button, RollingList, TextBox, draw_text

from Blocs.ParentBloc import ParentBloc
from Blocs.IfElseBloc import IfElseBloc
from Blocs.VariableAssignmentBloc import VariableAssignmentBloc
from Blocs.SequenceBloc import SequenceBloc
from Blocs.WhileBloc import WhileBloc
from Blocs.VariableReturnBloc import VariableReturnBloc
from Blocs.PrintBloc import PrintBloc
from executor import exec_ast
from fuzzy_finder import fuzzy_find

BLOCS = [VariableAssignmentBloc,
         IfElseBloc,
         WhileBloc,
         SequenceBloc,
         VariableReturnBloc,
         PrintBloc]

BLOCS_NAMES = [bloc.__name__ for bloc in BLOCS]

BLOC_CHOICE_SIZE: Vec2 = Vec2(150, 30)
ROLLING_LIST_SIZE: Vec2 = Vec2(210, 100)

INFO_TIME: int = 800
MARGIN: Vec2 = Vec2(5)


class BendayApp(App):
	"""Classe principale de l’application Benday.
	Logiciel de programmation visuel et dynamique."""
	
	def __init__(self):
		super().__init__("Dynamic UI", "grey 40", fps=120, quit_on_escape=False)
		
		self.ui_objects["bt_reset"].text = "CLEAR"
		
		self.ui_objects["bt_play"] = Button("tomato", Vec2(300, 50), Vec2(100, 40), text="PLAY")
		
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
		self.rolling_list: RollingList = None
		
		self.info_timer: int = 0
		
		self.AST = self.generate_AST()
	
	def reset(self):
		"""Vide la scène de tous les blocs."""
		self.blocs = [(Vec2(0, 0), SequenceBloc())]
		self.selected_bloc = None
		self.text_box = None
		self.text_box_bloc = None
		
		self.bloc_hovered = None
		self.mouse_hovered = None
		
		self.info_timer = 0
		self.changed = True
		self.AST = self.generate_AST()
	
	def update(self, delta):
		super().update(delta)
		
		if self.text_box is not None:
			self.text_box.update(delta, self.inputs)
			if self.text_box.changed:
				self.changed = True
			if self.text_box.size_changed and self.text_box_bloc is not None:
				self.blocs[self.text_box_bloc][1].update_size()
		
		if self.rolling_list is not None:
			self.rolling_list.update(delta, self.inputs)
			if self.text_box.text_changed:
				self.rolling_list.change_words(fuzzy_find(BLOCS_NAMES, self.text_box.text))
			if self.rolling_list.changed and self.rolling_list.selected_text is not None:
				self.text_box.text = self.rolling_list.selected_text
				self.text_box.changed = True
				self.changed = True
		
		if self.inputs.K_ESCAPE == Key.CLICKED:
			if self.text_box is None:
				self.running = False
				return
			self.update_AST()
		elif self.inputs.K_RETURN == Key.CLICKED:
			if self.rolling_list is not None:
				if self.rolling_list.selected_word is not None:
					if self.text_box.text == self.rolling_list.selected_text:
						self.add_a_bloc()
						self.update_AST()
					else:
						self.text_box.text = self.rolling_list.selected_text
						self.text_box.changed = True
						self.changed = True
				else:
					self.rolling_list.selected_word = 0
					self.text_box.text = self.rolling_list.selected_text
					self.text_box.changed = True
					self.changed = True
			elif self.text_box is not None:
				if self.text_box_bloc is None:
					self.add_a_bloc()
				self.update_AST()
		elif self.inputs.K_DOWN == Key.CLICKED:
			if self.rolling_list is not None and self.rolling_list.selected_word is None:
				self.rolling_list.selected_word = 0
				self.text_box.text = self.rolling_list.selected_text
				self.text_box.changed = True
				self.changed = True
		
		if self.ui_objects["bt_play"].state == Key.UNCLICKED:
			exec_ast(self.AST)
		
		# Retourne si un ou des éléments d’UI ont été bougés.
		if self.changed: return
		
		if self.selected_bloc is None:
			self.camera.update(self.inputs)
			if self.camera.changed: self.changed = True
		
		if self.inputs.mouse.K_RIGHT == Key.CLICKED:
			self.mouse_right_click()
			self.changed = True
		elif self.inputs.mouse.K_LEFT == Key.CLICKED:
			self.mouse_left_click()
			self.mouse_hovered = None
			self.changed = True
		elif self.inputs.mouse.K_LEFT == Key.UNCLICKED and self.selected_bloc is not None:
			self.release_bloc()
			self.bloc_hovered = None
			self.changed = True
		
		if self.mouse_hovered is not None:
			if self.mouse_hovered[2] == (HoveredOn.INFO, None):
				if self.info_timer <= INFO_TIME <= self.info_timer + delta:
					self.changed = True
				self.info_timer += delta
		
		if not ((self.inputs.mouse.delta and
		         not (self.text_box is not None and self.text_box_bloc is None))
		        or self.inputs.mouse.K_LEFT in [Key.CLICKED, Key.UNCLICKED]):
			return
		
		if self.selected_bloc is None:
			self.mouse_hover()
		else:
			self.bloc_hover()
			position, _ = self.selected_bloc
			position += self.inputs.mouse.delta / self.camera.scale
			self.changed = True
	
	def mouse_right_click(self):
		"""Gère le clic droit de la souris."""
		self.update_AST()
		
		position = self.inputs.mouse.position - BLOC_CHOICE_SIZE / 2
		self.text_box = TextBox(
		  position, BLOC_CHOICE_SIZE,
		  default_text="Enter bloc type", selected=True, corner_radius=3)
		
		self.rolling_list = RollingList(
		  position + Vec2(0, BLOC_CHOICE_SIZE.y - 1), ROLLING_LIST_SIZE,
		  BLOCS_NAMES, corner_radius=3)
	
	def mouse_left_click(self):
		"""Gère le clic gauche de la souris."""
		self.update_AST()
		
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
				self.update_AST()
			
			case HoveredOn.INFO:
				self.info_timer = INFO_TIME
				self.changed = True
			
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
				
				self.update_AST()
			
			case HoveredOn.SLOT:
				hovered_bloc = bloc.get_bloc(hierarchy)
				hovered_bloc.slots[hovered_on[1]].text_box.select()
				self.text_box = hovered_bloc.slots[hovered_on[1]].text_box
				self.text_box_bloc = bloc_id
				# TODO add rolling_list
			
			case HoveredOn.OTHER:
				hovered_bloc = bloc.get_bloc(hierarchy)
				if hovered_bloc.button_function(hovered_on[1]):
					bloc.update_size()
					self.update_AST()
				
				if hovered_bloc.buttons[hovered_on[1]] == "name_box":
					self.text_box = hovered_bloc.name_box
					self.text_box_bloc = bloc_id
	
	def update_AST(self):
		if self.text_box is not None:
			self.text_box.unselect()
		self.text_box = None
		self.text_box_bloc = None
		self.rolling_list = None
		self.AST = self.generate_AST()
		self.changed = True
	
	def add_a_bloc(self):
		try:
			index = BLOCS_NAMES.index(self.text_box.text)
		except ValueError:
			return
		
		bloc_type = BLOCS[index]
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
		
		self.update_AST()
	
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
		self.update_AST()
	
	def mouse_hover(self):
		"""Attribue quel bloc est survolé par la souris."""
		new_mouse_hovered = self.get_mouse_hover()
		if new_mouse_hovered == self.mouse_hovered: return
		
		if new_mouse_hovered == (0, [], (HoveredOn.SELF, None)):
			new_mouse_hovered = None
		
		if self.mouse_hovered is not None:
			bloc_id, hierarchy, _ = self.mouse_hovered
			bloc = self.blocs[bloc_id][1].get_bloc(hierarchy)
			bloc.hovered_on = HoveredOn.NONE, None
		
		if new_mouse_hovered is not None:
			bloc_id, hierarchy, hovered_on = new_mouse_hovered
			bloc = self.blocs[bloc_id][1].get_bloc(hierarchy)
			bloc.hovered_on = hovered_on
			if self.mouse_hovered is not None:
				self.info_timer = 0
		
		self.mouse_hovered = new_mouse_hovered
		self.changed = True
	
	def get_mouse_hover(self) -> tuple[int, list[int], str | None] | None:
		"""Renvoie la référence du bloc en collision avec la souris et sur quelle partie du bloc elle est."""
		mouse_world_position = self.camera.screen2world(self.inputs.mouse.position)
		
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
		
		if self.mouse_hovered is not None and self.info_timer >= INFO_TIME:
			bloc_id, hierarchy, _ = self.mouse_hovered
			bloc_position, bloc = self.blocs[bloc_id]
			hovered_bloc = bloc.get_bloc(hierarchy)
			title = f"{hovered_bloc.__class__.__name__}".upper()
			text = f"{title}\n{hovered_bloc.__doc__}".replace("\t", "").split("\n")
			
			size = Vec2(max([FONT_20.size(line)[0] for line in text]), len(text) * FONT_20.get_height())
			position = self.camera.world2screen(
			  bloc_position + bloc.get_position(hierarchy) +
			  bloc.top_box_position + bloc.info_bt_position) - size / 2 - Vec2(0, 50)
			
			draw.rect(self.window_surface, "white", (position - MARGIN, size + 2 * MARGIN), 0, 5)
			draw.rect(self.window_surface, "black", (position - MARGIN, size + 2 * MARGIN), 1, 5)
			for i, line in enumerate(text):
				draw_text(self.window_surface, line, position + (i + .5) * Vec2(0, FONT_20.get_height()),
				          20, align="left", bold=i == 0)
		
		if self.selected_bloc is not None:
			position, bloc = self.selected_bloc
			bloc.draw(self.window_surface, self.camera, position, selected=True)
		
		if self.text_box is not None and self.text_box_bloc is None:
			self.text_box.draw(self.window_surface)
		if self.rolling_list is not None:
			self.rolling_list.draw(self.window_surface)
		
		self.draw_clock()
		"""
		for i, node in enumerate(self.AST.data):
			draw_text(self.window_surface, node, Vec2(20, 160 + i * 20), size=15, align="left",
			          framed=True, back_framed=True, back_frame_color="grey 80")
		"""
	
	def draw_ui(self):
		text = "   ".join([f"({i + 1} {bloc_type.__name__[:-4]})" for i, bloc_type in enumerate(BLOCS)])
		draw_text(self.window_surface, text, Vec2(200, 50), size=15, align="left",
		          framed=True, back_framed=True, back_frame_color="grey 80")
		super().draw_ui()
	
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
	
	def generate_AST(self) -> ASTNode:
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
