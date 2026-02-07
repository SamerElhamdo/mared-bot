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
    
    async def add_user(self, user_id: int, use_invite_link: bool = None) -> bool:
        """
        Add user to channel
        
        Args:
            user_id: Telegram user ID
            use_invite_link: Whether to use invite link (None = use settings, True/False = override)
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Determine method to use
            if use_invite_link is None:
                use_invite_link = getattr(settings, 'USE_INVITE_LINKS', True)
            
            # First, unban if banned
            try:
                await self.bot.unban_chat_member(
                    chat_id=self.channel_id,
                    user_id=user_id,
                    only_if_banned=True
                )
            except:
                pass  # User might not be banned
            
            if use_invite_link:
                # Method 1: Use invite link (works best for private channels)
                try:
                    # Create a one-time invite link for this specific user
                    invite_link = await self.bot.create_chat_invite_link(
                        chat_id=self.channel_id,
                        name=f"User_{user_id}",
                        member_limit=1,
                        creates_join_request=False  # Direct join, no approval needed
                    )
                    
                    # Send the invite link to the user
                    await self.bot.send_message(
                        chat_id=user_id,
                        text=f"🔗 رابط الدعوة للقناة:\n{invite_link.invite_link}\n\nاضغط على الرابط للانضمام."
                    )
                    
                    logger.info(f"Sent invite link to user {user_id} for channel {self.channel_id}")
                    return True
                except Exception as e:
                    logger.warning(f"Failed to create invite link for user {user_id}: {e}, trying unban method")
                    # Fall through to unban method
            
            # Method 2: Use unban (for public channels or if invite link fails)
            try:
                await self.bot.unban_chat_member(
                    chat_id=self.channel_id,
                    user_id=user_id,
                    only_if_banned=False
                )
                logger.info(f"Added user {user_id} to channel {self.channel_id} via unban")
                return True
            except Exception as e2:
                logger.error(f"Failed to add user {user_id} via unban: {e2}")
                return False
                
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

