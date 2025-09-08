import os
from pathlib import Path

from src.utils.constants import SESSION_DIR,LOGGER_NAME,LOGGER_DIR
import os
from datetime import datetime
from pathlib import Path
from src.utils.logger import setup_daily_logger

import os
from datetime import datetime
from pathlib import Path

class FlatChatSessionLogger:
    def __init__(self, base_dir=SESSION_DIR):
        self.logger = setup_daily_logger(name=LOGGER_NAME, log_dir=LOGGER_DIR)
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.session_file = self._create_session_file()

    def _create_session_file(self) -> Path:
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        file_path = self.base_dir / f"{timestamp}.txt"
        file_path.touch(exist_ok=False)
        self.logger.info(f"creating session {file_path}")
        return file_path

    def log_interaction(self, question: str, answer: str):
        self.logger.info("logging new interaction")
        with self.session_file.open("a", encoding="utf-8") as f:
            f.write(f"Q: {question}\n")
            f.write(f"A: {answer}\n\n")

    @staticmethod
    def get_recent_sessions(base_dir=SESSION_DIR, count=7) -> list[str]:
        base_path = Path(base_dir)
        if not base_path.exists():
            return []

        # Filter only .txt files
        session_files = [f for f in base_path.glob("*.txt") if f.is_file()]

        # Sort by creation time (descending)
        sorted_files = sorted(
            session_files,
            key=lambda f: f.stat().st_ctime,
            reverse=True
        )

        return [str(f) for f in sorted_files[:count]]

