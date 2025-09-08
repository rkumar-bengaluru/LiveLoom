from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QComboBox
import sys
from src.utils.constants import LOGGER_DIR, LOGGER_NAME
from src.utils.logger import setup_daily_logger

class LLMSelector(QWidget):
    def __init__(self, settings):
        super().__init__()
        self.settings = settings 
        self.logger = setup_daily_logger(name=LOGGER_NAME, log_dir=LOGGER_DIR)

        self.combo = QComboBox()
        self.model_name = self.settings.get_current_model()
        self.models = self.settings.get_model_names()
        

        # Add model options
        self.combo.addItems(self.models)

        # Load saved model and set as default
        saved_model = self.settings.get_current_model()
        if saved_model in self.models:
            index = self.models.index(saved_model)
            self.combo.setCurrentIndex(index)

        self.combo.currentTextChanged.connect(self.model_selected)


        # Connect selection change to handler
        self.combo.currentTextChanged.connect(self.model_selected)

        layout = QVBoxLayout()
        layout.addWidget(self.combo)
        self.setLayout(layout)

    def model_selected(self, model_name):
        self.logger.info(f"Selected model: {model_name}")
        self.model_name = model_name
        self.settings.change_current_model(model_name)
        # You can trigger model hydration, failover logic, etc. here
