"""Types that are used in the render pipeline."""


import os
import json


class RenderBoyObject:
    """A base class for all renderboy objects. This class is used to identify the type of an object."""

    def __init__(self) -> None:
        """Initialize the object."""
        self.objectType = type(self).__name__


def loadRenderBoyObject(d: dict):
    """Return a RenderBoyObject from the given dict."""
    objectType = d.get("objectType")
    newObject = listAllRenderBoyObjects().get(objectType)
    newObject = newObject()

    if newObject is None:
        return d

    for var in d:
        if var in vars(newObject):
            setattr(newObject, var, d[var])

    return newObject


def loadProjectFromFile(filePath):
    """Load a project from the given file path."""
    with open(filePath, "r") as f:
        project = json.load(f, object_hook=loadRenderBoyObject)
    project.shots.sort(key=lambda x: x.name)
    return project


class Project(RenderBoyObject):
    """A project object. A project may have 0 or more shots."""

    def __init__(self, directory=None):
        """Initialize the project object.

        Arguments:
            directory (str): The directory of the project. If None, the project will be empty.

        Parameters:
            name (str): The name of the project.
            notes (str): Any notes about the project.
            shots (list): The shots for the project.
        """
        super().__init__()
        self.name = ""
        self.notes = ""
        self.shots = []

        if directory:
            self.generateFromDirectory(directory)

    def generateFromDirectory(self, directory):
        """Load the project from the given directory.

        Arguments:
            directory (str): The directory of the project.
        """
        shotFolders = os.listdir(directory)
        for shotFolder in shotFolders:
            shot = Shot()
            shot.name = shotFolder
            self.shots.append(shot)

    def writeToFile(self, filePath):
        """Write a json file to the given path."""
        # Lock the file so it can't be opened by another program while writing

        with open(filePath, "w") as f:
            json.dump(self, f, default=lambda o: o.__dict__, indent=4)

    def getShot(self, shotName):
        """Return the shot with the given name."""
        for shot in self.shots:
            if shot.name == shotName:
                return shot

        print(f"WARNING: Shot {shotName} not found.")
        return None


class Shot(RenderBoyObject):
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
        super().__init__()

        self.name = ""
        self.notes = ""
        self.layers = []
        self.renders = []
        self.frameStart = 0
        self.frameEnd = 0

    def addLayer(self):
        """Add a layer to the shot."""
        layer = Layer()
        layer.name = f"Layer {len(self.layers) + 1}"
        self.layers.append(layer)
        return layer

    def removeLayer(self, layerName):
        """Remove the given layer from the shot."""
        for layer in self.layers:
            if layer.name == layerName:
                del self.layers[self.layers.index(layer)]
                return True

        print(f"WARNING: Layer {layerName} not found.")
        return False

    def getLayer(self, layerName):
        """Return the layer with the given name."""
        for layer in self.layers:
            if layer.name == layerName:
                return layer

        print(f"WARNING: Layer {layerName} not found.")
        return None


class Layer(RenderBoyObject):
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
        super().__init__()

        self.name = ""
        self.notes = ""
        self.exclude = []
        self.matte = []
        self.phantom = []

    def rename(self, newName):
        """Rename the layer."""
        self.name = newName


class Render(RenderBoyObject):
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
            layers (list): The layers of the render.
        """
        super().__init__()

        self.name = ""
        self.author = ""
        self.notes = ""
        self.frameStart = 0
        self.frameEnd = 0
        self.resolution = ""
        self.layers = []


def listAllRenderBoyObjects():
    """Return a dict of the names of all renderboy objects and their classes."""
    classes = {}

    # Load the dictionary with all subclasses of RenderBoyObject
    for cls in RenderBoyObject.__subclasses__():
        classes[cls.__name__] = cls
        for subcls in cls.__subclasses__():
            classes[subcls.__name__] = subcls

    return classes


if __name__ == "__main__":
    print(listAllRenderBoyObjects())
    print(RenderBoyObject.__subclasses__())
