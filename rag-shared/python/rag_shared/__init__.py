"""
RAG 共享库 - 可被 DixyangFast 和 dixiyang-engine/python_api 共同使用
"""
from .config import (
    load_config,
    get_config_summary,
    detect_hardware,
    RAGConfig,
    get_config,
    reset_config,
)
from .processor import RAGProcessor, DocumentChunk, FileStateTracker

__version__ = "0.1.0"
__all__ = [
    "load_config",
    "get_config_summary",
    "detect_hardware",
    "RAGConfig",
    "get_config",
    "reset_config",
    "RAGProcessor",
    "DocumentChunk",
    "FileStateTracker",
]