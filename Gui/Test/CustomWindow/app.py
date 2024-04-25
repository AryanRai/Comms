from PySide6.QtWidgets import QApplication, QWidget
from PySide6.QtWidgets import QApplication, QWidget
from PySide6.QtWebEngineWidgets import QWebEngineView
import sys
from PySide6.QtWidgets import QVBoxLayout
from PySide6.QtCore import QUrl
from PySide6.QtWebEngineWidgets import QWebEngineView
# modify qevent code to work with PySide6
from PySide6.QtCore import QEvent
import webview

class MyApp(QApplication):
    def event(self, event: QEvent):
        if event.type() == QEvent.Type.ApplicationActivate:
            window.set_title("In focus")
        if event.type() == QEvent.Type.ApplicationDeactivate:
            window.set_title("Not in focus")
        return super(QApplication, self).event(event)


if __name__ == '__main__':
    app = MyApp(sys.argv)
    window = webview.create_window('Hello world', 'https://alvinwan.com/blog/')
    webview.start(gui='qt')