# Mock rgbmatrix.core

class FrameCanvas:
    def __init__(self, width=64, height=32):
        self.width = width
        self.height = height

    def Clear(self):
        pass

    def SwapOnVSync(self, canvas):
        return self

    def SetPixel(self, x, y, color):
        # optional: für Logging / Debugging
        # print(f"[MOCK] SetPixel({x},{y}, {color})")
        pass