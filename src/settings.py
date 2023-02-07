from pydantic import AnyHttpUrl, BaseSettings, RedisDsn


class Settings(BaseSettings):
    internal_ssl_verify: bool = False
    internal_api_base_url: AnyHttpUrl = "http://localhost:5284"  # type: ignore

    redis_connection_url: RedisDsn = "redis://localhost:6379/0"  # type: ignore
    redis_time_series_duplicate_policy: str = "last"
    redis_time_series_retention_seconds: int = 14400000

    service_log_level: str = "info"
    service_stream_lifetime_seconds: int = 86800

    class Config:
        env_prefix = "raccoon_"


settings = Settings()
