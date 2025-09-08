# ui/chat_tab.py
from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QPushButton,
    QTextEdit, QLineEdit, QComboBox, QLabel, QListWidget,
    QFrame
)
from PyQt6.QtCore import Qt
from src.ui.widgets.llm_selector import LLMSelector
from src.workers.llm_worker import LLMWorkerThread

class ChatTab(QWidget):
    def __init__(self, settings):
        super().__init__()
        self.settings = settings 
        self.init_ui()

    def init_ui(self):
        # Main Horizontal Layout (Sidebar 20% + Chat Area 80%)
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # --- LEFT SIDEBAR ---
        sidebar = QFrame()
        sidebar.setFixedWidth(240)  # ~20% of 1200px
        sidebar.setStyleSheet("background-color: #f5f5f5; border-right: 1px solid #ddd;")
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(10, 20, 10, 20)

        # New Chat Button
        new_chat_btn = QPushButton("+ New Chat")
        new_chat_btn.setStyleSheet("font-weight: bold; padding: 10px; background-color: #1890ff; color: white; border-radius: 5px;")
        new_chat_btn.clicked.connect(self.on_new_chat)
        sidebar_layout.addWidget(new_chat_btn)

        # Recent Sessions Label
        recent_label = QLabel("Recent (Last 7 Days)")
        recent_label.setStyleSheet("font-weight: bold; margin-top: 20px; margin-bottom: 10px;")
        sidebar_layout.addWidget(recent_label)

        # Recent Sessions List
        self.recent_list = QListWidget()
        sample_sessions = [
            "Chat about Python PyQt6",
            "Explain quantum computing",
            "Write a poem about AI",
            "Debug my React code",
            "Compare LLMs: Gemini vs Llama"
        ]
        self.recent_list.addItems(sample_sessions)
        self.recent_list.setStyleSheet("border: 1px solid #ddd; border-radius: 5px;")
        sidebar_layout.addWidget(self.recent_list)

        sidebar_layout.addStretch()  # Push everything to top

        # --- MAIN CHAT AREA ---
        chat_area = QWidget()
        chat_layout = QVBoxLayout(chat_area)
        chat_layout.setContentsMargins(20, 20, 20, 20)

        # Chat Display (Scrollable)
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setStyleSheet("font-size: 14px; border: 1px solid #ddd; border-radius: 8px; padding: 10px;")
        self.chat_display.setPlaceholderText("Your conversation will appear here...")
        chat_layout.addWidget(self.chat_display, 1)  # Take available space

        # Input Area (Model Picker + Text Box + Button)
        input_container = QWidget()
        input_layout = QHBoxLayout(input_container)
        input_layout.setContentsMargins(0, 10, 0, 0)
        input_layout.setSpacing(10)

        

        # Text Input
        self.input_box = QLineEdit()
        self.input_box.setPlaceholderText("Type your message here...")
        self.input_box.setStyleSheet("padding: 8px; font-size: 14px; border: 1px solid #ddd; border-radius: 4px;")
        self.input_box.returnPressed.connect(self.on_send_chat)  # Enter key sends
        input_layout.addWidget(self.input_box, 1)  # Take remaining space

        # Send Button
        self.send_button = QPushButton("Chat")
        self.send_button.setFixedWidth(80)
        self.send_button.setStyleSheet("padding: 8px; background-color: #52c41a; color: white; border-radius: 4px; font-weight: bold;")
        self.send_button.clicked.connect(self.on_send_chat)
        input_layout.addWidget(self.send_button)

        chat_layout.addWidget(input_container)

        # Model Picker
        self.llm_selector = LLMSelector(self.settings)
        input_layout.addWidget(self.llm_selector)

        # Add Sidebar and Chat Area to Main Layout
        main_layout.addWidget(sidebar)
        main_layout.addWidget(chat_area, 1)  # Take remaining space

        
        # add workers
         # Start worker thread
        self.worker = LLMWorkerThread()
        self.worker.update_signal.connect(self.update_display)  # Connect signal to slot
        self.worker.start()

    # --- Dummy Functions (Replace Later) ---

    def update_display(self, text):
        self.chat_display.append(f"<b>{self.llm_selector.model_name}</b>: {text}")

    def on_new_chat(self):
        print("[UI Action] New Chat clicked")
        # Clear chat_display, reset state, etc.

    def on_send_chat(self):
        user_text = self.input_box.text().strip()
        if not user_text:
            return

        # Get selected model
        model_name = self.model_picker.currentText()

        # Append to chat display
        self.chat_display.append(f"<b>You</b> <i>(via {model_name})</i>: {user_text}")
        self.chat_display.append(f"<b>{model_name}</b>: This is a mock response. Integrate your LLM logic here!")
        self.chat_display.append("")  # Blank line

        # Clear input
        self.input_box.clear()