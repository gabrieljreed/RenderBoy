"""RenderBoy Window."""


from PySide2 import QtWidgets, QtCore, QtGui

from functools import partial
import os
import sys

renderboyPath = os.path.normpath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))
sys.path.append(renderboyPath)

import renderboy.data.renderTypes as rbTypes


iconBasePath = os.path.join(os.path.dirname(__file__), "icons")


class RenderBoyWindow(QtWidgets.QMainWindow):
    """RenderBoy Window."""

    def __init__(self) -> None:
        """Initialize the RenderBoy window."""
        super().__init__()

        self.isSidebarCollapsed = False
        self.sidebarMode = "shots"

        self.userFolderPath = os.path.abspath(os.path.join(__file__, os.pardir, "_user"))
        if not os.path.exists(self.userFolderPath):
            os.makedirs(self.userFolderPath)

        self.projectDataPath = os.path.join(self.userFolderPath, "projectData.json")
        if os.path.isfile(self.projectDataPath):
            self.project = rbTypes.loadProjectFromFile(self.projectDataPath)
        else:
            self.project = rbTypes.Project()

        self.setupUI()

    def setupUI(self) -> None:
        """Set up the UI."""
        self.setWindowTitle("RenderBoy")
        self.resize(800, 600)

        self.centralWidget = QtWidgets.QWidget(self)
        self.setCentralWidget(self.centralWidget)

        self.layout = QtWidgets.QHBoxLayout()
        self.centralWidget.setLayout(self.layout)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        self.setupMenuBar()
        self.setupGutter()
        self.setupSidebar()
        self.setupShotWidget()

    def setupMenuBar(self):
        """Set up the menu bar."""
        # Add a menu bar
        self.menuBar = QtWidgets.QMenuBar(self)
        self.setMenuBar(self.menuBar)

        # Layers submenu
        self.layersMenu = QtWidgets.QMenu("Layers", self)
        self.layersMenu.addAction("Add Layer")
        self.layersMenu.addAction("Remove Layer")

        self.menuBar.addMenu(self.layersMenu)

        # Renders submenu
        self.rendersMenu = QtWidgets.QMenu("Renders", self)
        self.rendersMenu.addAction("Add Render")
        self.rendersMenu.addAction("Remove Render")

        self.menuBar.addMenu(self.rendersMenu)

    def setupGutter(self):
        """Set up the gutter."""
        self.gutter = QtWidgets.QFrame(self)
        self.gutter.setMinimumWidth(50)
        self.gutter.setMaximumWidth(50)
        self.gutter.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Expanding)
        self.gutter.setLineWidth(1)
        # Only draw the frame on the right side
        self.gutter.setStyleSheet("QFrame { border-right: 1px solid #FFFFFF; }")

        self.gutterLayout = QtWidgets.QVBoxLayout(self.gutter)
        self.gutterLayout.setContentsMargins(0, 0, 0, 0)
        self.gutterLayout.setSpacing(0)
        self.gutterLayout.setAlignment(QtCore.Qt.AlignTop)

        self.gutter.setLayout(self.gutterLayout)

        self.layout.addWidget(self.gutter)

        # Add a vertical line to the layout after the gutter
        self.line = QtWidgets.QFrame(self)
        self.line.setFrameShape(QtWidgets.QFrame.VLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.layout.addWidget(self.line)

        self.sidebarButton = QtWidgets.QPushButton()
        self.sidebarButton.setIcon(QtGui.QIcon(os.path.join(iconBasePath, "sidebar.svg")))
        self.sidebarButton.setIconSize(QtCore.QSize(24, 24))
        self.sidebarButton.setFlat(True)
        self.sidebarButton.setFixedWidth(48)
        self.sidebarButton.setFixedHeight(48)
        self.sidebarButton.clicked.connect(partial(self.updateSidebar, "shots"))
        self.gutterLayout.addWidget(self.sidebarButton)

        self.settingsButton = QtWidgets.QPushButton()
        self.settingsButton.setIcon(QtGui.QIcon(os.path.join(iconBasePath, "settings.svg")))
        self.settingsButton.setIconSize(QtCore.QSize(24, 24))
        self.settingsButton.setFlat(True)
        self.settingsButton.setFixedWidth(48)
        self.settingsButton.setFixedHeight(48)
        self.settingsButton.clicked.connect(partial(self.updateSidebar, "settings"))
        self.gutterLayout.addWidget(self.settingsButton)

    def setupSidebar(self):
        """Set up the sidebar."""
        self.sidebar = QtWidgets.QFrame(self)
        self.sidebar.setMinimumWidth(200)
        self.sidebar.setMaximumWidth(200)
        self.sidebar.setFixedWidth(200)

        self.sidebarLayout = QtWidgets.QVBoxLayout(self.sidebar)
        self.sidebarLayout.setContentsMargins(0, 0, 0, 0)
        self.sidebarLayout.setSpacing(4)
        self.sidebarLayout.setAlignment(QtCore.Qt.AlignTop)

        self.sidebar.setLayout(self.sidebarLayout)

        self.layout.addWidget(self.sidebar)

        if self.sidebarMode == "shots":
            self.setupShotsSidebar()
        elif self.sidebarMode == "settings":
            self.setupSettingsSidebar()

    def clearSidebar(self):
        """Clear the sidebar."""
        # Remove all children from self.sidebarLayout
        for i in reversed(range(self.sidebarLayout.count())):
            self.sidebarLayout.itemAt(i).widget().setParent(None)

    def setupShotsSidebar(self):
        """Set up the shots sidebar."""
        self.clearSidebar()

        self.sidebarLayout.addWidget(QtWidgets.QLabel("Shots"))

        self.sidebarSearchBar = QtWidgets.QLineEdit(self)
        self.sidebarSearchBar.setPlaceholderText("Search")
        self.sidebarSearchBar.setFixedWidth(198)
        self.sidebarSearchBar.textEdited.connect(self.searchShots)
        self.sidebarLayout.addWidget(self.sidebarSearchBar)

        self.shotListWidget = QtWidgets.QListWidget(self)
        self.shotListWidget.setAlternatingRowColors(True)
        self.shotListWidget.setFixedWidth(198)
        shotsToAdd = [shot.name for shot in self.project.shots]
        self.shotListWidget.itemClicked.connect(self.updateShotWidget)
        self.shotListWidget.addItems(shotsToAdd)
        self.sidebarLayout.addWidget(self.shotListWidget)

        self.bottomSpacer = QtWidgets.QWidget()
        self.bottomSpacer.setMaximumHeight(2)
        self.bottomSpacer.setMinimumHeight(2)
        self.sidebarLayout.addWidget(self.bottomSpacer)

    def setupSettingsSidebar(self):
        """Set up the settings sidebar."""
        self.clearSidebar()

        self.sidebarLayout.addWidget(QtWidgets.QLabel("Settings"))

        self.createShotsFromDirectoryButton = QtWidgets.QPushButton("Create Shots From Directory")
        self.createShotsFromDirectoryButton.clicked.connect(self.createShotsFromDirectory)
        self.sidebarLayout.addWidget(self.createShotsFromDirectoryButton)

        self.loadProjectFromFileButton = QtWidgets.QPushButton("Load Project From File")
        self.loadProjectFromFileButton.clicked.connect(self.loadProjectFromFile)
        self.sidebarLayout.addWidget(self.loadProjectFromFileButton)

    def createShotsFromDirectory(self):
        """Create shots from a directory."""
        directory = QtWidgets.QFileDialog.getExistingDirectory(self, "Select Project Directory")
        if not directory:
            return

        self.project = rbTypes.Project(directory)
        self.shotListWidget.clear()
        shotNames = [shot.name for shot in self.project.shots]
        self.shotListWidget.addItems(shotNames)
        self.writeProjectToFile()

    def searchShots(self):
        """Search for shots."""
        if self.sidebarSearchBar.text():
            self.sidebarSearchBar.setClearButtonEnabled(True)
            self.shotListWidget.clear()
            shotsToSearch = [shot.name for shot in self.project.shots]
            self.shotListWidget.addItems([shot for shot in shotsToSearch if self.sidebarSearchBar.text() in shot])
        else:
            self.shotListWidget.clear()
            self.shotListWidget.addItems([shot.name for shot in self.project.shots])

    def updateSidebar(self, mode):
        """Update the sidebar collapsed state and mode."""
        if self.isSidebarCollapsed:
            self.sidebarMode = mode
            if self.sidebarMode == "shots":
                self.setupShotsSidebar()
            elif self.sidebarMode == "settings":
                self.setupSettingsSidebar()

            self.sidebar.setFixedWidth(200)
            self.isSidebarCollapsed = False

        elif mode == self.sidebarMode:
            # Update the sidebar collapsed state
            if self.isSidebarCollapsed:
                self.sidebar.setFixedWidth(200)
            else:
                self.sidebar.setFixedWidth(0)

            self.isSidebarCollapsed = not self.isSidebarCollapsed

        else:
            # Update the sidebar mode
            self.sidebarMode = mode

            if self.sidebarMode == "shots":
                self.setupShotsSidebar()
            elif self.sidebarMode == "settings":
                self.setupSettingsSidebar()

    def setupShotWidget(self):
        """Set up the shot widget."""
        self.shotWidget = QtWidgets.QTabWidget(self)
        self.layout.addWidget(self.shotWidget)

        self.layerTab = QtWidgets.QWidget()
        self.renderTab = QtWidgets.QWidget()

        self.shotWidget.addTab(self.layerTab, "Layers")
        self.shotWidget.addTab(self.renderTab, "Renders")

        self.setupLayerTab()
        self.setupRenderTab()

    def updateShotWidget(self):
        """Update the shot widget."""
        self.updateLayerTab()

    def setupLayerTab(self):
        """Set up the layer tab."""
        self.layerLayout = QtWidgets.QHBoxLayout(self.layerTab)
        self.layerTab.setLayout(self.layerLayout)
        self.layerTab.setDisabled(True)

        layerListWidgetHolder = QtWidgets.QWidget()
        layerListWidgetHolder.setFixedWidth(250)
        layerListWidgetHolderLayout = QtWidgets.QVBoxLayout(layerListWidgetHolder)
        layerListWidgetHolderLayout.setAlignment(QtCore.Qt.AlignTop)
        layerListWidgetHolder.setLayout(layerListWidgetHolderLayout)
        self.layerLayout.addWidget(layerListWidgetHolder)

        # ADD/REMOVE BUTTONS
        buttonFrame = QtWidgets.QWidget()
        buttonFrameLayout = QtWidgets.QHBoxLayout(buttonFrame)
        buttonFrameLayout.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignLeft)
        buttonFrameLayout.setSpacing(0)
        buttonFrameLayout.setContentsMargins(0, 0, 0, 0)
        buttonFrame.setLayout(buttonFrameLayout)
        layerListWidgetHolderLayout.addWidget(buttonFrame)

        self.addLayerButton = QtWidgets.QPushButton("+")
        self.addLayerButton.setToolTip("Add Layer")
        self.addLayerButton.setFixedWidth(20)
        self.addLayerButton.setFixedHeight(20)
        self.addLayerButton.clicked.connect(self.addLayer)
        buttonFrameLayout.addWidget(self.addLayerButton)

        self.removeLayerButton = QtWidgets.QPushButton("-")
        self.removeLayerButton.setToolTip("Remove Layer")
        self.removeLayerButton.setFixedWidth(20)
        self.removeLayerButton.setFixedHeight(20)
        self.removeLayerButton.clicked.connect(self.removeLayer)
        buttonFrameLayout.addWidget(self.removeLayerButton)

        # LIST WIDGET
        self.layerListWidget = QtWidgets.QListWidget(self)
        self.layerListWidget.setAlternatingRowColors(True)
        self.layerListWidget.setFixedWidth(198)
        self.layerListWidget.itemClicked.connect(self.updateLayerSettingsWidget)
        layerListWidgetHolderLayout.addWidget(self.layerListWidget)

        # SETTINGS WIDGET
        self.setupLayerSettingsWidget()

    def setupLayerSettingsWidget(self):
        """Set up the layer settings widget."""
        self.layerSettingsWidget = QtWidgets.QWidget()
        # self.layerLayout.addWidget(self.layerSettingsWidget)

        self.layerSettingsLayout = QtWidgets.QVBoxLayout(self.layerSettingsWidget)
        self.layerSettingsLayout.setAlignment(QtCore.Qt.AlignTop)
        self.layerSettingsLayout.setSpacing(0)

        self.layerSettingsWidget.setLayout(self.layerSettingsLayout)

        self.layerSettingsLayout.addWidget(QtWidgets.QLabel("Layer Name"))

        self.layerNameLineEdit = QtWidgets.QLineEdit()
        self.layerNameLineEdit.setPlaceholderText("Layer Name")
        self.layerNameLineEdit.textEdited.connect(self.renameLayer)
        self.layerSettingsLayout.addWidget(self.layerNameLineEdit)

        self.layerSettingsLayout.addWidget(QtWidgets.QLabel("Notes"))

        self.layerNotesTextEdit = QtWidgets.QTextEdit()
        self.layerNotesTextEdit.setFixedHeight(100)
        self.layerNotesTextEdit.setPlaceholderText("Notes")
        self.layerNotesTextEdit.textChanged.connect(self.updateLayerNotes)
        self.layerSettingsLayout.addWidget(self.layerNotesTextEdit)

        self.layerSettingsLayout.addWidget(QtWidgets.QLabel("Exclude"))

        excludeButtonFrame, addExcludeButton, removeExcludeButton, copyExcludeButton = self.createAddRemoveCopyButtons()
        self.layerSettingsLayout.addWidget(excludeButtonFrame)

        addExcludeButton.clicked.connect(partial(self.addToLayerList, "exclude"))
        removeExcludeButton.clicked.connect(partial(self.removeFromLayerList, "exclude"))
        copyExcludeButton.clicked.connect(partial(self.copyToClipboardFromList, "exclude"))

        self.excludeListWidget = QtWidgets.QListWidget()
        self.excludeListWidget.setAlternatingRowColors(True)
        self.excludeListWidget.setFixedHeight(98)
        self.layerSettingsLayout.addWidget(self.excludeListWidget)

        self.layerSettingsLayout.addWidget(QtWidgets.QLabel("Matte"))

        matteButtonFrame, addMatteButton, removeMatteButton, copyMatteButton = self.createAddRemoveCopyButtons()
        self.layerSettingsLayout.addWidget(matteButtonFrame)

        addMatteButton.clicked.connect(partial(self.addToLayerList, "matte"))
        removeMatteButton.clicked.connect(partial(self.removeFromLayerList, "matte"))
        copyMatteButton.clicked.connect(partial(self.copyToClipboardFromList, "matte"))

        self.matteListWidget = QtWidgets.QListWidget()
        self.matteListWidget.setAlternatingRowColors(True)
        self.matteListWidget.setFixedHeight(98)
        self.layerSettingsLayout.addWidget(self.matteListWidget)

        self.layerSettingsLayout.addWidget(QtWidgets.QLabel("Phantom"))

        phantomButtonFrame, addPhantomButton, removePhantomButton, copyPhantomButton = self.createAddRemoveCopyButtons()
        self.layerSettingsLayout.addWidget(phantomButtonFrame)

        addPhantomButton.clicked.connect(partial(self.addToLayerList, "phantom"))
        removePhantomButton.clicked.connect(partial(self.removeFromLayerList, "phantom"))
        copyPhantomButton.clicked.connect(partial(self.copyToClipboardFromList, "phantom"))

        self.phantomListWidget = QtWidgets.QListWidget()
        self.phantomListWidget.setAlternatingRowColors(True)
        self.phantomListWidget.setFixedHeight(98)
        self.layerSettingsLayout.addWidget(self.phantomListWidget)

        scrollArea = QtWidgets.QScrollArea()
        scrollArea.setWidget(self.layerSettingsWidget)
        scrollArea.setWidgetResizable(True)
        self.layerLayout.addWidget(scrollArea)

    def createAddRemoveCopyButtons(self):
        """Create the add, remove and copy buttons for the layer settings widget."""
        arcButtonFrame = QtWidgets.QWidget()
        arcButtonFrame.setFixedHeight(20)
        arcFrameLayout = QtWidgets.QHBoxLayout(arcButtonFrame)
        arcFrameLayout.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignLeft)
        arcFrameLayout.setSpacing(0)
        arcFrameLayout.setContentsMargins(0, 0, 0, 0)
        arcButtonFrame.setLayout(arcFrameLayout)

        addExcludebutton = QtWidgets.QPushButton("+")
        addExcludebutton.setFixedWidth(20)
        addExcludebutton.setFixedHeight(20)
        arcFrameLayout.addWidget(addExcludebutton)

        removeExcludeButton = QtWidgets.QPushButton("-")
        removeExcludeButton.setFixedWidth(20)
        removeExcludeButton.setFixedHeight(20)
        arcFrameLayout.addWidget(removeExcludeButton)

        spacerWidget = QtWidgets.QWidget()
        spacerWidget.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        arcFrameLayout.addWidget(spacerWidget)

        copyExcludeToClipboardButton = QtWidgets.QPushButton("Copy to clipboard")
        copyExcludeToClipboardButton.setFixedWidth(100)
        copyExcludeToClipboardButton.setFixedHeight(20)
        arcFrameLayout.addWidget(copyExcludeToClipboardButton)

        return arcButtonFrame, addExcludebutton, removeExcludeButton, copyExcludeToClipboardButton

    def updateLayerTab(self):
        """Update the layer tab."""
        # Get the currently selected shot
        if not self.shotListWidget.currentItem():
            self.layerListWidget.clear()
            self.layerTab.setDisabled(True)
            return

        self.layerTab.setDisabled(False)
        shotName = self.shotListWidget.currentItem().text()
        shot = self.project.getShot(shotName)

        # Update the layer list widget
        self.layerListWidget.clear()
        layerNames = [layer.name for layer in shot.layers]
        self.layerListWidget.addItems(layerNames)

        self.updateLayerSettingsWidget()

    def updateLayerSettingsWidget(self):
        """Update the layer settings widget."""
        if not self.shotListWidget.currentItem():
            self.layerListWidget.clear()
            self.layerTab.setDisabled(True)
            self.layerNameLineEdit.setText("")
            self.layerNotesTextEdit.setPlainText("")
            return

        if not self.layerListWidget.currentItem():
            self.layerSettingsWidget.setDisabled(True)
            self.layerNameLineEdit.setText("")
            self.layerNotesTextEdit.setPlainText("")
            return

        self.layerSettingsWidget.setDisabled(False)

        shotName = self.shotListWidget.currentItem().text()
        shot = self.project.getShot(shotName)

        layerName = self.layerListWidget.currentItem().text()
        layer = shot.getLayer(layerName)

        self.layerNameLineEdit.setText(layer.name)

        self.layerNotesTextEdit.setPlainText(layer.notes)

    def setupRenderTab(self):
        """Set up the render tab."""
        self.renderTabLayout = QtWidgets.QVBoxLayout(self.renderTab)
        self.renderTab.setLayout(self.renderTabLayout)
        self.renderTabLayout.setAlignment(QtCore.Qt.AlignTop)
        self.renderTab.setDisabled(True)

        self.renderTabLayout.addWidget(QtWidgets.QLabel("Renders"))

        self.renderHWidget = QtWidgets.QWidget()
        self.renderHLayout = QtWidgets.QHBoxLayout(self.renderHWidget)
        self.renderHLayout.setAlignment(QtCore.Qt.AlignTop)
        self.renderHWidget.setLayout(self.renderHLayout)
        self.renderTabLayout.addWidget(self.renderHWidget)

        self.renderListWidget = QtWidgets.QListWidget(self)
        self.renderListWidget.setAlternatingRowColors(True)
        self.renderListWidget.setFixedWidth(198)
        self.renderHLayout.addWidget(self.renderListWidget)

        self.renderSettingsWidget = QtWidgets.QWidget()
        self.renderSettingsLayout = QtWidgets.QVBoxLayout(self.renderSettingsWidget)
        self.renderSettingsLayout.setAlignment(QtCore.Qt.AlignTop)
        self.renderSettingsWidget.setLayout(self.renderSettingsLayout)
        self.renderHLayout.addWidget(self.renderSettingsWidget)

        self.renderSettingsLayout.addWidget(QtWidgets.QLabel("Render Details"))

    def updateRenderTab(self, shot=None):
        """Update the render tab.

        Arguments:
            shot {str} -- The shot to update the render tab for. Defaults to None, which will clear the render tab.
        """
        pass

    def addLayer(self):
        """Add a layer to the current shot."""
        if not self.shotListWidget.currentItem():
            return

        shotName = self.shotListWidget.currentItem().text()
        shot = self.project.getShot(shotName)
        shot.addLayer()
        self.updateLayerTab()

    def removeLayer(self):
        """Remove a layer from the current shot."""
        if not self.shotListWidget.currentItem():
            return
        if not self.layerListWidget.currentItem():
            return

        shotName = self.shotListWidget.currentItem().text()
        shot = self.project.getShot(shotName)
        currentLayer = self.layerListWidget.currentItem().text()
        shot.removeLayer(currentLayer)
        self.updateLayerTab()

    def renameLayer(self):
        """Rename the currently selected layer in the current shot."""
        if not self.shotListWidget.currentItem():
            return
        if not self.layerListWidget.currentItem():
            return

        shotName = self.shotListWidget.currentItem().text()
        shot = self.project.getShot(shotName)
        layerName = self.layerListWidget.currentItem().text()
        layer = shot.getLayer(layerName)
        layer.rename(self.layerNameLineEdit.text())

        # Change the name in the layer list widget
        self.layerListWidget.currentItem().setText(self.layerNameLineEdit.text())

    def updateLayerNotes(self):
        """Update the notes for the currently selected layer in the current shot."""
        if not self.shotListWidget.currentItem():
            return
        if not self.layerListWidget.currentItem():
            return

        shotName = self.shotListWidget.currentItem().text()
        shot = self.project.getShot(shotName)
        layerName = self.layerListWidget.currentItem().text()
        layer = shot.getLayer(layerName)
        layer.notes = self.layerNotesTextEdit.toPlainText()

    def addToLayerList(self, listType):
        """Add to layer exclude, matte, or phantom list.

        Arguments:
            listType {str} -- The type of list to add to. Can be "exclude", "matte", or "phantom".
        """
        if listType == "exclude":
            listWidget = self.layerExcludeListWidget
            listToAddTo = self.layer.exclude
        elif listType == "matte":
            listWidget = self.layerMatteListWidget
            listToAddTo = self.layer.matte
        elif listType == "phantom":
            listWidget = self.layerPhantomListWidget
            listToAddTo = self.layer.phantom
        else:
            return

        listToAddTo.append(f"New {listType.title()} Item")
        listWidget.addItem(f"New {listType.title()} Item")

    def removeFromLayerList(self, listType):
        """Remove from layer exclude, matte, or phantom list.

        Arguments:
            listType {str} -- The type of list to remove from. Can be "exclude", "matte", or "phantom".
        """
        if listType == "exclude":
            listWidget = self.layerExcludeListWidget
            listToRemoveFrom = self.layer.exclude
        elif listType == "matte":
            listWidget = self.layerMatteListWidget
            listToRemoveFrom = self.layer.matte
        elif listType == "phantom":
            listWidget = self.layerPhantomListWidget
            listToRemoveFrom = self.layer.phantom
        else:
            return

        for item in listWidget.selectedItems():
            listToRemoveFrom.remove(item.text())
            listWidget.takeItem(listWidget.row(item))

    def copyToClipboardFromList(self, listType):
        """Copy to clipboard from layer exclude, matte, or phantom list."""
        if listType == "exclude":
            listToCopyFrom = self.layerExcludeListWidget
        elif listType == "matte":
            listToCopyFrom = self.layerMatteListWidget
        elif listType == "phantom":
            listToCopyFrom = self.layerPhantomListWidget
        else:
            return

        textToCopy = ""
        for item in listToCopyFrom.selectedItems():
            textToCopy += item.text() + " "

        # TODO: Do the copy

    def writeProjectToFile(self):
        """Write the project to a file."""
        if self.project:
            self.project.writeToFile(self.projectDataPath)

    def loadProjectFromFile(self, filePath):
        """Load the project from a file."""
        self.project = rbTypes.loadProjectFromFile(filePath)
        if self.project:
            self.shotListWidget.clear()
            shotNames = [shot.name for shot in self.project.shots]
            self.shotListWidget.addItems(shotNames)

    def closeEvent(self, event):
        """Close the window and save project details."""
        self.writeProjectToFile()
        event.accept()
