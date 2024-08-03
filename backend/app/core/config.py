from pydantic import BaseSettings, AnyHttpUrl, EmailStr, validator
from typing import List, Union

class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    SERVER_NAME: str
    SERVER_HOST: AnyHttpUrl
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []

    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    PROJECT_NAME: str
    POSTGRES_SERVER: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    SQLALCHEMY_DATABASE_URI: str = None

    @validator("SQLALCHEMY_DATABASE_URI", pre=True)
    def assemble_db_connection(cls, v: str, values: dict) -> str:
        if isinstance(v, str):
            return v
        return f"postgresql://{values.get('POSTGRES_USER')}:{values.get('POSTGRES_PASSWORD')}@{values.get('POSTGRES_SERVER')}/{values.get('POSTGRES_DB')}"

    SMTP_TLS: bool = True
    SMTP_PORT: int = None
    SMTP_HOST: str = None
    SMTP_USER: str = None
    SMTP_PASSWORD: str = None
    EMAILS_FROM_EMAIL: EmailStr = None
    EMAILS_FROM_NAME: str = None

    @validator("EMAILS_FROM_NAME")
    def get_project_name(cls, v: str, values: dict) -> str:
        if not v:
            return values["PROJECT_NAME"]
        return v

    EMAIL_RESET_TOKEN_EXPIRE_HOURS: int = 48
    EMAIL_TEMPLATES_DIR: str = "/app/app/email-templates/build"
    EMAILS_ENABLED: bool = False

    @validator("EMAILS_ENABLED", pre=True)
    def get_emails_enabled(cls, v: bool, values: dict) -> bool:
        return bool(
            values.get("SMTP_HOST")
            and values.get("SMTP_PORT")
            and values.get("EMAILS_FROM_EMAIL")
        )

    EMAIL_TEST_USER: EmailStr = "csa.balogh.0165@gmail.com"
    FIRST_SUPERUSER: EmailStr
    FIRST_SUPERUSER_PASSWORD: str
    USERS_OPEN_REGISTRATION: bool = False

    CLAUDE_API_URL: str
    CLAUDE_API_KEY: str
    GPT4_API_URL: str
    GPT4_API_KEY: str
    CODEX_API_URL: str
    OPENAI_API_KEY: str

    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379

    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings()