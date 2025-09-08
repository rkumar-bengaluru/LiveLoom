# ui/main_window.py
from PyQt6.QtWidgets import QMainWindow, QTabWidget, QLabel
from PyQt6.QtGui import QGuiApplication
from PyQt6.QtCore import Qt


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("LLM Chat UI - Mock")

        with open("src/resources/style.qss", "r") as f:
            self.setStyleSheet(f.read())

        # 💥 Set window to 100% width, 30% height, docked at bottom (above taskbar)
        screen = QGuiApplication.primaryScreen().availableGeometry()
        width = screen.width()
        height = int(screen.height() * 0.30)  # 30% of available height
        x = screen.left()
        y = screen.bottom() - height          # Just above taskbar

        # 💥 HIDE FROM TASKBAR
        # self.setWindowFlag(Qt.WindowType.Tool)

        self.setGeometry(x, y, width, height)

        # Optional: Disable resizing if you want a fixed bar
        # self.setFixedSize(width, height)

        # Optional: Frameless window (no title bar) for cleaner look
        # self.setWindowFlag(Qt.WindowType.FramelessWindowHint)

        # Optional: Always on top (like a desktop assistant)
        # self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint)

        # Central Tab Widget
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        # Add Chat Tab
        from .chat_tab import ChatTab
        self.chat_tab = ChatTab()
        self.tabs.addTab(self.chat_tab, "Chat")

        # Add Settings Tab (placeholder)
        from .settings_tab import SettingsTab
        settings_placeholder = SettingsTab()
        # settings_placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.tabs.addTab(settings_placeholder, "Settings")


    def keyPressEvent(self, event):
        """Handle global key presses for window movement and AltGr"""
        key = event.key()
        mod = event.modifiers()
        step = 10  # pixels to move per keypress

        # Arrow keys to move window
        if key == Qt.Key.Key_Left:
            self.move(self.x() - step, self.y())
            event.accept()
        elif key == Qt.Key.Key_Right:
            self.move(self.x() + step, self.y())
            event.accept()
        elif key == Qt.Key.Key_Up:
            self.move(self.x(), self.y() - step)
            event.accept()
        elif key == Qt.Key.Key_Down:
            self.move(self.x(), self.y() + step)
            event.accept()


        # AltGr detection (Right Alt)
        # On Windows/Linux: AltGr = Key.Key_AltGr
        # On macOS: Option key may behave differently
        

        else:
            super().keyPressEvent(event)  # Let parent handle other keys
