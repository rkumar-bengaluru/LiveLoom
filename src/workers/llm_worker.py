import sys
import time
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget
from PyQt6.QtCore import QThread, pyqtSignal
import queue 

class LLMWorkerThread(QThread):

    update_signal = pyqtSignal(str)

    def set_app(self, app):
        self.app = app 

    def run(self):
        while True:
            try:
                response = self.app.answer_queue.get(timeout=0.5) 
                self.update_signal.emit(response)
            except queue.Empty:
                response = None  # Or handle retry logic
       
        
