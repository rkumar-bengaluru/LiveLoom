# ui/settings_tab.py
import json
import os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget, QTableWidgetItem,
    QPushButton, QDialog, QLineEdit, QFormLayout, QDialogButtonBox,
    QMessageBox, QHeaderView
)
from PyQt6.QtCore import Qt

SETTINGS_FILE = "settings.json"

class SettingsTab(QWidget):
    def __init__(self):
        super().__init__()
        self.models = []
        self.init_ui()
        self.load_models()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

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

        layout.addWidget(top_section, 1)  # 50% height

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

        layout.addWidget(bottom_section, 1)  # 50% height

        # Connect selection change to enable/disable delete button
        self.model_table.itemSelectionChanged.connect(self.on_selection_changed)

    def on_selection_changed(self):
        """Enable Delete button only if a row is selected"""
        self.delete_btn.setEnabled(self.model_table.currentRow() >= 0)

    def load_models(self):
        """Load models from settings.json and populate table"""
        self.models = []
        self.model_table.setRowCount(0)  # Clear table

        if not os.path.exists(SETTINGS_FILE):
            self.create_default_settings()
            return

        try:
            with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.models = data.get("models", [])
        except (json.JSONDecodeError, Exception) as e:
            print(f"[ERROR] Failed to load settings.json: {e}")
            self.models = []

        # Populate table
        for model in self.models:
            row = self.model_table.rowCount()
            self.model_table.insertRow(row)

            name_item = QTableWidgetItem(model.get('modelName', 'Unknown'))
            url_item = QTableWidgetItem(model.get('apiUrl', ''))
            key_item = QTableWidgetItem(model.get('apiKey', ''))

            # Optional: Mask API key in UI
            if key_item.text():
                key_item.setText("•" * len(key_item.text()))

            # Store original API key in item data (so we can save it back later)
            key_item.setData(Qt.ItemDataRole.UserRole, model.get('apiKey', ''))

            self.model_table.setItem(row, 0, name_item)
            self.model_table.setItem(row, 1, url_item)
            self.model_table.setItem(row, 2, key_item)

    def create_default_settings(self):
        """Create default settings.json if not exists"""
        default_data = {
            "models": [
                {
                    "modelName": "Qwen (Default)",
                    "apiUrl": "https://api.qwen.ai/v1/chat",
                    "apiKey": "your_default_key_here"
                }
            ]
        }
        with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
            json.dump(default_data, f, indent=2)
        print(f"[INFO] Created default {SETTINGS_FILE}")

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

            new_model = {"modelName": name, "apiUrl": url, "apiKey": key}
            self.models.append(new_model)
            self.save_models_to_file()
            self.load_models()  # Refresh table
            dialog.accept()

        button_box.accepted.connect(save_and_close)
        button_box.rejected.connect(dialog.reject)

        dialog.exec()

    def save_models_to_file(self):
        """Write models back to settings.json"""
        data = {"models": self.models}
        try:
            with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            print(f"[INFO] Saved {len(self.models)} models to {SETTINGS_FILE}")
        except Exception as e:
            QMessageBox.critical(self, "Save Error", f"Failed to save: {e}")

    def delete_selected_model(self):
        """Delete selected model"""
        row = self.model_table.currentRow()
        if row < 0:
            return

        model_name = self.models[row]['modelName']
        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Are you sure you want to delete '{model_name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            del self.models[row]
            self.save_models_to_file()
            self.load_models()  # Refresh table