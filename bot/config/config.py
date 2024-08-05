from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_ignore_empty=True)

    API_ID: int
    API_HASH: str

    SLEEP_BY_MIN_ENERGY: int = 200

    ADD_TAPS_ON_TURBO: int = 2500

    AUTO_UPGRADE: bool = True
    BALANCE_TO_SAVE: int = 10000
    MAX_LEVEL: int = 20
    MIN_SIGNIFICANCE: float = 0.1
    MULTIPLIER_FOR_CARDS_WITH_EXPIRE: float = 1
    PRIORITIZED_FIRST_LEVEL: bool = False

    APPLY_DAILY_ENERGY: bool = True
    APPLY_DAILY_TURBO: bool = True

    USE_PROXY_FROM_FILE: bool = False

    AUTO_CLAIM_DAILY_CIPHER: bool = False
    AUTO_FINISH_MINI_GAME: bool = False
    AUTO_BUY_COMBO: bool = False
    AUTO_FINISH_BIKE_GAME: bool = False
    BUY_ALL_SKINS: bool = False

settings = Settings()
