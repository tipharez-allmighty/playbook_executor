from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Environmental vatiables
    HOSTS: str = "/etc/playbook/hosts"
    TIMEOUT: int = 10
    MAX_CONCURRENT_TASKS: int = 10
    SSH_KNOWN_HOSTS_FILE: str = ""

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
