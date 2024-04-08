import sys
import json
import pygetwindow as gw
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QRubberBand,
    QWidget,
    QDesktopWidget,
)
from PyQt5.QtCore import Qt, QPoint, QRect, QSize, pyqtSignal
import os


class TransparentWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TranslucentBackground)


class ScreenSelector(QMainWindow):
    closed = pyqtSignal()  # Создаем сигнал для сообщения о закрытии окна

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        width, height = self.get_screen_resolution()

        self.setWindowTitle("Screen Selector")
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.setWindowOpacity(0.1)

        self.contentWidget = TransparentWidget(self)
        self.setCentralWidget(self.contentWidget)

        self.rubberBand = QRubberBand(QRubberBand.Rectangle, self)
        self.setMouseTracking(True)

        self.resize(width, height)
        self.center()

    def get_screen_resolution(self):
        screen = QDesktopWidget().screenGeometry()
        width, height = screen.width(), screen.height()
        return width, height

    def center(self):
        screen_geometry = QDesktopWidget().screenGeometry()
        window_geometry = self.geometry()
        x = (screen_geometry.width() - window_geometry.width()) // 2
        y = (screen_geometry.height() - window_geometry.height()) // 2
        self.move(x, y)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.origin = QPoint(event.pos())
            self.rubberBand.setGeometry(QRect(self.origin, QSize()))
            self.rubberBand.show()

    def mouseMoveEvent(self, event):
        if self.rubberBand.isVisible():
            self.rubberBand.setGeometry(QRect(self.origin, event.pos()).normalized())

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.rubberBand.hide()
            selected_area = self.rubberBand.geometry()
            print("Selected area:", selected_area)
            self.closed.emit()  # Отправляем сигнал о закрытии окна


class ScreenSelectorApplication:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.ar_dict = None

    def main(self):
        target_window = gw.getWindowsWithTitle("stalcraft")
        if not target_window:
            print("Window not found")
            return None
        target_window[0].maximize()
        screen_selector = ScreenSelector()
        screen_selector.show()

        try:

            def on_screen_selector_closed():  # Функция, которая будет вызвана при закрытии ScreenSelector
                target_window[0].minimize()
                self.ar_dict = {
                    "x": screen_selector.rubberBand.geometry().x(),
                    "y": screen_selector.rubberBand.geometry().y() + 34,
                    "width": screen_selector.rubberBand.geometry().width(),
                    "height": screen_selector.rubberBand.geometry().height(),
                }
                current_directory = os.path.dirname(os.path.abspath(__file__))
                file_path = os.path.join(current_directory, "ar_data.json")

                with open(file_path, "w") as json_file:
                    json.dump(self.ar_dict, json_file)
                screen_selector.close()  # Закрываем окно ScreenSelector

            screen_selector.closed.connect(on_screen_selector_closed)

            self.app.exec()
            return self.ar_dict

        except Exception as e:
            print("An error occurred:", e)
            return None


def main():
    a = ScreenSelectorApplication()
    a.main()
