import sys
import time
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget
from PyQt6.QtCore import QThread, pyqtSignal

class LLMWorkerThread(QThread):
    # Define a signal to send data to main thread
    update_signal = pyqtSignal(str)

    def run(self):
        for i in range(100):
            time.sleep(1)
            # ✅ SAFE: Emit signal → slot in main thread will update UI
            self.update_signal.emit(f"Step {i + 1} completed")
