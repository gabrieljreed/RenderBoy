"""Types that are used in the render pipeline."""


class Shot:
    """A shot object. A shot may have 0 or more layers and renders."""

    def __init__(self):
        """Initialize the shot object.

        Parameters:
            name (str): The name of the shot.
            notes (str): Any notes about the shot.
            layers (list): The layers for the shot.
            renders (list): The renders for the shot.
            frameStart (int): The start frame of the shot.
            frameEnd (int): The end frame of the shot.
        """
        self.notes = ""
        self.layers = []
        self.renders = []
        self.frameStart = 0
        self.frameEnd = 0


class Layer:
    """A layer object. A shot may have 0 or more layers."""

    def __init__(self):
        """Initialize the layer object.

        Parameters:
            name (str): The name of the layer.
            notes (str): Any notes about the layer.
            exclude (list): The exclude list for the layer.
            matte (list): The matte list for the layer.
            phantom (list): The phantom list for the layer.
        """
        self.name = ""
        self.notes = ""
        self.exclude = []
        self.matte = []
        self.phantom = []


class Render:
    """A render object. A shot may have 0 or more renders."""

    def __init__(self) -> None:
        """Initialize the render object.

        Parameters:
            name (str): The name of the render.
            author (str): The author of the render.
            notes (str): Any notes about the render.
            frameStart (int): The start frame of the render.
            frameEnd (int): The end frame of the render.
            resolution (str): The resolution of the render.
        """
        self.name = ""
        self.author = ""
        self.notes = ""
        self.frameStart = 0
        self.frameEnd = 0
        self.resolution = ""
