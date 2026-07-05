from enum import Enum


class ConversationMode(str, Enum):
    """对话模式 - 用户每轮对话前明确指定"""

    WRITE = "WRITE"
    DISCUSS = "DISCUSS"
    ANALYZE = "ANALYZE"
    BRAINSTORM = "BRAINSTORM"
    ASK = "ASK"


MODE_META: dict[ConversationMode, dict] = {
    ConversationMode.WRITE: {
        "label": "创作",
        "icon": "Edit",
        "max_tokens": 8192,
        "show_thinking": False,
        "instruction": "按设定创作剧情、对话、描写、续写。严格基于固定设定，不自由发挥。",
    },
    ConversationMode.DISCUSS: {
        "label": "讨论",
        "icon": "ChatDotRound",
        "max_tokens": 2048,
        "show_thinking": False,
        "instruction": "只回答关于角色、世界观、大纲的设定问题。不要创作内容。如果用户要求创作，提醒他切换到创作模式。",
    },
    ConversationMode.ANALYZE: {
        "label": "分析",
        "icon": "Search",
        "max_tokens": 4096,
        "show_thinking": True,
        "instruction": "分析角色性格、剧情逻辑、世界观一致性。给出有依据的分析。请输出 <thinking> 分析过程，再给结论。",
    },
    ConversationMode.BRAINSTORM: {
        "label": "头脑风暴",
        "icon": "MagicStick",
        "max_tokens": 4096,
        "show_thinking": True,
        "instruction": "帮用户发散思考、寻找创作灵感。可以提出多种可能性。请输出 <thinking> 思考过程，再给建议。",
    },
    ConversationMode.ASK: {
        "label": "提问",
        "icon": "Help",
        "max_tokens": 1024,
        "show_thinking": False,
        "instruction": "快速精准回答用户问题，简短不啰嗦。",
    },
}


def get_mode(value: str | None) -> ConversationMode:
    """安全解析模式字符串，无效值回退 WRITE"""
    if not value:
        return ConversationMode.WRITE
    try:
        return ConversationMode(value.upper())
    except ValueError:
        return ConversationMode.WRITE
