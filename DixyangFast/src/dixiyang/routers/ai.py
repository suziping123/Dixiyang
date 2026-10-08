from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from ..config import DEEPSEEK_API_KEY
from ..services.completion import get_provider, request_completion
from ..services.completion.base import CompletionContext
from ..utils.auth_deps import get_current_user_id
from ..utils.response import Result

router = APIRouter(prefix="/ai", tags=["AI 补全"])


class CompletionReq(BaseModel):
    chapterId: int = 0
    chapterTitle: str = ""
    cursorBefore: str = Field(default="", description="光标前正文（截断后）")
    cursorAfter: str = Field(default="", description="光标后正文（截断后）")
    novelContext: str = ""
    novelId: int = Field(default=0, description="小说 ID（设定上下文组装用）")
    characterIds: list[int] = Field(default_factory=list, description="勾选的角色 ID")
    storyNodeIds: list[int] = Field(default_factory=list, description="勾选的事件（故事节点）ID")
    timelineIds: list[int] = Field(default_factory=list, description="勾选的时间线 ID")
    maxTokens: int = 80

    class Config:
        populate_by_name = True


@router.get("/status")
async def ai_status(user_id: int = Depends(get_current_user_id)):
    """AI 补全可用状态（前端显示 AI 就绪/未连接）：无 key 时如实报未连接"""
    provider = get_provider()
    return Result.success("获取成功", {
        "connected": bool(DEEPSEEK_API_KEY),
        "provider": provider.name,
    })


@router.post("/completion")
async def completion(req: CompletionReq, user_id: int = Depends(get_current_user_id)):
    """
    请求 AI 补全。
    - 只返回短补全文本，绝不修改正文
    - 失败返回 data=null，不影响编辑器继续写作
    - 上下文由前端截断（光标前 2000 字 / 光标后 200 字）
    """
    ctx = CompletionContext(
        chapter_id=req.chapterId,
        chapter_title=req.chapterTitle,
        cursor_before=req.cursorBefore[-2000:],
        cursor_after=req.cursorAfter[:200],
        novel_context=req.novelContext[:300],
        novel_id=req.novelId,
        character_ids=req.characterIds[:50],
        story_node_ids=req.storyNodeIds[:50],
        timeline_ids=req.timelineIds[:50],
        max_tokens=max(20, min(req.maxTokens, 80)),
    )
    result = await request_completion(ctx)
    if result is None:
        return Result.success("补全不可用", None)
    return Result.success("补全成功", {
        "text": result.text,
        "model": result.model,
        "requestId": result.request_id,
        "latency": result.latency_ms,
        "finishReason": result.finish_reason,
    })
