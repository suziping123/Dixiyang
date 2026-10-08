"""
补全服务：小说编辑器 AI 续写。
无独立配置——直接复用 RAG 聊天同一套 DeepSeek（config.DEPREESEEK_*），
切换模型/本地部署见 docs/LLM接入配置切换.md。
"""
import asyncio
import logging

from ...config import DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL, DEEPSEEK_MODEL
from .base import CompletionContext, CompletionProvider, CompletionResult

log = logging.getLogger(__name__)

COMPLETION_TIMEOUT = 10.0  # 单次补全超时（秒）

_provider: CompletionProvider | None = None


class OpenAICompatibleProvider(CompletionProvider):
    """OpenAI 兼容补全（DeepSeek / 自部署均可，懒加载 openai SDK）"""

    def __init__(self, base_url: str, api_key: str, model: str, timeout: float):
        self._base_url = base_url
        self._api_key = api_key
        self._model = model
        self._timeout = timeout
        self._client = None

    @property
    def name(self) -> str:
        return "openai-compatible"

    def _get_client(self):
        if self._client is None:
            from openai import AsyncOpenAI
            self._client = AsyncOpenAI(
                base_url=self._base_url,
                api_key=self._api_key,
                timeout=self._timeout,
            )
        return self._client

    async def complete(self, ctx: CompletionContext) -> CompletionResult | None:
        import time
        if not self._api_key:
            # 未配置 key：静默降级（前端 data=null，不影响写作）
            log.warning("补全未配置 DEEPSEEK_API_KEY，跳过请求")
            return None
        start = time.monotonic()
        try:
            client = self._get_client()
            prompt = _build_completion_prompt(ctx)
            resp = await client.chat.completions.create(
                model=self._model,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "你是小说续写助手。只输出从光标处直接接续的下一句增量文本（20~80字），"
                            "严禁复述、重写或总结光标前已有的内容，"
                            "不要输出解释、引号、换行前缀或任何与正文无关的内容。"
                        ),
                    },
                    {"role": "user", "content": prompt},
                ],
                max_tokens=ctx.max_tokens,
                temperature=ctx.temperature,
            )
            text = (resp.choices[0].message.content or "").strip()
            if not text:
                return None
            # 防复述：截掉与光标前文尾部重叠的前缀（修"返回整段"）
            text = _strip_repetition(text, ctx.cursor_before)[: ctx.max_tokens * 2].strip()
            if not text:
                return None
            return CompletionResult(
                text=text[: ctx.max_tokens * 2],
                model=self._model,
                finish_reason=resp.choices[0].finish_reason or "stop",
                latency_ms=int((time.monotonic() - start) * 1000),
            )
        except Exception as e:
            # 不输出正文上下文，只记录错误类型
            log.warning("补全请求失败: %s: %s", type(e).__name__, e)
            return None


def _build_setting_context(ctx: CompletionContext) -> str:
    """按勾选 IDs 组装设定上下文（角色卡 + 事件 + 时间线），总截断 1500 字符。

    复用 chat_service.build_fixed_context 查角色（含背景/性格/外貌）与事件；
    时间线单独查表拼 [时间线] 条目。查询量小（各 ≤50 条），同步执行开销可忽略。
    """
    parts: list[str] = []
    try:
        if ctx.character_ids or ctx.story_node_ids:
            from ..chat_service import build_fixed_context
            fixed = build_fixed_context(ctx.character_ids, ctx.story_node_ids)
            if fixed:
                parts.append(fixed)
        if ctx.timeline_ids:
            from ...models.timeline import Timeline
            from ...utils.database import SessionLocal
            with SessionLocal() as db:
                rows = db.query(Timeline).filter(Timeline.id.in_(ctx.timeline_ids)).all()
            for t in rows:
                line = f"[时间线] {t.name}"
                if t.description:
                    line += f"：{t.description[:100]}"
                parts.append(line)
    except Exception as e:
        # 设定上下文组装失败不阻塞补全，只记错误类型
        log.warning("设定上下文组装失败: %s", type(e).__name__)
    return "\n".join(parts)[:1500]


def _strip_repetition(text: str, cursor_before: str) -> str:
    """防复述：返回文本若复述了光标前文尾部，截掉重叠前缀。

    找最长 k（≥6）使 cursor_before 以 text[:k] 结尾——命中即说明模型把
    已有内容当成了输出。截完为空（纯复述无增量）则返回空串=无补全。
    """
    if not text or not cursor_before:
        return text
    max_k = min(len(text), len(cursor_before), 120)
    for k in range(max_k, 5, -1):
        if cursor_before.endswith(text[:k]):
            return text[k:].lstrip()
    return text


def _build_completion_prompt(ctx: CompletionContext) -> str:
    """组装最小化上下文，控制 token 消耗"""
    parts = []
    if ctx.chapter_title:
        parts.append(f"章节标题：{ctx.chapter_title}")
    setting = _build_setting_context(ctx)
    if setting:
        parts.append(f"设定上下文：\n{setting}")
    if ctx.novel_context:
        parts.append(f"背景设定：{ctx.novel_context[:300]}")
    parts.append(f"光标前正文：\n{ctx.cursor_before}")
    if ctx.cursor_after.strip():
        parts.append(f"光标后正文：\n{ctx.cursor_after}")
    parts.append("请直接续写光标处的下一句（不超过80字），只输出接续的增量文字，严禁复述或重写光标前正文：")
    return "\n\n".join(parts)


def get_provider() -> CompletionProvider:
    """获取补全 Provider（单例，复用 DeepSeek 配置）"""
    global _provider
    if _provider is None:
        _provider = OpenAICompatibleProvider(
            DEEPSEEK_BASE_URL, DEEPSEEK_API_KEY, DEEPSEEK_MODEL, COMPLETION_TIMEOUT
        )
    return _provider


async def request_completion(ctx: CompletionContext) -> CompletionResult | None:
    """统一入口：带超时保护，失败返回 None（不影响编辑器）"""
    provider = get_provider()
    try:
        return await asyncio.wait_for(provider.complete(ctx), timeout=COMPLETION_TIMEOUT + 2)
    except asyncio.TimeoutError:
        log.warning("补全超时: provider=%s", provider.name)
        return None
    except Exception as e:
        log.warning("补全异常: %s: %s", type(e).__name__, e)
        return None
