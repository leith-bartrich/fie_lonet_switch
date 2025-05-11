import sys
from PySide6.QtWidgets import QApplication, QSystemTrayIcon, QMenu, QAction
from PySide6.QtGui import QIcon

def main():
    app = QApplication(sys.argv)
    tray = QSystemTrayIcon()
    tray.setIcon(QIcon())  # You can set a custom icon here
    
    menu = QMenu()
    quit_action = QAction("Quit")
    quit_action.triggered.connect(app.quit)
    menu.addAction(quit_action)
    tray.setContextMenu(menu)
    tray.show()
    sys.exit(app.exec())