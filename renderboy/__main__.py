"""Main entry point for the RenderBoy application."""

if __name__ == "__main__":
    import sys
    from PySide2 import QtWidgets

    from ui.renderboyWindow import RenderBoyWindow

    app = QtWidgets.QApplication(sys.argv)
    window = RenderBoyWindow()
    window.show()
    sys.exit(app.exec_())
