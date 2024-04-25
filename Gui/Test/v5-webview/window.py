import sys
from PyQt6 import QtCore
from PyQt6.QtCore import QUrl
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWidgets import QApplication, QMainWindow

if __name__ == '__main__':
    app = QApplication(sys.argv)

    # Create a main window
    window = QMainWindow()
    window.setWindowTitle("WebView Example")
    window.setGeometry(100, 100, 800, 600)

    # Create a WebView
    webview = QWebEngineView(window)
    webview.load(QUrl("https://www.example.com"))

    # Set the WebView as the central widget of the main window
    window.setCentralWidget(webview)

    # Show the main window
    window.show()

    # Run the application event loop
    sys.exit(app.exec())

    
