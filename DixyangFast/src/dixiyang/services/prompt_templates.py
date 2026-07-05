"""
所有 Prompt 模板的统一管理
对齐 Spring 版 PromptTemplates.java
"""

from .conversation_mode import ConversationMode, MODE_META

# ==================== System Prompt ====================

_BASE_RULES = """你是小说创作助手。严格遵循以下规则：
1. 角色信息必须与【固定设定】中的角色卡完全一致
2. 故事事件必须与【固定设定】中的故事节点一致
3. 设定中没有的信息不能凭空编造，必须明确说"设定中没有这个信息"
4. 如果用户要求写与设定矛盾的内容，拒绝并说明原因"""


def build_system_prompt(mode: ConversationMode, custom_instruction: str | None = None) -> str:
    meta = MODE_META[mode]
    parts = [
        _BASE_RULES,
        "",
        f"【对话模式：{meta['label']}】",
        meta["instruction"],
    ]
    if custom_instruction:
        parts.append("")
        parts.append("【用户自定义指令】")
        parts.append(custom_instruction)
    return "\n".join(parts)


# ==================== User Prompt ====================

def build_user_prompt(
    fixed_context: str,
    history: str,
    edits: str,
    user_message: str,
) -> str:
    parts: list[str] = []
    if fixed_context:
        parts.append(f"【固定设定·不可违背】\n{fixed_context}\n")
    if history:
        parts.append(f"【对话历史】\n{history}\n")
    if edits:
        parts.append(f"{edits}\n")
    parts.append(f"【用户本轮输入】\n{user_message}")
    return "\n".join(parts)


# ==================== 修正要点提取 ====================

_KEYPOINT_TEMPLATE = """你是修正要点提取器。对比以下 AI 原始输出和用户修正后的内容，提取修正要点。

AI 原始输出：{original}

用户修正后：{edited}

请返回 JSON（不要 markdown 包裹）：
{{"keyPoint":"一句话总结修正要点（30字以内）","errorType":"错误类型"}}

错误类型只能是以下之一：
- FACT_ERROR（事实/数据错误）
- SETTING_VIOLATION（违背设定）
- TONE_WRONG（语气/风格不对）
- TOO_LONG（太啰嗦）
- OFF_TOPIC（答非所问）
- OTHER（其他）

只返回 JSON，不要任何解释。"""


def build_keypoint_prompt(original: str, edited: str) -> str:
    return _KEYPOINT_TEMPLATE.format(
        original=original[:500],
        edited=edited[:500],
    )


# ==================== 标题生成 ====================

_TITLE_TEMPLATE = """你是一个对话标题生成器。请用 3-8 个字概括以下对话的主题，直接返回标题，不要任何解释、标点或引号。

对话：
{conversation}"""


def build_title_prompt(conversation: str) -> str:
    return _TITLE_TEMPLATE.format(conversation=conversation)


# ==================== 历史摘要 ====================

_SUMMARIZE_TEMPLATE = """请用 3-5 句话概括以下对话的核心内容（设定讨论、创作内容、关键决定）。直接返回摘要，不要解释。

{previous_summary}

新对话内容：
{conversation}"""


def build_summarize_prompt(previous_summary: str, conversation: str) -> str:
    prev = f"已有摘要：\n{previous_summary}" if previous_summary else ""
    return _SUMMARIZE_TEMPLATE.format(
        previous_summary=prev,
        conversation=conversation,
    )
