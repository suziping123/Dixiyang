from typing import Any, Optional


class GetJSONResponse:
    @staticmethod
    def success(msg: str = "success", data: Any = None) -> dict:
        return {"code": 200, "msg": msg, "data": data}

    @staticmethod
    def error(msg: str = "error", data: Any = None) -> dict:
        return {"code": 500, "msg": msg, "data": data}

    @staticmethod
    def unauthorized(msg: str = "未授权") -> dict:
        return {"code": 401, "msg": msg, "data": None}

    @staticmethod
    def not_found(msg: str = "资源不存在") -> dict:
        return {"code": 404, "msg": msg, "data": None}

    @staticmethod
    def bad_request(msg: str = "请求参数错误") -> dict:
        return {"code": 400, "msg": msg, "data": None}