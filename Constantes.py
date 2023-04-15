from pygame import font, Vector2 as Vec2

# Text
font.init()
FONT_20: font.Font = font.SysFont("tw cen", 20)
# print(font.get_fonts())


# Global
MOTHER_SIZE: Vec2 = 100 * Vec2(4, 6)

TYPES: list[str] = ["Int", "Float", "Bool", "String"]


# Blocs
RADIUS: int = 7
SMALL_RADIUS: int = 2

SLOT_SIZE: Vec2 = Vec2(80, 25)
SLOT_TEXT_SIZE: int = 18

MARGIN: int = 12
INNER_MARGIN: int = 6

BT_SIZE: Vec2 = Vec2(16)
