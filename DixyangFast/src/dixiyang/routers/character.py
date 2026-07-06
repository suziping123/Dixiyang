import json
from fastapi import APIRouter, Depends

from ..schemas.character import CharacterCreate, CharacterUpdate
from ..services.character_service import CharacterService
from ..services.prompt_templates import build_character_extract_prompt
from ..services.chat_service import call_llm
from ..utils.response import Result

router = APIRouter(prefix="/novelCharacter", tags=["角色管理模块"])


@router.get("/list/{novel_id}")
async def list_paginated(novel_id: int, page: int = 1, page_size: int = 10, svc: CharacterService = Depends()):
    return svc.list_paginated(novel_id, page, page_size)


@router.get("/all/{novel_id}")
async def list_all(novel_id: int, svc: CharacterService = Depends()):
    return svc.list_all(novel_id)


@router.get("/{char_id}")
async def get_by_id(char_id: int, svc: CharacterService = Depends()):
    return svc.get_by_id(char_id)


@router.post("/create")
async def create(req: CharacterCreate, svc: CharacterService = Depends()):
    return svc.create(req)


@router.post("/update/{char_id}")
async def update(char_id: int, req: CharacterUpdate, svc: CharacterService = Depends()):
    return svc.update(char_id, req)


@router.post("/delete/{char_id}")
async def delete(char_id: int, svc: CharacterService = Depends()):
    return svc.delete(char_id)


@router.post("/extractSettings")
async def extract_settings(body: dict):
    """
    从对话内容中提取角色设定
    输入: { "conversation": "对话文本" }
    返回: { "settings": { ... } }
    """
    conversation = body.get("conversation", "")
    if not conversation.strip():
        return Result.error("对话内容不能为空")

    prompt = build_character_extract_prompt(conversation)
    try:
        result = call_llm(
            [{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=1024,
        )
        # 清理结果
        result = result.strip()
        if result.startswith("```"):
            result = result.split("\n", 1)[-1].rsplit("```", 1)[0].strip()
        settings = json.loads(result)
        return Result.success("提取成功", {"settings": settings})
    except json.JSONDecodeError:
        return Result.error("AI 返回的不是有效 JSON")
    except Exception as e:
        return Result.error(f"提取失败: {e}")


@router.post("/saveSettings")
async def save_settings(body: dict, svc: CharacterService = Depends()):
    """
    保存角色设定到 extra 字段
    输入: { "characterId": 123, "settings": { ... } }
    """
    char_id = body.get("characterId")
    settings = body.get("settings")
    if not char_id or settings is None:
        return Result.error("参数不完整")
    return svc.save_settings(char_id, settings)
