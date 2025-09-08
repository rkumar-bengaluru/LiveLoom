import sys
import time
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget
from PyQt6.QtCore import QThread, pyqtSignal

class LLMWorkerThread(QThread):
    # Define a signal to send data to main thread
    update_signal = pyqtSignal(str)

    def run(self):
        for i in range(5):
            time.sleep(1)
            # ✅ SAFE: Emit signal → slot in main thread will update UI
            self.update_signal.emit(f"Step {i + 1} completed")

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Thread-Safe UI Update")
        self.setGeometry(100, 100, 400, 200)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        self.status_label = QLabel("Click Start to begin background task...")
        layout.addWidget(self.status_label)

        # Start worker thread
        self.worker = WorkerThread()
        self.worker.update_signal.connect(self.update_label)  # Connect signal to slot
        self.worker.start()

    def update_label(self, text):
        # ✅ This runs in MAIN THREAD — SAFE to update UI
        self.status_label.setText(text)
