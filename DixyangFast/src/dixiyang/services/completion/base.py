"""
AI 补全 Provider 抽象层
编辑器能力层 ← CompletionService ← Provider 实现
编辑器不感知具体模型，模型配置只在后端。
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
import uuid


@dataclass
class CompletionContext:
    """补全请求上下文（只含必要上下文，控制 token 消耗）"""
    chapter_id: int
    chapter_title: str
    cursor_before: str  # 光标前最近一段正文
    cursor_after: str   # 光标后少量正文
    novel_context: str = ""  # 可选：角色/世界观摘要（自由文本，兼容旧调用）
    novel_id: int = 0  # 小说 ID（设定上下文组装）
    character_ids: list[int] = field(default_factory=list)  # 勾选的角色
    story_node_ids: list[int] = field(default_factory=list)  # 勾选的事件（故事节点）
    timeline_ids: list[int] = field(default_factory=list)  # 勾选的时间线
    max_tokens: int = 80    # 严格限制补全长度（20~80 汉字）
    temperature: float = 0.7


@dataclass
class CompletionResult:
    """补全结果"""
    text: str
    model: str
    request_id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    latency_ms: int = 0
    finish_reason: str = "stop"


class CompletionProvider(ABC):
    """补全提供者统一接口"""

    @property
    @abstractmethod
    def name(self) -> str: ...

    @abstractmethod
    async def complete(self, ctx: CompletionContext) -> CompletionResult | None:
        """
        请求补全。返回 None 表示不可用（前端显示 AI 未连接）。
        实现方负责超时控制，建议 5~10s。
        """
        raise NotImplementedError
