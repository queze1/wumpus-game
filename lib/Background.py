from lib.helpers import BaseSprite

from config import WINDOW_HEIGHT, WINDOW_WIDTH


class Background(BaseSprite):
    def __init__(self):
        super().__init__(image_assets='assets/wallpaper.png', center=(WINDOW_WIDTH/2, WINDOW_HEIGHT/2))

class MenuBackground(BaseSprite):
    def __init__(self):
        super().__init__(image_assets='assets/wallpaper.png', center=(WINDOW_WIDTH/2, WINDOW_HEIGHT/2))
