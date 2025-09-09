# ui/chat_tab.py
from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QPushButton,
    QTextEdit, QLineEdit, QComboBox, QLabel, QListWidget,
    QFrame
)
from PyQt6.QtGui import QTextCursor
from PyQt6.QtCore import Qt
from src.ui.widgets.llm_selector import LLMSelector
from src.workers.llm_worker import LLMWorkerThread
from src.utils.logger import setup_daily_logger
from src.utils.constants import LOGGER_DIR, LOGGER_NAME
from src.llm.wrapper import LLMWrapper
from src.chat.chat import ChatModule
from src.chat.session import FlatChatSessionLogger
import queue 
import os 
import threading 

class ChatTab(QWidget):
    def __init__(self, settings):
        super().__init__()
        self.settings = settings 
        self.answer_queue = queue.Queue()
        self.logger = setup_daily_logger(name=LOGGER_NAME, log_dir=LOGGER_DIR)
        self.llm = LLMWrapper(model=self.settings.get_current_model(),
                              api_url=self.settings.get_current_url(),
                              api_key=self.settings.get_current_key(),
                              answer_queue=self.answer_queue)
        model = self.settings.get_current_model()
        url = self.settings.get_current_url()
        self.logger.info("initializing...%s with url %s", model, url)
        self.session = FlatChatSessionLogger()
        self.chatModule = ChatModule(self.llm, self)
        
        # add workers
        # Start worker thread
        self.worker = LLMWorkerThread()
        self.worker.set_app(self)
        self.worker.update_signal.connect(self.update_display)  # Connect signal to slot
        self.worker.start()

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
        self.recent_sessions = self.session.get_recent_sessions()
        self.recent_list.setStyleSheet("""
            QListWidget::item:selected {
                background-color: #d0eaff;
                color: black;
            }
            """)
        self.sample_sessions = []
        for session in self.recent_sessions:
            self.sample_sessions.append(os.path.basename(session))
        # Connect the click signal
        self.recent_list.itemClicked.connect(self.on_item_clicked)
       
        self.recent_list.addItems(self.sample_sessions)
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

        
        

    # --- Dummy Functions (Replace Later) ---

    def refresh_list_widget(self,list_widget: QListWidget, items: list[str]):
        list_widget.clear()               # Remove all existing items
        list_widget.addItems(items)       # Add new items

    def update_display(self, delta):
        # self.chat_display.append(f"<b>{self.llm_selector.model_name}</b>: ")
        if delta == "data: [DONE]":
            self.chat_display.append(f"<b>{self.llm_selector.model_name} : Done...</b><br><br> ")
        else:
            self.chat_display.moveCursor(QTextCursor.MoveOperation.End)
            self.chat_display.insertPlainText(delta)

        # self.chat_display.append(text)

    def on_item_clicked(self, item):
        for session in self.recent_sessions:
            if item.text() in session:
                try:
                    with open(session, "r", encoding="utf-8") as f:
                        content = f.read()
                        self.chat_display.setPlainText(content)
                except Exception as e:
                    self.chat_display.setPlainText(f"Error loading file:\n{e}")
        

    def on_new_chat(self):
        self.logger.info("[UI Action] New Chat clicked")
        new_session = self.session._create_session_file()
        self.recent_sessions = self.session.get_recent_sessions()
        self.sample_sessions = []
        
        for session in self.recent_sessions:
            self.sample_sessions.append(os.path.basename(session))
        self.refresh_list_widget(self.recent_list, self.sample_sessions)
        # Refresh Diplay with new file
        try:
            with open(new_session, "r", encoding="utf-8") as f:
                content = f.read()
                self.chat_display.setPlainText(content)
        except Exception as e:
            self.chat_display.setPlainText(f"Error loading file:\n{e}")

    

    def on_send_chat(self):
        user_text = self.input_box.text().strip()
        if not user_text:
            return
        
        if self.session.session_file is None:
            self.on_new_chat()

        # Get selected model
        model_name = self.llm_selector.model_name

        # Append to chat display
        self.chat_display.append(f"<b>You</b> <i>(via {model_name})</i>: {user_text}<br><br><b>{self.llm_selector.model_name}</b>:")
        # Using positional arguments
        thread1 = threading.Thread(target=chat_async, args=(self.chatModule.chat_with_llm, user_text))
        thread1.start()

        # Clear input
        self.input_box.clear()

def chat_async(chat, input_text):
    chat(input_text)