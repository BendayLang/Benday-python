from pygame import Vector2 as Vec2, draw
from copy import deepcopy

from Blocs.MotherBloc import MotherBloc
from Constantes import FONT_20, MOTHER_SIZE
from Blocs.Containers import HoveredOn

from MyPygameLibrary.App import App
from MyPygameLibrary.Camera import Camera
from MyPygameLibrary.Inputs import Key
from MyPygameLibrary.UI_elements import Button, RollingList, TextBox, draw_text

from Blocs.ParentBloc import ParentBloc
from Blocs.IfElseBloc import IfElseBloc
from Blocs.VariableAssignmentBloc import VariableAssignmentBloc
from Blocs.SequenceBloc import SequenceBloc
from Blocs.WhileBloc import WhileBloc
from Blocs.ReturnBloc import ReturnBloc
from Blocs.PrintBloc import PrintBloc

BLOCS = [VariableAssignmentBloc,
         IfElseBloc,
         WhileBloc,
         SequenceBloc,
         ReturnBloc,
         PrintBloc]

BLOCS_NAMES = [bloc.__name__.split("Bloc")[0] for bloc in BLOCS]

BLOC_CHOICE_SIZE: Vec2 = Vec2(200, 30)
ROLLING_LIST_HEIGHT: int = 120

INFO_TIME: int = 800
MARGIN: Vec2 = Vec2(5)


