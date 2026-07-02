from langchain_openai import ChatOpenAI
from app.chat.utils import settings

_model_instance = None

def load_model() -> ChatOpenAI:
    global _model_instance
    if _model_instance is None:
        _model_instance = ChatOpenAI(
            api_key=settings.DS_API_KEY,
            base_url=settings.BASE_URL,
            model=settings.MODEL_NAME
        )
    return _model_instance