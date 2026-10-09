"""点子库与创意社区路由 /api/idea/*"""
from fastapi import APIRouter, Depends, Query

from ..schemas.idea import CommentCreate, DraftCreate, DraftUpdate, ImportRequest, PostUpdate, PublishRequest
from ..services.idea_service import IdeaService
from ..utils.auth_deps import get_current_user_id, get_optional_user_id

router = APIRouter(prefix="/idea", tags=["点子库与创意社区"])


# ---------- 草稿 ----------

@router.get("/drafts")
async def list_drafts(
    category: str | None = None, q: str | None = None,
    page: int = 1, page_size: int = Query(10, alias="pageSize"),
    user_id: int = Depends(get_current_user_id), svc: IdeaService = Depends(),
):
    return svc.list_drafts(user_id, category, q, page, page_size)


@router.post("/drafts")
async def create_draft(req: DraftCreate, user_id: int = Depends(get_current_user_id), svc: IdeaService = Depends()):
    return svc.create_draft(user_id, req)


@router.get("/drafts/{draft_id}")
async def get_draft(draft_id: int, user_id: int = Depends(get_current_user_id), svc: IdeaService = Depends()):
    return svc.get_draft(user_id, draft_id)


@router.put("/drafts/{draft_id}")
async def update_draft(draft_id: int, req: DraftUpdate, user_id: int = Depends(get_current_user_id), svc: IdeaService = Depends()):
    return svc.update_draft(user_id, draft_id, req)


@router.delete("/drafts/{draft_id}")
async def delete_draft(draft_id: int, user_id: int = Depends(get_current_user_id), svc: IdeaService = Depends()):
    return svc.delete_draft(user_id, draft_id)


@router.post("/drafts/{draft_id}/publish")
async def publish(draft_id: int, req: PublishRequest, user_id: int = Depends(get_current_user_id), svc: IdeaService = Depends()):
    return svc.publish(user_id, draft_id, req)


# ---------- 帖子 ----------

@router.get("/posts")
async def list_posts(
    category: str | None = None, sort: str = "new", q: str | None = None,
    tags: str | None = None,
    page: int = 1, page_size: int = Query(10, alias="pageSize"),
    user_id: int | None = Depends(get_optional_user_id),
    svc: IdeaService = Depends(),
):
    return svc.list_posts(user_id, category, sort, q, tags.split(",") if tags else None, page, page_size)


@router.get("/posts/{post_id}")
async def get_post(post_id: int, svc: IdeaService = Depends(), user_id: int | None = Depends(get_optional_user_id)):
    return svc.get_post(post_id, user_id)


@router.get("/posts/{post_id}/attachment")
async def get_attachment(post_id: int, svc: IdeaService = Depends(), user_id: int | None = Depends(get_optional_user_id)):
    return svc.get_attachment(post_id, user_id)


@router.put("/posts/{post_id}")
async def update_post(post_id: int, req: PostUpdate, user_id: int = Depends(get_current_user_id), svc: IdeaService = Depends()):
    return svc.update_post(user_id, post_id, req)


@router.post("/posts/{post_id}/remove")
async def remove_post(post_id: int, user_id: int = Depends(get_current_user_id), svc: IdeaService = Depends()):
    return svc.remove_post(user_id, post_id)


@router.post("/posts/{post_id}/restore")
async def restore_post(post_id: int, user_id: int = Depends(get_current_user_id), svc: IdeaService = Depends()):
    return svc.restore_post(user_id, post_id)


@router.post("/posts/{post_id}/import")
async def import_post(post_id: int, req: ImportRequest, user_id: int = Depends(get_current_user_id), svc: IdeaService = Depends()):
    return svc.import_attachment(user_id, post_id, req)


@router.get("/mine/posts")
async def mine_posts(page: int = 1, page_size: int = Query(10, alias="pageSize"),
                     user_id: int = Depends(get_current_user_id), svc: IdeaService = Depends()):
    return svc.list_mine_posts(user_id, page, page_size)


# ---------- 互动 ----------

@router.post("/posts/{post_id}/like")
async def toggle_like(post_id: int, user_id: int = Depends(get_current_user_id), svc: IdeaService = Depends()):
    return svc.toggle_like(user_id, post_id)


@router.post("/posts/{post_id}/collect")
async def toggle_collect(post_id: int, user_id: int = Depends(get_current_user_id), svc: IdeaService = Depends()):
    return svc.toggle_collect(user_id, post_id)


@router.get("/mine/collects")
async def mine_collects(page: int = 1, page_size: int = Query(10, alias="pageSize"),
                        user_id: int = Depends(get_current_user_id), svc: IdeaService = Depends()):
    return svc.list_mine_collects(user_id, page, page_size)


@router.get("/mine/likes")
async def mine_likes(page: int = 1, page_size: int = Query(10, alias="pageSize"),
                     user_id: int = Depends(get_current_user_id), svc: IdeaService = Depends()):
    return svc.list_mine_likes(user_id, page, page_size)


# ---------- 评论 ----------

@router.get("/posts/{post_id}/comments")
async def list_comments(post_id: int, page: int = 1, page_size: int = Query(10, alias="pageSize"),
                        svc: IdeaService = Depends(), user_id: int | None = Depends(get_optional_user_id)):
    return svc.list_comments(post_id, user_id, page, page_size)


@router.post("/posts/{post_id}/comments")
async def add_comment(post_id: int, req: CommentCreate, user_id: int = Depends(get_current_user_id), svc: IdeaService = Depends()):
    return svc.add_comment(user_id, post_id, req)


@router.delete("/comments/{comment_id}")
async def delete_comment(comment_id: int, user_id: int = Depends(get_current_user_id), svc: IdeaService = Depends()):
    return svc.delete_comment(user_id, comment_id)


# ---------- 标签 ----------

@router.get("/tags")
async def list_tags(top: int = 30, svc: IdeaService = Depends()):
    return svc.list_tags(top)