class BendayApp(App):
	"""Classe principale de l’application Benday.
	Logiciel de programmation visuel et dynamique."""
	
	def __init__(self):
		super().__init__("Dynamic UI", "grey 40", fps=120, quit_on_escape=False)
		
		self.ui_objects["bt_reset"].text = "CLEAR"
		self.ui_objects["bt_play"] = Button("tomato", Vec2(300, 25), Vec2(100, 40), text="PLAY")
		
		self.camera = Camera(self.window_size, zoom_speed=2 ** (1 / 8), vertical_scroll=True,
		                     min_scale=1 / 2, max_scale=2,
		                     left_limit=-2000, right_limit=2000, top_limit=-1000, bottom_limit=4000)
		
		self.blocs: list[tuple[Vec2, ParentBloc]] = [(-MOTHER_SIZE / 2, MotherBloc())]
		self.selected_bloc: tuple[Vec2, ParentBloc] = None
		
		self.bloc_hovered = None
		self.mouse_hovered = None
		
		self.text_box: TextBox | None = None
		self.text_box_bloc: int | None = None
		self.rolling_list: RollingList = None
		
		self.info_timer: int = 0
		
		self.AST = self.blocs[0][1].as_ASTNode()
		
		self.variables: list[str] = []
	
	def reset(self):
		"""Vide la scène de tous les blocs."""
		self.blocs = [(-MOTHER_SIZE / 2, MotherBloc())]
		self.selected_bloc = None
		self.text_box = None
		self.text_box_bloc = None
		
		self.bloc_hovered = None
		self.mouse_hovered = None
		
		self.info_timer = 0
		self.changed = True
		self.AST = self.blocs[0][1].as_ASTNode()
	
	def manage_inputs(self, delta: int):
		super().manage_inputs(delta)
		
		if self.ui_objects["bt_play"].is_released():
			print("\nEXECUTION :")
			self.AST.execute()
		
		# Retourne si un ou des éléments d’UI ont été bougés.
		if self.changed:
			self.unselect_text_box()
			return
		
		if self.text_box is None:
			if self.inputs.K_ESCAPE == Key.PRESSED: self.running = False
			return
		
		if self.inputs.K_ESCAPE == Key.PRESSED:
			self.unselect_text_box()
			self.changed = True
			return
		
		# Text box
		self.text_box.update(delta, self.inputs)
		if self.text_box.changed:
			self.changed = True
		if self.text_box.size_changed and self.text_box_bloc is not None:
			self.blocs[self.text_box_bloc][1].update_size()
		
		# Rolling list
		if self.rolling_list is None:
			if self.inputs.K_RETURN == Key.PRESSED: self.unselect_text_box()
			return
		
		if self.text_box.text_changed:
			self.rolling_list.update_words(self.text_box.text)
		
		self.rolling_list.update(delta, self.inputs)
		if self.rolling_list.changed:
			self.changed = True
			if self.rolling_list.selected_text is not None:
				self.text_box.text = self.rolling_list.selected_text
				self.text_box.select()
		
		if self.inputs.K_RETURN == Key.PRESSED:
			if self.rolling_list.selected_word is not None:
				if self.text_box.text == self.rolling_list.selected_text:
					if self.text_box_bloc is None:
						self.add_a_bloc()
					self.unselect_text_box()
					return
				else:
					self.text_box.text = self.rolling_list.selected_text
					self.text_box.select()
					self.changed = True
			elif self.rolling_list.words:
				self.rolling_list.selected_word = 0
				self.text_box.text = self.rolling_list.selected_text
				self.text_box.select()
				self.changed = True
			elif self.text_box_bloc is None:
				self.text_box.select()
			else:
				self.unselect_text_box()
	
	def update(self, delta):
		super().update(delta)
		
		# Retourne si un ou des éléments d’UI ont été bougés.
		if self.changed: return
		
		if self.selected_bloc is None and self.text_box is None:
			self.camera.update(self.inputs)
			if self.camera.changed: self.changed = True
		
		if self.inputs.mouse.K_RIGHT == Key.PRESSED:
			self.mouse_right_click()
		elif self.inputs.mouse.K_LEFT == Key.PRESSED:
			self.mouse_left_click()
		elif self.inputs.mouse.K_LEFT == Key.RELEASED:
			self.release_bloc()
		
		if self.mouse_hovered is not None:
			if self.mouse_hovered[2] == (HoveredOn.INFO_BT, None):
				if self.info_timer <= INFO_TIME <= self.info_timer + delta:
					self.changed = True
				self.info_timer += delta
		
		if not ((self.inputs.mouse.delta and
		         not (self.text_box is not None and self.text_box_bloc is None))
		        or self.inputs.mouse.K_LEFT in [Key.PRESSED, Key.RELEASED]):
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
		self.unselect_text_box()
		
		position = self.inputs.mouse.position - BLOC_CHOICE_SIZE / 2
		self.text_box = TextBox(
		  position, BLOC_CHOICE_SIZE,
		  default_text="Enter bloc type", selected=True, corner_radius=3)
		
		self.rolling_list = RollingList(
		  position + Vec2(0, BLOC_CHOICE_SIZE.y - 1), ROLLING_LIST_HEIGHT,
		  BLOCS_NAMES, corner_radius=3)
		
		self.changed = True
	
	def mouse_left_click(self):
		"""Gère le clic gauche de la souris."""
		if self.mouse_hovered in [None, (0, [], (HoveredOn.SEQUENCE, 0))]:
			self.unselect_text_box()
			return
		
		bloc_id, hierarchy, hovered_on = self.mouse_hovered
		position, bloc = self.blocs[bloc_id]
		
		match hovered_on[0]:
			case HoveredOn.SELF | HoveredOn.SEQUENCE:
				self.unselect_text_box()
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
			
			case HoveredOn.INFO_BT:
				self.unselect_text_box()
				self.info_timer = INFO_TIME
			
			case HoveredOn.COPY_BT:
				self.unselect_text_box()
				hovered_bloc = bloc.get_bloc(hierarchy)
				self.selected_bloc = position + bloc.get_position(hierarchy), deepcopy(hovered_bloc)
				hovered_bloc.hovered_on = HoveredOn.NONE, None
			
			case HoveredOn.CROSS_BT:
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
				self.unselect_text_box()
			
			case HoveredOn.SLOT:
				hovered_bloc = bloc.get_bloc(hierarchy)
				hovered_text_box = hovered_bloc.slots[hovered_on[1]].text_box
				if self.text_box is hovered_text_box: return
				self.unselect_text_box()
				self.text_box = hovered_text_box
				self.text_box.select()
				self.text_box_bloc = bloc_id
				
				if self.variables:
					self.rolling_list = RollingList(
					  self.camera.world2screen(
						position + bloc.get_position(hierarchy) +
						hovered_bloc.slot_position(hovered_on[1]) + Vec2(0, self.text_box.size.y)),
					  ROLLING_LIST_HEIGHT, self.variables, corner_radius=3)
			
			case HoveredOn.OTHER:
				hovered_bloc = bloc.get_bloc(hierarchy)
				if hovered_bloc.buttons[hovered_on[1]] == "name_box":
					if self.text_box is hovered_bloc.name_box: return
					self.unselect_text_box()
					self.text_box = hovered_bloc.name_box
					self.text_box.select()
					self.text_box_bloc = bloc_id
					if self.variables:
						self.rolling_list = RollingList(
						  self.camera.world2screen(
							position + bloc.get_position(hierarchy) +
							hovered_bloc.button_position(hovered_on[1]) + Vec2(0, self.text_box.size.y)),
						  ROLLING_LIST_HEIGHT, self.variables, corner_radius=3)
				elif hovered_bloc.button_function(hovered_on[1]):
					bloc.update_size()
					self.update_AST()
		
		self.mouse_hovered = None
		self.changed = True
	
	def unselect_text_box(self):
		"""Désélectionne la boîte de texte actuellement sélectionnée."""
		if self.text_box is not None:
			self.text_box.unselect()
			if self.text_box_bloc is not None:
				self.update_AST()
		self.text_box = None
		self.text_box_bloc = None
		self.rolling_list = None
	
	def update_AST(self):
		"""Met à jour l’Abstract Syntax Tree selon la disposition des blocs actuels."""
		self.AST = self.blocs[0][1].as_ASTNode()
	
	def add_a_bloc(self):
		try:
			index = BLOCS_NAMES.index(self.text_box.text)
		except ValueError:
			return
		
		new_bloc = BLOCS[index]()
		new_bloc_position = self.camera.screen2world(self.text_box.position + self.text_box.size / 2)
		
		if self.mouse_hovered is None:
			self.blocs.append((new_bloc_position - new_bloc.size / 2, new_bloc))
		else:
			bloc_id, hierarchy, hovered_on = self.mouse_hovered
			position, bloc = self.blocs[bloc_id]
			hovered_bloc = bloc.get_bloc(hierarchy)
			
			match hovered_on[0]:
				case HoveredOn.SEQUENCE:
					sequence = hovered_bloc.sequences[hovered_on[1]]
					point = new_bloc_position - position - \
					        bloc.get_position(hierarchy) - bloc.sequence_position(hovered_on[1])
					gap_id = sequence.hovered_gap(point)
					sequence.set_hovered(gap_id, new_bloc)
					self.blocs[bloc_id][1].update_size()
				case HoveredOn.SLOT:
					slot = hovered_bloc.slots[hovered_on[1]]
					slot.set_bloc(new_bloc)
					self.blocs[bloc_id][1].update_size()
				case _:
					self.blocs.append((new_bloc_position - new_bloc.size / 2, new_bloc))
		
		self.update_AST()
	
	def release_bloc(self):
		"""Relâche le bloc sélectionné."""
		if self.selected_bloc is None: return
		
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
		self.bloc_hovered = None
		self.update_AST()
		self.changed = True
	
	def mouse_hover(self):
		"""Attribue quel bloc est survolé par la souris."""
		new_mouse_hovered = self.get_mouse_hover()
		if new_mouse_hovered == (0, [], (HoveredOn.SELF, None)):
			new_mouse_hovered = (0, [], (HoveredOn.SEQUENCE, 0))
		if new_mouse_hovered == self.mouse_hovered: return
		
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
		
		self.draw_info_box()
		
		if self.selected_bloc is not None:
			position, bloc = self.selected_bloc
			bloc.draw(self.window_surface, self.camera, position, selected=True)
		
		if self.text_box is not None and self.text_box_bloc is None:
			self.text_box.draw(self.window_surface)
		if self.rolling_list is not None:
			self.rolling_list.draw(self.window_surface)
		
		self.draw_clock()
	
	def draw_info_box(self):
		"""Affiche la boite d’information au-dessus d’un bloc quand on survole son bouton info."""
		if self.info_timer < INFO_TIME: return
		
		if self.mouse_hovered is None: return
		bloc_id, hierarchy, _ = self.mouse_hovered
		position, bloc = self.blocs[bloc_id]
		hovered_bloc = bloc.get_bloc(hierarchy)
		title = hovered_bloc.__class__.__name__.split("Bloc")[0].upper()
		text = f"{title}\n{hovered_bloc.__doc__}".replace("\t", "").split("\n")
		
		size = Vec2(max([FONT_20.size(line)[0] for line in text]), len(text) * FONT_20.get_height())
		info_position = self.camera.world2screen(
		  position + bloc.get_position(hierarchy) +
		  bloc.top_box_position + bloc.info_bt_position) - size / 2 - Vec2(0, 50)
		
		draw.rect(self.window_surface, "white", (info_position - MARGIN, size + 2 * MARGIN), 0, 5)
		draw.rect(self.window_surface, "black", (info_position - MARGIN, size + 2 * MARGIN), 1, 5)
		for i, line in enumerate(text):
			draw_text(self.window_surface, line,
			          info_position + (i + .5) * Vec2(0, FONT_20.get_height()),
			          20, align="left", bold=i == 0)
