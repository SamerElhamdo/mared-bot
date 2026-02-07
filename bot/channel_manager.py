from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest
from config.settings import settings
import logging

logger = logging.getLogger(__name__)


class ChannelManager:
    """Manage channel membership"""
    
    def __init__(self, bot: Bot):
        self.bot = bot
        self.channel_id = settings.CHANNEL_ID
    
    async def add_user(self, user_id: int) -> bool:
        """Add user to channel"""
        try:
            # First, unban if banned
            try:
                await self.bot.unban_chat_member(
                    chat_id=self.channel_id,
                    user_id=user_id,
                    only_if_banned=True
                )
            except:
                pass  # User might not be banned
            
            # Then, invite user (for private channels) or unban (for public channels)
            # For public channels, unban is enough
            # For private channels, we need to use invite link or unban
            await self.bot.unban_chat_member(
                chat_id=self.channel_id,
                user_id=user_id,
                only_if_banned=False
            )
            logger.info(f"Added user {user_id} to channel {self.channel_id}")
            return True
        except TelegramBadRequest as e:
            logger.error(f"Failed to add user {user_id} to channel: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error adding user {user_id} to channel: {e}")
            return False
    
    async def remove_user(self, user_id: int) -> bool:
        """Remove user from channel"""
        try:
            await self.bot.ban_chat_member(
                chat_id=self.channel_id,
                user_id=user_id
            )
            logger.info(f"Removed user {user_id} from channel {self.channel_id}")
            return True
        except TelegramBadRequest as e:
            logger.error(f"Failed to remove user {user_id} from channel: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error removing user {user_id} from channel: {e}")
            return False
    
    async def check_user_membership(self, user_id: int) -> bool:
        """Check if user is member of channel"""
        try:
            member = await self.bot.get_chat_member(
                chat_id=self.channel_id,
                user_id=user_id
            )
            return member.status in ["member", "administrator", "creator"]
        except Exception as e:
            logger.error(f"Error checking membership for user {user_id}: {e}")
            return False

