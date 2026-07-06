"""文件状态追踪（用于增量更新）"""
import json
import hashlib
import logging
from pathlib import Path
from typing import Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class FileStateTracker:
    """追踪已处理文件的状态，仅处理变更文件"""

    def __init__(self, state_file: Path):
        self.state_file = state_file
        self.states = self._load()

    def _load(self) -> Dict[str, Dict[str, Any]]:
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"加载状态文件失败: {e}")
        return {}

    def save(self):
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.state_file, 'w', encoding='utf-8') as f:
            json.dump(self.states, f, ensure_ascii=False, indent=2)

    def get_file_hash(self, file_path: Path) -> str:
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()

    def is_changed(self, file_path: Path) -> bool:
        key = str(file_path)
        current_mtime = file_path.stat().st_mtime
        current_hash = self.get_file_hash(file_path)

        if key not in self.states:
            return True

        old_state = self.states[key]
        return (old_state.get('mtime') != current_mtime or
                old_state.get('hash') != current_hash)

    def update(self, file_path: Path, chunks_count: int):
        key = str(file_path)
        self.states[key] = {
            'mtime': file_path.stat().st_mtime,
            'hash': self.get_file_hash(file_path),
            'chunks_count': chunks_count,
            'updated_at': datetime.now().isoformat()
        }
