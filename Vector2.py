class Vector2:
    x = 0
    y = 0

    def __init__(self, x=0, y=0):
        self.setXY(x, y)

    def setXY(self, x=None, y=None):
        self.x = x or self.x
        self.y = y or self.y
