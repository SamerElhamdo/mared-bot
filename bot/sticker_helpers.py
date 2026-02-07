"""
Helper functions to send animated stickers (TGS) and emojis with messages
Supports TGS format (Telegram Sticker format based on Lottie)
"""
from aiogram import Bot
from aiogram.types import FSInputFile, MessageEntity
from pathlib import Path
from bot.stickers import StickerManager
import logging

logger = logging.getLogger(__name__)


async def send_sticker_if_available(bot: Bot, chat_id: int, sticker_name: str) -> bool:
    """
    Send animated sticker (TGS format) if available, otherwise return False
    
    TGS (Telegram Sticker) is the standard format for animated stickers in Telegram.
    It's a Gzipped JSON file based on Lottie library.
    
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
        
        # TGS files are supported directly by Telegram
        sticker_file = FSInputFile(sticker_path)
        await bot.send_sticker(chat_id=chat_id, sticker=sticker_file)
        return True
    except Exception as e:
        logger.error(f"Error sending sticker {sticker_name}: {e}")
        return False


async def send_dice_emoji(bot: Bot, chat_id: int, emoji: str = "🎲") -> bool:
    """
    Send animated dice/interactive emoji
    
    Supported emojis: 🎲 (dice), 🎯 (dart), 🏀 (basketball), 
                      ⚽ (football), 🎰 (slot machine), 🎳 (bowling)
    
    Args:
        bot: Bot instance
        chat_id: Chat ID to send dice to
        emoji: Emoji type (default: 🎲)
    
    Returns:
        True if sent successfully, False otherwise
    """
    try:
        await bot.send_dice(chat_id=chat_id, emoji=emoji)
        return True
    except Exception as e:
        logger.error(f"Error sending dice emoji {emoji}: {e}")
        return False


async def send_custom_emoji(bot: Bot, chat_id: int, text: str, 
                            emoji_id: str, offset: int, length: int) -> bool:
    """
    Send message with custom animated emoji (Premium feature)
    
    Note: Requires custom_emoji_id from Telegram's emoji set
    
    Args:
        bot: Bot instance
        chat_id: Chat ID to send message to
        text: Message text with placeholder for emoji
        emoji_id: Custom emoji ID from Telegram
        offset: Position of emoji in text
        length: Length of emoji placeholder
    
    Returns:
        True if sent successfully, False otherwise
    """
    try:
        await bot.send_message(
            chat_id=chat_id,
            text=text,
            entities=[
                MessageEntity(
                    type="custom_emoji",
                    offset=offset,
                    length=length,
                    custom_emoji_id=emoji_id
                )
            ]
        )
        return True
    except Exception as e:
        logger.error(f"Error sending custom emoji: {e}")
        return False


async def send_sticker_before_message(bot: Bot, chat_id: int, sticker_name: str, 
                                     message_text: str, reply_markup=None, parse_mode=None) -> bool:
    """
    Send sticker (TGS) before message if available
    
    Returns:
        True if sticker was sent, False otherwise
    """
    sticker_sent = await send_sticker_if_available(bot, chat_id, sticker_name)
    if sticker_sent:
        # Small delay to ensure sticker is shown first
        import asyncio
        await asyncio.sleep(0.3)
    return sticker_sent

