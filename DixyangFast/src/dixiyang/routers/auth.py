from fastapi import APIRouter, Depends

from ..schemas.auth import AuthDTO, RegisterDTO, LoginByCodeDTO, SendCodeDTO
from ..services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["身份认证模块"])


@router.post("/login")
async def login(req: AuthDTO, svc: AuthService = Depends()):
    return svc.login(req)


@router.post("/register")
async def register(req: RegisterDTO, svc: AuthService = Depends()):
    return svc.register(req)


@router.post("/send-code")
async def send_code(req: SendCodeDTO, svc: AuthService = Depends()):
    return svc.send_code(req)


@router.post("/login-by-code")
async def login_by_code(req: LoginByCodeDTO, svc: AuthService = Depends()):
    return svc.login_by_code(req)
