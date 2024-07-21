from vispy.app import use_app

from .qtgui import Window

def fakemain():
    # Create the application
    app = use_app("pyqt6")
    app.create()
    # app = QApplication(sys.argv)
    # Create and show the main window
    win = Window()
    win.show()
    app.run()
    # Run the event loop
    # sys.exit(app.exec())

if __name__ == "__main__":
    fakemain()
