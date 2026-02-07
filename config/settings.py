from pydantic_settings import BaseSettings
from pydantic import ConfigDict
from typing import List


class Settings(BaseSettings):
    # Telegram Bot Configuration
    BOT_TOKEN: str
    CHANNEL_ID: str
    
    # Database Configuration
    DATABASE_URL: str
    
    # Crypto Payment Configuration
    CRYPTO_PROVIDER: str = "manual"
    CRYPTO_WALLET_ADDRESS: str = ""
    # USDT Wallet Addresses for different networks
    USDT_TRC20_ADDRESS: str = ""
    USDT_BSC_ADDRESS: str = ""
    
    # Bot Configuration
    ADMIN_USER_IDS: str = ""
    FREE_TRIAL_DAYS: int = 7
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    @property
    def admin_ids_list(self) -> List[int]:
        """Parse admin user IDs from comma-separated string"""
        if not self.ADMIN_USER_IDS:
            return []
        return [int(uid.strip()) for uid in self.ADMIN_USER_IDS.split(",") if uid.strip()]
    
    model_config = ConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore"  # Ignore extra environment variables (e.g., from Dokploy)
    )


settings = Settings()

