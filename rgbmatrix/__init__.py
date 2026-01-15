# Mock rgbmatrix package (Mac-Entwicklung)

from .core import FrameCanvas

class RGBMatrixOptions:
    def __init__(self):
        self.rows = None
        self.cols = None
        self.chain_length = None
        self.parallel = None
        self.hardware_mapping = None

class RGBMatrix:
    def __init__(self, options=None):
        self.options = options or RGBMatrixOptions()
        # sinnvolle Defaults für Mac-Mock
        self.options.cols = self.options.cols or 64
        self.options.rows = self.options.rows or 32

    def CreateFrameCanvas(self, *args, **kwargs):
        return FrameCanvas(self.options.cols, self.options.rows)

class graphics:
    class Color:
        def __init__(self, r=0, g=0, b=0):
            self.r = r
            self.g = g
            self.b = b

        # Kompatibilität mit echtem rgbmatrix.Color
        @property
        def red(self):
            return self.r

        @property
        def green(self):
            return self.g

        @property
        def blue(self):
            return self.b

        def __repr__(self):
            return f"Color({self.r},{self.g},{self.b})"

    class Font:
        def __init__(self):
            self.loaded = False
            self.height = 8
            self.baseline = 7

        def LoadFont(self, path):
            print(f"[MOCK] Font geladen: {path}")
            self.loaded = True
            if "4x6" in path:
                self.height = 6
                self.baseline = 5
            elif "5x7" in path:
                self.height = 7
                self.baseline = 6
            elif "tom-thumb" in path:
                self.height = 5
                self.baseline = 4

        def CharacterWidth(self, cp):
            # Dummywert für Mac-Testing
            # Für kleine Monospace-Fonts: width ~ height // 2
            return max(1, self.height // 2)

        def __repr__(self):
            return f"<Font h={self.height} bl={self.baseline}>"