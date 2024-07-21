# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""Sample PyQt application."""

import sys
from functools import partial
import numpy as np
import pickle

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon, QKeySequence, QAction
from PyQt6.QtWidgets import (
    QApplication,
    QLabel,
    QMainWindow,
    QMenu,
    QSpinBox,
    QToolBar,
)

from vispy.app import use_app
from vispy.scene import SceneCanvas, AxisWidget, visuals

from .camera import ScaZoomCamera
from .fileadapter import PickleFileAdapter

# NOTE: Uncomment this import to enable icons
# import qrc_resources

FNAME = 'numpy-samples'

class Window(QMainWindow):
    """Main Window."""

    def __init__(self, parent=None):
        """Initializer."""
        super().__init__(parent)
        self.setWindowTitle(f"sidevis - {FNAME}")
        self.resize(1200, 600)

        self.fileAdapter = PickleFileAdapter(FNAME)

        self.traceCanvas = TraceCanvas(self.fileAdapter)
        self.centralWidget = self.traceCanvas.canvas.native # QLabel("Hello, World")


        # self.centralWidget.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter)
        self.setCentralWidget(self.centralWidget)
        self._createActions()
        self._createMenuBar()
        self._createToolBars()

        # Uncomment the call to ._createContextMenu() below to create a context
        # menu using menu policies. To test this out, you also need to
        # comment .contextMenuEvent() and uncomment ._createContextMenu()

        # self._createContextMenu()

        self._connectActions()
        self._createStatusBar()

    def _createMenuBar(self):
        menuBar = self.menuBar()
        # File menu
        fileMenu = QMenu("&File", self)
        menuBar.addMenu(fileMenu)
        fileMenu.addAction(self.newAction)
        fileMenu.addAction(self.openAction)
        # Open Recent submenu
        self.openRecentMenu = fileMenu.addMenu("Open Recent")
        fileMenu.addAction(self.saveAction)
        # Separator
        fileMenu.addSeparator()
        fileMenu.addAction(self.exitAction)
        # Edit menu
        editMenu = menuBar.addMenu("&Edit")
        editMenu.addAction(self.copyAction)
        editMenu.addAction(self.pasteAction)
        editMenu.addAction(self.cutAction)
        # Separator
        editMenu.addSeparator()
        # Find and Replace submenu
        findMenu = editMenu.addMenu("Find and Replace")
        findMenu.addAction("Find...")
        findMenu.addAction("Replace...")
        # Help menu
        helpMenu = menuBar.addMenu("&Help")
        helpMenu.addAction(self.helpContentAction)
        helpMenu.addAction(self.aboutAction)

    def _createToolBars(self):
        # File toolbar
        fileToolBar = self.addToolBar("File")
        fileToolBar.setMovable(False)
        fileToolBar.addAction(self.newAction)
        fileToolBar.addAction(self.openAction)
        fileToolBar.addAction(self.saveAction)
        # Edit toolbar
        editToolBar = QToolBar("Edit", self)
        self.addToolBar(editToolBar)
        editToolBar.addAction(self.copyAction)
        editToolBar.addAction(self.pasteAction)
        editToolBar.addAction(self.cutAction)
        # Widgets
        editToolBar.addAction(self.resetCameraAction)

        self.rootTraceSpinBox = QSpinBox()
        self.rootTraceSpinBox.setValue(self.traceCanvas.root_trace)
        self.rootTraceSpinBox.setFocusPolicy(Qt.FocusPolicy.WheelFocus)
        editToolBar.addWidget(self.rootTraceSpinBox)

        self.traceViewCountSpinBox = QSpinBox()
        self.traceViewCountSpinBox.setValue(self.traceCanvas.view_count)
        self.traceViewCountSpinBox.setMinimum(1)
        self.traceViewCountSpinBox.setMaximum(5)
        self.traceViewCountSpinBox.setFocusPolicy(Qt.FocusPolicy.WheelFocus)
        editToolBar.addWidget(self.traceViewCountSpinBox)

    def _createStatusBar(self):
        self.statusbar = self.statusBar()
        # Temporary message
        self.statusbar.showMessage("Ready", 3000)
        # Permanent widget
        self.wcLabel = QLabel(f"{self.getWordCount()} Words")
        self.statusbar.addPermanentWidget(self.wcLabel)

    def _createActions(self):
        # File actions
        self.newAction = QAction(self)
        self.newAction.setText("&New")
        self.openAction = QAction("&Open...", self)
        self.saveAction = QAction("&Save", self)
        self.exitAction = QAction("&Exit", self)
        # String-based key sequences
        self.newAction.setShortcut("Ctrl+N")
        self.openAction.setShortcut("Ctrl+O")
        self.saveAction.setShortcut("Ctrl+S")
        # Help tips
        newTip = "Create a new file"
        self.newAction.setStatusTip(newTip)
        self.newAction.setToolTip(newTip)
        self.newAction.setWhatsThis("Create a new and empty text file")
        # Edit actions
        self.copyAction = QAction("&Copy", self)
        self.pasteAction = QAction("&Paste", self)
        self.cutAction = QAction("C&ut", self)
        # Standard key sequence
        self.copyAction.setShortcut(QKeySequence.StandardKey.Copy)
        self.pasteAction.setShortcut(QKeySequence.StandardKey.Paste)
        self.cutAction.setShortcut(QKeySequence.StandardKey.Cut)
        # Help actions
        self.helpContentAction = QAction("&Help Content...", self)
        self.aboutAction = QAction("&About...", self)

        self.resetCameraAction = QAction("&RESET", self)

    # Uncomment this method to create a context menu using menu policies
    # def _createContextMenu(self):
    #     # Setting contextMenuPolicy
    #     self.centralWidget.setContextMenuPolicy(Qt.ActionsContextMenu)
    #     # Populating the widget with actions
    #     self.centralWidget.addAction(self.newAction)
    #     self.centralWidget.addAction(self.openAction)
    #     self.centralWidget.addAction(self.saveAction)
    #     self.centralWidget.addAction(self.copyAction)
    #     self.centralWidget.addAction(self.pasteAction)
    #     self.centralWidget.addAction(self.cutAction)

    # def contextMenuEvent(self, event):
    #     # Context menu
    #     menu = QMenu(self.centralWidget)
    #     # Populating the menu with actions
    #     menu.addAction(self.newAction)
    #     menu.addAction(self.openAction)
    #     menu.addAction(self.saveAction)
    #     # Separator
    #     separator = QAction(self)
    #     separator.setSeparator(True)
    #     menu.addAction(separator)
    #     menu.addAction(self.copyAction)
    #     menu.addAction(self.pasteAction)
    #     menu.addAction(self.cutAction)
    #     # Launching the menu
    #     menu.exec(event.globalPos())

    def _connectActions(self):
        # Connect File actions
        self.newAction.triggered.connect(self.newFile)
        self.openAction.triggered.connect(self.openFile)
        self.saveAction.triggered.connect(self.saveFile)
        self.exitAction.triggered.connect(self.close)
        # Connect Edit actions
        self.copyAction.triggered.connect(self.copyContent)
        self.pasteAction.triggered.connect(self.pasteContent)
        self.cutAction.triggered.connect(self.cutContent)
        # Connect Help actions
        self.helpContentAction.triggered.connect(self.helpContent)
        self.aboutAction.triggered.connect(self.about)
        # Connect Open Recent to dynamically populate it
        self.openRecentMenu.aboutToShow.connect(self.populateOpenRecent)
        
        self.resetCameraAction.triggered.connect(self.resetCamera)

        self.rootTraceSpinBox.valueChanged.connect(self.setRootTrace)
    # self.traceViewCountSpinBox.valueChanged.connect(self.setViewCount)

    # Slots
    def newFile(self):
        # Logic for creating a new file goes here...
        print("<b>File > New</b> clicked")

    def openFile(self):
        # Logic for opening an existing file goes here...
        print("<b>File > Open...</b> clicked")

    def saveFile(self):
        # Logic for saving a file goes here...
        print("<b>File > Save</b> clicked")

    def copyContent(self):
        # Logic for copying content goes here...
        print("<b>Edit > Copy</b> clicked")

    def pasteContent(self):
        # Logic for pasting content goes here...
        print("<b>Edit > Paste</b> clicked")

    def cutContent(self):
        # Logic for cutting content goes here...
        print("<b>Edit > Cut</b> clicked")

    def helpContent(self):
        # Logic for launching help goes here...
        print("<b>Help > Help Content...</b> clicked")

    def about(self):
        # Logic for showing an about dialog content goes here...
        print("<b>Help > About...</b> clicked")
      
    def resetCamera(self):
        self.traceCanvas.reset_camera()
    
    def setRootTrace(self, root):
        self.traceCanvas.root_trace = int(root)
        self.traceCanvas.update_trace_views()
    
    def setViewCount(self, count):
        self.traceCanvas.view_count = int(count)
        # TODO would be nice to not rebuild it..
        self.traceCanvas.build_canvas()
        self.centralWidget = self.traceCanvas.canvas.native
        self.setCentralWidget(self.centralWidget)


    def populateOpenRecent(self):
        # Step 1. Remove the old options from the menu
        self.openRecentMenu.clear()
        # Step 2. Dynamically create the actions
        actions = []
        filenames = [f"File-{n}" for n in range(5)]
        for filename in filenames:
            action = QAction(filename, self)
            action.triggered.connect(partial(self.openRecentFile, filename))
            actions.append(action)
        # Step 3. Add the actions to the menu
        self.openRecentMenu.addActions(actions)

    def openRecentFile(self, filename):
        # Logic for opening a recent file goes here...
        self.centralWidget.setText(f"<b>{filename}</b> opened")

    def getWordCount(self):
        # Logic for computing the word count goes here...
        return 42

