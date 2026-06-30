"""
RAG 配置管理器
支持自动检测硬件、手动切换配置、配置合并
"""
import os
import yaml
import torch
import platform
from pathlib import Path
from typing import Dict, Any, Optional, Literal
from dataclasses import dataclass, field
import logging

logger = logging.getLogger(__name__)

CONFIG_DIR = Path(__file__).parent

# 硬件配置预设
HARDWARE_PRESETS = {
    "r5_5600u": "rag_r5_5600u.yaml",
    "rtx_4060": "rag_rtx_4060.yaml",
    "auto": "auto",
    "cpu_fallback": "rag_r5_5600u.yaml",
}

@dataclass
class RAGConfig:
    """RAG 配置数据类"""
    device: str = "cpu"
    precision: str = "fp32"
    
    # Embedding
    embedding_model: str = "BAAI/bge-small-zh-v1.5"
    embedding_batch_size: int = 16
    embedding_max_length: int = 512
    embedding_device: str = "cpu"
    embedding_half_precision: bool = False
    
    # Text Splitter
    chunk_size: int = 400
    chunk_overlap: int = 80
    
    # VectorDB
    vectordb_path: str = "./storage/vectordb"
    collection_name: str = "dixiyang_knowledge"
    
    # Retrieval
    top_k: int = 5
    score_threshold: float = 0.6
    use_reranker: bool = False
    reranker_model: str = "BAAI/bge-reranker-base"
    reranker_device: str = "cpu"
    reranker_batch_size: int = 8
    rerank_top_k: int = 10
    
    # Processing
    num_workers: int = 4
    batch_size: int = 32
    checkpoint_interval: int = 100
    incremental: bool = True
    preload_models: bool = False
    
    # Paths
    cache_dir: str = "./models/cache"
    books_dir: str = "./my_books"
    datasets_dir: str = "./datasets/datasets"
    chunks_dir: str = "./storage/rag/chunks"
    metadata_file: str = "./storage/rag/metadata.json"
    state_file: str = "./storage/rag/file_states.json"
    
    # Memory
    reserved_vram_mb: int = 1024
    auto_batch_size: bool = False
    
    # Raw config for advanced access
    raw: Dict[str, Any] = field(default_factory=dict)


def detect_hardware() -> str:
    """
    自动检测硬件类型
    返回: 'r5_5600u' | 'rtx_4060' | 'cpu_fallback'
    """
    # 检查 CUDA
    if torch.cuda.is_available():
        gpu_name = torch.cuda.get_device_name(0).lower()
        vram_gb = torch.cuda.get_device_properties(0).total_memory / 1024**3
        
        logger.info(f"检测到 GPU: {gpu_name}, VRAM: {vram_gb:.1f}GB")
        
        if "4060" in gpu_name or "rtx 4060" in gpu_name:
            return "rtx_4060"
        elif vram_gb >= 6:
            # 其他 NVIDIA GPU，按 4060 配置处理
            return "rtx_4060"
        else:
            # 低显存 GPU，回退 CPU
            logger.warning(f"GPU 显存较小 ({vram_gb:.1f}GB)，回退到 CPU 模式")
            return "cpu_fallback"
    
    # 检查 CPU 型号
    cpu_info = platform.processor().lower()
    if "5600u" in cpu_info or "ryzen 5 5600u" in cpu_info:
        logger.info("检测到 R5 5600U")
        return "r5_5600u"
    
    # 默认 CPU 模式
    logger.info("未检测到支持的 GPU，使用 CPU 模式")
    return "cpu_fallback"


def load_yaml(path: Path) -> Dict[str, Any]:
    """加载 YAML 配置文件"""
    if not path.exists():
        raise FileNotFoundError(f"配置文件不存在: {path}")
    with open(path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f) or {}


