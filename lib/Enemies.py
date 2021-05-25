from lib.helpers import BaseSprite


class TestEnemy(BaseSprite):
    def __init__(self, center=(0, 0)):
        super().__init__(image_path='assets/wall.png')