class TraceCanvas:
    def __init__(self, file_adapter, view_count=3):
        self.file_adapter = file_adapter

        # def on_mouse_double_click(event):
        #     print('on_mouse_double_click!')
        # def on_mouse_wheel(event):
        #     print('on_mouse_wheel!')
        def on_mouse_press(event):
            print('on_mouse_press!')
        def on_mouse_release(event):
            print('on_mouse_release!')
        def on_mouse_move(event):
            print('on_mouse_move!')
        def on_key_press(event):
            print('on_key_press!')
        def on_key_release(event):
            print('on_key_release!')

        self.root_trace = 1
        self.view_count = view_count
        self.views = {}
        self.canvas = None

        self.build_canvas()

        # self.canvas.connect(on_mouse_double_click)
        # self.canvas.connect(on_mouse_wheel)
        # self.canvas.connect(on_mouse_press)
        # self.canvas.connect(on_mouse_release)
        # self.canvas.connect(on_mouse_move)
        # self.canvas.connect(on_key_press)
        # self.canvas.connect(on_key_release)

    def build_canvas(self):
        if self.canvas:
            self.canvas.close()
            self.views = {}

        self.canvas = SceneCanvas(
            size=(1280, 900),
            position=(200, 200),
            keys="interactive",
            bgcolor="#222",
            parent=None,
        )

        self.grid = self.canvas.central_widget.add_grid(spacing=0)
        for view_pos in range(self.view_count):
            self.add_trace_views(view_pos)
        
        self.update_trace_views()
        self.link_cameras()
        self.reset_camera()
        pass
        # self.views[0].camera.set_range(x=(line_data[0].min(), line_data[0].max()), y=(line_data[1].min(), line_data[1].max()), margin=0)




        # self.x_axis2 = AxisWidget(orientation="bottom")
        # self.y_axis2 = AxisWidget(orientation="left")
        # self.x_axis2.stretch = (1, 0.05)
        # self.y_axis2.stretch = (0.05, 1)
        # self.grid.add_widget(self.x_axis2, row=3, col=1)
        # self.grid.add_widget(self.y_axis2, row=2, col=0)
        # self.view2 = self.grid.add_view(2, 1, camera="panzoom")
        # self.x_axis2.link_view(self.view2)
        # self.y_axis2.link_view(self.view2)

        # line_data = np.empty((2, TRACES[2].shape[0]), np.uint32)
        # line_data[0] = np.arange(len(TRACES[2]))
        # line_data[1] = TRACES[2]
        # self.line = visuals.Line(line_data.T, parent=self.view2.scene, color=LINE_COLOR_CHOICES[0])
        
        # self.view2.camera.set_range(x=(line_data[0].min(), line_data[0].max()), y=(line_data[1].min(), line_data[1].max()))

        # self.view2.camera.link(self.view.camera)

    def add_trace_views(self, view_pos):

        """
        yaxis | line
        --------------
          /   | xaxis
        
        """

        line_view = self.grid.add_view(row=view_pos, col=1)
        line_view.camera = ScaZoomCamera()
        self.views[view_pos] = line_view
        visuals.Line(parent=line_view.scene, color="white")
        visuals.GridLines(parent=line_view.scene)

        y_axis = AxisWidget(orientation="left")
        y_axis.stretch = (0.05, 1)
        self.grid.add_widget(y_axis, row=view_pos, col=0)
        y_axis.link_view(line_view)

        if view_pos == self.view_count - 1:
            x_axis = AxisWidget(orientation="bottom")
            x_axis.stretch = (1, .2)
            self.grid.add_widget(x_axis, row=view_pos+1, col=1)
            x_axis.link_view(line_view)

    def update_trace_views(self):
        for view_pos in range(self.view_count):
            line_data = self.file_adapter.raw_to_plot(self.file_adapter.TRACES[(self.root_trace + view_pos) % (len(self.file_adapter.TRACES))])
            if view_pos == 0:
                self.lims = (line_data.T[0].min(), line_data.T[0].max()), (line_data.T[1].min(), line_data.T[1].max())

            self.views[view_pos].scene.children
            line = next(filter( lambda x: isinstance(x, visuals.Line), self.views[view_pos].scene.children))

            line.set_data(line_data)

    def link_cameras(self):
        for _, view in list(self.views.items())[1:]:
            self.views[0].camera.link(view.camera)
        
    def reset_camera(self):
        self.views[0].camera.set_range(*self.lims, margin=0)
        
    def set_line_color(self, color):
        print(f"Changing line color to {color}")
        for view_pos in range(self.view_count):
            line = next(filter( lambda x: isinstance(x, visuals.Line), self.views[view_pos].scene.children))
            line.set_data(color=color)



