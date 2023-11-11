from Qt import QtGui, QtWidgets


class SplashScreen(QtWidgets.QSplashScreen):
    """A widget that provides a QSplashScreen that can be used for long
    load times.  This subclass can use both static and animated images.

    Args:
        path_to_image (string): The full filepath to an image.
    """

    def __init__(self, path_to_image: str):
        # QMovie can be used for both animated and static images
        self.movie = QtGui.QMovie(path_to_image)
        self.movie.jumpToFrame(0)
        pixmap = QtGui.QPixmap(self.movie.frameRect().size())
        QtWidgets.QSplashScreen.__init__(self, pixmap)
        self.movie.frameChanged.connect(self.repaint)

    def showEvent(self, event):  # noqa: N802
        self.movie.start()

    def hideEvent(self, event):  # noqa: N802
        self.movie.stop()

    def paintEvent(self, event):  # noqa: N802
        painter = QtGui.QPainter(self)
        pixmap = self.movie.currentPixmap()
        self.setMask(pixmap.mask())
        painter.drawPixmap(0, 0, pixmap)
