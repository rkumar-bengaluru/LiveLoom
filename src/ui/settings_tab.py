# ui/settings_tab.py
import json
import os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget, QTableWidgetItem,
    QPushButton, QDialog, QLineEdit, QFormLayout, QDialogButtonBox,
    QMessageBox, QHeaderView, QCheckBox
)
from PyQt6.QtCore import Qt
from src.utils.constants import LOGGER_DIR, LOGGER_NAME, SETTINGS_FILE
from src.utils.logger import setup_daily_logger

class SettingsTab(QWidget):
    def __init__(self):
        super().__init__()
        self.logger = setup_daily_logger(name=LOGGER_NAME, log_dir=LOGGER_DIR)
        self.init_ui()
        self.load_models()
        self.init_steaming()
        

    def init_steaming(self):
        stream_section = QWidget()
        stream_layout = QVBoxLayout(stream_section)
        stream_layout.setContentsMargins(0, 0, 0, 0)
        stream_layout.setSpacing(10)
        self.checkbox = QCheckBox("Enable Streaming")
        streaming_enabled = self.settings.get("enable_streaming")
        self.checkbox.setChecked(streaming_enabled)
        
        # Connect checkbox state change
        self.checkbox.stateChanged.connect(self.toggle_streaming)

        stream_layout.addWidget(self.checkbox)
        self.layout.addWidget(stream_section, 1)
        

    def init_ui(self):
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setSpacing(15)

        # === TOP SECTION: Saved Models Table (50%) ===
        top_section = QWidget()
        top_layout = QVBoxLayout(top_section)
        top_layout.setContentsMargins(0, 0, 0, 0)

        top_label = QLabel("Saved Models")
        top_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        top_layout.addWidget(top_label)

        # Create Table
        self.model_table = QTableWidget()
        self.model_table.setColumnCount(3)
        self.model_table.setHorizontalHeaderLabels(["Model Name", "API URL", "API Key"])
        self.model_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.model_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.model_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)  # Read-only

        # Resize columns to fit content
        header = self.model_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Interactive)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)

        # 💥 EQUAL COLUMN WIDTH
        header = self.model_table.horizontalHeader()
        for i in range(3):
            header.setSectionResizeMode(i, QHeaderView.ResizeMode.Stretch)

        top_layout.addWidget(self.model_table, 1)

        # Optional: Hide API Key column by default for security
        # self.model_table.setColumnHidden(2, True)

        top_layout.addWidget(self.model_table, 1)


        self.layout.addWidget(top_section, 3)  # 50% height

        # === BOTTOM SECTION: Buttons (50%) ===
        bottom_section = QWidget()
        bottom_layout = QVBoxLayout(bottom_section)
        bottom_layout.setContentsMargins(0, 0, 0, 0)
        bottom_layout.setSpacing(10)


        # Button Row
        button_row = QHBoxLayout()
        button_row.setSpacing(10)

        self.add_btn = QPushButton("Add Model")
        self.add_btn.clicked.connect(self.open_add_model_dialog)
        button_row.addWidget(self.add_btn)

        self.delete_btn = QPushButton("Delete Selected")
        self.delete_btn.clicked.connect(self.delete_selected_model)
        self.delete_btn.setEnabled(False)  # Disabled until selection
        button_row.addWidget(self.delete_btn)

        button_row.addStretch()  # Push buttons to left

        bottom_layout.addLayout(button_row)
        bottom_layout.addStretch()  # Push buttons to top of bottom section

        self.layout.addWidget(bottom_section, 1)  # 50% height

        # Connect selection change to enable/disable delete button
        self.model_table.itemSelectionChanged.connect(self.on_selection_changed)

        # === BOTTOM SECTION: Buttons (50%) ===
        


        
        
    def is_steaming(self):
        return self.settings["enable_streaming"]

    def toggle_streaming(self, state):
        if self.checkbox.isChecked():
            self.settings["enable_streaming"] = 1
            # self.label.setText("Streaming Mode: ON")
            # Trigger streaming logic here
        else:
            self.settings["enable_streaming"] = 0
            # self.label.setText("Streaming Mode: OFF")
            # Trigger non-streaming logic here
        self.save_models_to_file()


    def on_selection_changed(self):
        """Enable Delete button only if a row is selected"""
        self.delete_btn.setEnabled(self.model_table.currentRow() >= 0)

    def get_model_names(self):
        models = []
        for model in self.settings.get("models"):
            models.append(model.get("name"))
        return models 
    
    def change_current_model(self, name):
        for model in self.settings.get("models"):
            if model.get("name") == name:
                self.settings["model_name"] = name 
                self.settings["model_url"] = model.get("url")
                self.settings["model_key"] = model.get("key")
        self.save_models_to_file()
    
    def get_current_model(self):
        return self.settings.get("model_name")
    
    def get_current_key(self):
        return self.settings.get("model_key")
    
    def get_current_url(self):
        return self.settings.get("model_url")
    

    def load_models(self):
        """Load models from settings.json and populate table"""
        self.models = []
        self.model_table.setRowCount(0)  # Clear table

        if not os.path.exists(SETTINGS_FILE):
            self.settings = self.create_default_settings()
            return

        try:
            with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
                self.settings = json.load(f)
        except (json.JSONDecodeError, Exception) as e:
            self.logger.error(f"[ERROR] Failed to load settings.json: {e}")
            self.models = []
        
        # Populate table
        for model in self.settings.get("models"):
            row = self.model_table.rowCount()
            self.model_table.insertRow(row)

            name_item = QTableWidgetItem(model.get('name', 'Unknown'))
            url_item = QTableWidgetItem(model.get('url', ''))
            key_item = QTableWidgetItem(model.get('key', ''))

            # Optional: Mask API key in UI
            if key_item.text():
                key_item.setText("•" * len(key_item.text()))

            # Store original API key in item data (so we can save it back later)
            key_item.setData(Qt.ItemDataRole.UserRole, model.get('key', ''))

            self.model_table.setItem(row, 0, name_item)
            self.model_table.setItem(row, 1, url_item)
            self.model_table.setItem(row, 2, key_item)

    def create_default_settings(self):
        """Create default settings.json if not exists"""
        default_data = {
            "model_name": "gemini-2.0-flash",
            "model_url": "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions",
            "model_key": "XXX",
            "enable_streaming": 1,
            "whisper_model_name": "small.en",
            "models": [
                {
                    "name": "gemini-2.0-flash",
                    "url": "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions",
                    "key": "XXX"
                }
            ]
        }
        with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
            json.dump(default_data, f, indent=2)
        self.logger.info(f"[INFO] Created default {SETTINGS_FILE}")
        return default_data

    def open_add_model_dialog(self):
        """Open dialog to add new model"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Add New Model")
        dialog.setModal(True)
        dialog.resize(500, 200)

        layout = QFormLayout(dialog)

        name_input = QLineEdit()
        url_input = QLineEdit()
        key_input = QLineEdit()
        key_input.setEchoMode(QLineEdit.EchoMode.Password)  # Hide while typing

        layout.addRow("Model Name:", name_input)
        layout.addRow("API Endpoint:", url_input)
        layout.addRow("API Key:", key_input)

        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel
        )
        layout.addRow(button_box)

        def save_and_close():
            name = name_input.text().strip()
            url = url_input.text().strip()
            key = key_input.text().strip()

            if not name or not url:
                QMessageBox.warning(dialog, "Input Error", "Model Name and API Endpoint are required!")
                return

            new_model = {"name": name, "url": url, "key": key}
            self.settings.get("models").append(new_model)
            self.save_models_to_file()
            self.load_models()  # Refresh table
            dialog.accept()

        button_box.accepted.connect(save_and_close)
        button_box.rejected.connect(dialog.reject)

        dialog.exec()

    def save_models_to_file(self):
        """Write models back to settings.json"""
        try:
            with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=2)
            self.logger.info(f"[INFO] Saved {len(self.models)} models to {SETTINGS_FILE}")
        except Exception as e:
            QMessageBox.critical(self, "Save Error", f"Failed to save: {e}")

    def delete_selected_model(self):
        """Delete selected model"""
        row = self.model_table.currentRow()
        if row < 0:
            return

        model_name = self.settings.get("models")[row]['name']
        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Are you sure you want to delete '{model_name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            del self.settings.get("models")[row]
            self.save_models_to_file()
            self.load_models()  # Refresh table