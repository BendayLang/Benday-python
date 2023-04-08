"""Ce programme python contient une classe permettant de gérer plus facilement les entrées utilisateur."""
import pygame as pg
from pygame import Vector2 as Vec2
from dataclasses import dataclass, field
from enum import Enum, auto


class Key(Enum):
	UP = auto()
	CLICKED = auto()
	DOWN = auto()
	UNCLICKED = auto()


@dataclass
class Mouse:
	position: Vec2 = field(default=Vec2)
	delta: Vec2 = field(default=Vec2)
	scroll: int = 0  # (scroll < 0 vers le haut) et (scroll > 0 vers le bas)
	
	K_LEFT: Key = Key.UP  # 1
	K_WHEEL: Key = Key.UP  # 2
	K_RIGHT: Key = Key.UP  # 3


@dataclass
class Inputs:
	K_ESCAPE: Key = Key.UP
	K_RETURN: Key = Key.UP
	K_SPACE: Key = Key.UP
	K_BACKSPACE: Key = Key.UP
	K_DELETE: Key = Key.UP
	
	K_TAB: Key = Key.UP
	K_SHIFT: Key = Key.UP
	K_CONTROL: Key = Key.UP
	K_ALT: Key = Key.UP
	
	K_LEFT: Key = Key.UP
	K_RIGHT: Key = Key.UP
	K_UP: Key = Key.UP
	K_DOWN: Key = Key.UP
	
	K_0: Key = Key.UP
	K_1: Key = Key.UP
	K_2: Key = Key.UP
	K_3: Key = Key.UP
	K_4: Key = Key.UP
	K_5: Key = Key.UP
	K_6: Key = Key.UP
	K_7: Key = Key.UP
	K_8: Key = Key.UP
	K_9: Key = Key.UP
	
	TEXT_INPUT: str = ""
	
	mouse: Mouse = field(default=Mouse)
	WINDOW_RESIZED = False
	
	def get_events(self, events) -> bool:
		"""Met à jour les entrées utilisateur."""
		self.TEXT_INPUT = ""
		self.mouse.scroll = 0
		self.WINDOW_RESIZED = False
		
		if self.K_ESCAPE == Key.CLICKED: self.K_ESCAPE = Key.DOWN
		if self.K_ESCAPE == Key.UNCLICKED: self.K_ESCAPE = Key.UP
		if self.K_RETURN == Key.CLICKED: self.K_RETURN = Key.DOWN
		if self.K_RETURN == Key.UNCLICKED: self.K_RETURN = Key.UP
		if self.K_SPACE == Key.CLICKED: self.K_SPACE = Key.DOWN
		if self.K_SPACE == Key.UNCLICKED: self.K_SPACE = Key.UP
		if self.K_BACKSPACE == Key.CLICKED: self.K_BACKSPACE = Key.DOWN
		if self.K_BACKSPACE == Key.UNCLICKED: self.K_BACKSPACE = Key.UP
		if self.K_DELETE == Key.CLICKED: self.K_DELETE = Key.DOWN
		if self.K_DELETE == Key.UNCLICKED: self.K_DELETE = Key.UP
		
		if self.K_TAB == Key.CLICKED: self.K_TAB = Key.DOWN
		if self.K_TAB == Key.UNCLICKED: self.K_TAB = Key.UP
		if self.K_SHIFT == Key.CLICKED: self.K_SHIFT = Key.DOWN
		if self.K_SHIFT == Key.UNCLICKED: self.K_SHIFT = Key.UP
		if self.K_CONTROL == Key.CLICKED: self.K_CONTROL = Key.DOWN
		if self.K_CONTROL == Key.UNCLICKED: self.K_CONTROL = Key.UP
		if self.K_ALT == Key.CLICKED: self.K_ALT = Key.DOWN
		if self.K_ALT == Key.UNCLICKED: self.K_ALT = Key.UP
		
		if self.K_LEFT == Key.CLICKED: self.K_LEFT = Key.DOWN
		if self.K_LEFT == Key.UNCLICKED: self.K_LEFT = Key.UP
		if self.K_RIGHT == Key.CLICKED: self.K_RIGHT = Key.DOWN
		if self.K_RIGHT == Key.UNCLICKED: self.K_RIGHT = Key.UP
		if self.K_UP == Key.CLICKED: self.K_UP = Key.DOWN
		if self.K_UP == Key.UNCLICKED: self.K_UP = Key.UP
		if self.K_DOWN == Key.CLICKED: self.K_DOWN = Key.DOWN
		if self.K_DOWN == Key.UNCLICKED: self.K_DOWN = Key.UP
		
		if self.K_0 == Key.CLICKED: self.K_0 = Key.DOWN
		if self.K_0 == Key.UNCLICKED: self.K_0 = Key.UP
		if self.K_1 == Key.CLICKED: self.K_1 = Key.DOWN
		if self.K_1 == Key.UNCLICKED: self.K_1 = Key.UP
		if self.K_2 == Key.CLICKED: self.K_2 = Key.DOWN
		if self.K_2 == Key.UNCLICKED: self.K_2 = Key.UP
		if self.K_3 == Key.CLICKED: self.K_3 = Key.DOWN
		if self.K_3 == Key.UNCLICKED: self.K_3 = Key.UP
		if self.K_4 == Key.CLICKED: self.K_4 = Key.DOWN
		if self.K_4 == Key.UNCLICKED: self.K_4 = Key.UP
		if self.K_5 == Key.CLICKED: self.K_5 = Key.DOWN
		if self.K_5 == Key.UNCLICKED: self.K_5 = Key.UP
		if self.K_6 == Key.CLICKED: self.K_6 = Key.DOWN
		if self.K_6 == Key.UNCLICKED: self.K_6 = Key.UP
		if self.K_7 == Key.CLICKED: self.K_7 = Key.DOWN
		if self.K_7 == Key.UNCLICKED: self.K_7 = Key.UP
		if self.K_8 == Key.CLICKED: self.K_8 = Key.DOWN
		if self.K_8 == Key.UNCLICKED: self.K_8 = Key.UP
		if self.K_9 == Key.CLICKED: self.K_9 = Key.DOWN
		if self.K_9 == Key.UNCLICKED: self.K_9 = Key.UP
		
		if self.mouse.K_LEFT == Key.CLICKED: self.mouse.K_LEFT = Key.DOWN
		if self.mouse.K_LEFT == Key.UNCLICKED: self.mouse.K_LEFT = Key.UP
		if self.mouse.K_WHEEL == Key.CLICKED: self.mouse.K_WHEEL = Key.DOWN
		if self.mouse.K_WHEEL == Key.UNCLICKED: self.mouse.K_WHEEL = Key.UP
		if self.mouse.K_RIGHT == Key.CLICKED: self.mouse.K_RIGHT = Key.DOWN
		if self.mouse.K_RIGHT == Key.UNCLICKED: self.mouse.K_RIGHT = Key.UP
		
		for event in events:
			if event.type == pg.QUIT:
				return False
			elif event.type == pg.KEYDOWN:  # Appuie sur une touche du CLAVIER
				
				if event.key == pg.K_ESCAPE: self.K_ESCAPE = Key.CLICKED
				if event.key == pg.K_RETURN: self.K_RETURN = Key.CLICKED
				if event.key == pg.K_SPACE: self.K_SPACE = Key.CLICKED
				if event.key == pg.K_BACKSPACE: self.K_BACKSPACE = Key.CLICKED
				if event.key == pg.K_DELETE: self.K_DELETE = Key.CLICKED
				
				if event.key == pg.K_TAB: self.K_TAB = Key.CLICKED
				if event.key == pg.K_LSHIFT or event.key == pg.K_RSHIFT: self.K_SHIFT = Key.CLICKED
				if event.key == pg.K_LCTRL: self.K_CONTROL = Key.CLICKED
				if event.key == pg.KMOD_ALT: self.K_ALT = Key.CLICKED
				
				if event.key == pg.K_LEFT: self.K_LEFT = Key.CLICKED
				if event.key == pg.K_RIGHT: self.K_RIGHT = Key.CLICKED
				if event.key == pg.K_UP: self.K_UP = Key.CLICKED
				if event.key == pg.K_DOWN: self.K_DOWN = Key.CLICKED
				
				if event.key == pg.K_0: self.K_0 = Key.CLICKED
				if event.key == pg.K_1: self.K_1 = Key.CLICKED
				if event.key == pg.K_2: self.K_2 = Key.CLICKED
				if event.key == pg.K_3: self.K_3 = Key.CLICKED
				if event.key == pg.K_4: self.K_4 = Key.CLICKED
				if event.key == pg.K_5: self.K_5 = Key.CLICKED
				if event.key == pg.K_6: self.K_6 = Key.CLICKED
				if event.key == pg.K_7: self.K_7 = Key.CLICKED
				if event.key == pg.K_8: self.K_8 = Key.CLICKED
				if event.key == pg.K_9: self.K_9 = Key.CLICKED
			
			elif event.type == pg.KEYUP:  # Relâche une touche du CLAVIER
				if event.key == pg.K_ESCAPE: self.K_ESCAPE = Key.UNCLICKED
				if event.key == pg.K_RETURN: self.K_RETURN = Key.UNCLICKED
				if event.key == pg.K_SPACE: self.K_SPACE = Key.UNCLICKED
				if event.key == pg.K_BACKSPACE: self.K_BACKSPACE = Key.UNCLICKED
				if event.key == pg.K_DELETE: self.K_DELETE = Key.UNCLICKED
				
				if event.key == pg.K_TAB: self.K_TAB = Key.UNCLICKED
				if event.key == pg.K_LSHIFT or event.key == pg.K_RSHIFT: self.K_SHIFT = Key.UNCLICKED
				if event.key == pg.K_LCTRL: self.K_CONTROL = Key.UNCLICKED
				if event.key == pg.KMOD_ALT: self.K_SPACE = Key.UNCLICKED
				
				if event.key == pg.K_LEFT: self.K_LEFT = Key.UNCLICKED
				if event.key == pg.K_RIGHT: self.K_RIGHT = Key.UNCLICKED
				if event.key == pg.K_UP: self.K_UP = Key.UNCLICKED
				if event.key == pg.K_DOWN: self.K_DOWN = Key.UNCLICKED
				
				if event.key == pg.K_0: self.K_0 = Key.UNCLICKED
				if event.key == pg.K_1: self.K_1 = Key.UNCLICKED
				if event.key == pg.K_2: self.K_2 = Key.UNCLICKED
				if event.key == pg.K_3: self.K_3 = Key.UNCLICKED
				if event.key == pg.K_4: self.K_4 = Key.UNCLICKED
				if event.key == pg.K_5: self.K_5 = Key.UNCLICKED
				if event.key == pg.K_6: self.K_6 = Key.UNCLICKED
				if event.key == pg.K_7: self.K_7 = Key.UNCLICKED
				if event.key == pg.K_8: self.K_8 = Key.UNCLICKED
				if event.key == pg.K_9: self.K_9 = Key.UNCLICKED
			
			elif event.type == pg.MOUSEBUTTONDOWN:  # Clique sur la SOURIS
				if event.button == 1:
					self.mouse.K_LEFT = Key.CLICKED
				elif event.button == 2:
					self.mouse.K_WHEEL = Key.CLICKED
				elif event.button == 3:
					self.mouse.K_RIGHT = Key.CLICKED
			elif event.type == pg.MOUSEBUTTONUP:  # Dé-clique sur la SOURIS
				if event.button == 1:
					self.mouse.K_LEFT = Key.UNCLICKED
				elif event.button == 2:
					self.mouse.K_WHEEL = Key.UNCLICKED
				elif event.button == 3:
					self.mouse.K_RIGHT = Key.UNCLICKED
			elif event.type == pg.MOUSEWHEEL:  # Scroll
				self.mouse.scroll = event.y
			elif event.type == pg.WINDOWRESIZED:
				self.WINDOW_RESIZED = Vec2(event.x, event.y)
			
			if event.type == pg.TEXTINPUT:  # Appuie sur une touche du CLAVIER
				self.TEXT_INPUT += event.text
		
		self.mouse.position = Vec2(pg.mouse.get_pos())
		self.mouse.delta = Vec2(pg.mouse.get_rel())
		return True
