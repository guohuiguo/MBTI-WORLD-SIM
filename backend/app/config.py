from pydantic import BaseModel


class Settings(BaseModel):
    app_name: str = "MBTI World Simulator Backend"
    debug: bool = True

    # Phase 2 起可开
    use_llm: bool = True

    # 官方建议生产使用稳定模型名；先用 2.5 Flash 最稳
    gemini_model: str = "gemini-2.5-flash"

    # 兜底超时
    gemini_timeout_seconds: int = 20

    random_seed: int = 42


settings = Settings()