def deep_merge(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    """深度合并字典"""
    result = base.copy()
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value
    return result


def parse_config(raw: Dict[str, Any]) -> RAGConfig:
    """将原始配置字典解析为 RAGConfig 对象"""
    cfg = RAGConfig()
    cfg.raw = raw
    
    # 设备配置
    cfg.device = raw.get('device', 'cpu')
    cfg.precision = raw.get('precision', 'fp32')
    
    # Embedding
    emb = raw.get('embedding', {})
    cfg.embedding_model = emb.get('model_name', cfg.embedding_model)
    cfg.embedding_batch_size = emb.get('batch_size', cfg.embedding_batch_size)
    cfg.embedding_max_length = emb.get('max_length', cfg.embedding_max_length)
    enc_kwargs = emb.get('encode_kwargs', {})
    cfg.embedding_device = enc_kwargs.get('device', cfg.device)
    cfg.embedding_half_precision = enc_kwargs.get('half_precision', False)
    
    # Text Splitter
    ts = raw.get('text_splitter', {})
    cfg.chunk_size = ts.get('chunk_size', cfg.chunk_size)
    cfg.chunk_overlap = ts.get('chunk_overlap', cfg.chunk_overlap)
    
    # VectorDB
    vdb = raw.get('vectordb', {})
    cfg.vectordb_path = vdb.get('persist_directory', cfg.vectordb_path)
    cfg.collection_name = vdb.get('collection_name', cfg.collection_name)
    
    # Retrieval
    ret = raw.get('retrieval', {})
    cfg.top_k = ret.get('top_k', cfg.top_k)
    cfg.score_threshold = ret.get('score_threshold', cfg.score_threshold)
    cfg.use_reranker = ret.get('use_reranker', cfg.use_reranker)
    cfg.reranker_model = ret.get('reranker_model', cfg.reranker_model)
    cfg.reranker_device = ret.get('rerank_device', cfg.device)
    cfg.reranker_batch_size = ret.get('reranker_batch_size', cfg.reranker_batch_size)
    cfg.rerank_top_k = ret.get('rerank_top_k', cfg.rerank_top_k)
    
    # Processing
    proc = raw.get('processing', {})
    cfg.num_workers = proc.get('num_workers', cfg.num_workers)
    cfg.batch_size = proc.get('batch_size', cfg.batch_size)
    cfg.checkpoint_interval = proc.get('checkpoint_interval', cfg.checkpoint_interval)
    cfg.incremental = proc.get('incremental', cfg.incremental)
    cfg.preload_models = proc.get('preload_models', cfg.preload_models)
    
    # Paths
    cfg.cache_dir = raw.get('cache_dir', cfg.cache_dir)
    
    # Memory
    mem = raw.get('memory_management', {})
    cfg.reserved_vram_mb = mem.get('reserved_vram_mb', cfg.reserved_vram_mb)
    cfg.auto_batch_size = mem.get('auto_batch_size', cfg.auto_batch_size)
    
    return cfg


def load_config(
    hardware: Optional[str] = None,
    config_dir: Optional[Path] = None,
    base_config_name: str = "rag_base.yaml"
) -> RAGConfig:
    """
    加载并合并配置
    
    Args:
        hardware: 硬件预设名称 ('r5_5600u', 'rtx_4060', 'auto')，None 则自动检测
        config_dir: 配置目录，默认当前文件目录
        base_config_name: 基础配置文件名
    
    Returns:
        合并后的 RAGConfig 对象
    """
    config_dir = config_dir or CONFIG_DIR
    
    # 1. 加载基础配置
    base_config = load_yaml(config_dir / base_config_name)
    
    # 2. 确定硬件配置
    if hardware is None or hardware == "auto":
        hardware = detect_hardware()
        logger.info(f"自动检测硬件: {hardware}")
    
    # 3. 加载硬件专用配置
    hw_config = {}
    if hardware in HARDWARE_PRESETS:
        preset_file = HARDWARE_PRESETS[hardware]
        if preset_file != "auto":
            hw_config = load_yaml(config_dir / preset_file)
            logger.info(f"加载硬件配置: {preset_file}")
    else:
        # 尝试直接加载文件
        hw_config = load_yaml(config_dir / hardware)
        logger.info(f"加载自定义配置: {hardware}")
    
    # 4. 深度合并
    merged = deep_merge(base_config, hw_config)
    
    # 5. 解析为对象
    cfg = parse_config(merged)
    
    # 6. 环境变量覆盖（最高优先级）
    _apply_env_overrides(cfg)
    
    return cfg


def _apply_env_overrides(cfg: RAGConfig):
    """应用环境变量覆盖"""
    env_map = {
        'RAG_DEVICE': 'device',
        'RAG_EMBEDDING_MODEL': 'embedding_model',
        'RAG_BATCH_SIZE': ('batch_size', int),
        'RAG_CHUNK_SIZE': ('chunk_size', int),
        'RAG_VECTORDB_PATH': 'vectordb_path',
        'RAG_CACHE_DIR': 'cache_dir',
        'RAG_NUM_WORKERS': ('num_workers', int),
        'RAG_USE_RERANKER': ('use_reranker', lambda x: x.lower() == 'true'),
    }
    
    for env_key, attr in env_map.items():
        value = os.environ.get(env_key)
        if value is not None:
            if isinstance(attr, tuple):
                attr_name, converter = attr
                setattr(cfg, attr_name, converter(value))
            else:
                setattr(cfg, attr, value)
            logger.info(f"环境变量覆盖: {env_key} -> {attr} = {value}")


def get_config_summary(cfg: RAGConfig) -> str:
    """获取配置摘要字符串"""
    lines = [
        "=" * 50,
        "RAG 配置摘要",
        "=" * 50,
        f"设备: {cfg.device} ({cfg.precision})",
        f"Embedding: {cfg.embedding_model}",
        f"  批次: {cfg.embedding_batch_size}, 最大长度: {cfg.embedding_max_length}",
        f"  设备: {cfg.embedding_device}, 半精度: {cfg.embedding_half_precision}",
        f"切分: chunk_size={cfg.chunk_size}, overlap={cfg.chunk_overlap}",
        f"向量库: {cfg.vectordb_path} ({cfg.collection_name})",
        f"检索: top_k={cfg.top_k}, threshold={cfg.score_threshold}",
        f"重排序: {'启用' if cfg.use_reranker else '禁用'} ({cfg.reranker_model})",
        f"处理: workers={cfg.num_workers}, batch={cfg.batch_size}",
        f"缓存: {cfg.cache_dir}",
        "=" * 50,
    ]
    return "\n".join(lines)


# 全局配置实例（懒加载）
_global_config: Optional[RAGConfig] = None


def get_config(hardware: Optional[str] = None) -> RAGConfig:
    """获取全局配置单例"""
    global _global_config
    if _global_config is None:
        _global_config = load_config(hardware)
    return _global_config


def reset_config(hardware: Optional[str] = None) -> RAGConfig:
    """重置全局配置"""
    global _global_config
    _global_config = load_config(hardware)
    return _global_config


if __name__ == "__main__":
    # 测试
    logging.basicConfig(level=logging.INFO)
    
    print("测试自动检测...")
    cfg = load_config("auto")
    print(get_config_summary(cfg))
    
    print("\n测试 R5 5600U 配置...")
    cfg_r5 = load_config("r5_5600u")
    print(get_config_summary(cfg_r5))
    
    print("\n测试 RTX 4060 配置...")
    cfg_4060 = load_config("rtx_4060")
    print(get_config_summary(cfg_4060))