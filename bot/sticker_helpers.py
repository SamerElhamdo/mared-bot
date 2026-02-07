"""
Helper functions to send animated stickers with messages
"""
from aiogram import Bot
from aiogram.types import FSInputFile, InputSticker
from pathlib import Path
from bot.stickers import StickerManager
import logging

logger = logging.getLogger(__name__)


async def send_sticker_if_available(bot: Bot, chat_id: int, sticker_name: str) -> bool:
    """
    Send animated sticker if available, otherwise return False
    
    Args:
        bot: Bot instance
        chat_id: Chat ID to send sticker to
        sticker_name: Name of sticker from StickerManager.STICKER_MAP
    
    Returns:
        True if sticker was sent, False otherwise
    """
    try:
        sticker_path = StickerManager.get_sticker_path(sticker_name)
        if not sticker_path:
            return False
        
        sticker_file = FSInputFile(sticker_path)
        await bot.send_sticker(chat_id=chat_id, sticker=sticker_file)
        return True
    except Exception as e:
        logger.error(f"Error sending sticker {sticker_name}: {e}")
        return False


async def send_sticker_before_message(bot: Bot, chat_id: int, sticker_name: str, 
                                     message_text: str, reply_markup=None, parse_mode=None) -> bool:
    """
    Send sticker before message if available
    
    Returns:
        True if sticker was sent, False otherwise
    """
    sticker_sent = await send_sticker_if_available(bot, chat_id, sticker_name)
    if sticker_sent:
        # Small delay to ensure sticker is shown first
        import asyncio
        await asyncio.sleep(0.3)
    return sticker_sent

