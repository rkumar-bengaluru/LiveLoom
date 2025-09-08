# main.py
import sys
import os
import signal
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer

# Import MainWindow from src/ui
from src.ui.main_window import MainWindow  # ✅ Clean import

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()

    # Handle Ctrl+C
    signal.signal(signal.SIGINT, lambda sig, frame: app.quit())
    timer = QTimer()
    timer.start(500)
    timer.timeout.connect(lambda: None)

    sys.exit(app.exec())

if __name__ == "__main__":
    main()