"""
Admin handlers for managing stickers
"""
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from bot.stickers import StickerManager
from config.settings import settings
import logging

logger = logging.getLogger(__name__)

admin_router = Router()


def is_admin(user_id: int) -> bool:
    """Check if user is admin"""
    return user_id in settings.admin_ids_list


@admin_router.message(Command("upload_sticker"))
async def cmd_upload_sticker(message: Message):
    """Upload a sticker file (.tgs)"""
    if not is_admin(message.from_user.id):
        await message.answer("❌ ليس لديك صلاحية لهذا الأمر")
        return
    
    if not message.document:
        await message.answer(
            "📎 يرجى إرسال ملف .tgs\n\n"
            "الاستخدام:\n"
            "1. أرسل ملف .tgs\n"
            "2. أضف اسم الـ sticker في الرد\n\n"
            "الأسماء المتاحة:\n"
            f"{', '.join(StickerManager.STICKER_MAP.keys())}"
        )
        return
    
    # Wait for sticker name in reply
    await message.answer(
        "⏳ يرجى إرسال اسم الـ sticker في رسالة منفصلة\n\n"
        f"الأسماء المتاحة: {', '.join(StickerManager.STICKER_MAP.keys())}"
    )


@admin_router.message(Command("list_stickers"))
async def cmd_list_stickers(message: Message):
    """List all available stickers"""
    if not is_admin(message.from_user.id):
        return
    
    stickers = StickerManager.list_available_stickers()
    
    text = "📋 قائمة الـ Stickers:\n\n"
    for name, exists in stickers.items():
        status = "✅" if exists else "❌"
        text += f"{status} {name}\n"
    
    await message.answer(text)


@admin_router.message(F.document & F.document.file_name.endswith('.tgs'))
async def handle_sticker_upload(message: Message):
    """Handle sticker file upload"""
    if not is_admin(message.from_user.id):
        return
    
    # Get sticker name from caption or previous message
    sticker_name = message.caption
    
    if not sticker_name:
        await message.answer(
            "❌ يرجى إضافة اسم الـ sticker في الـ caption\n\n"
            f"الأسماء المتاحة: {', '.join(StickerManager.STICKER_MAP.keys())}"
        )
        return
    
    sticker_name = sticker_name.strip().lower()
    
    if sticker_name not in StickerManager.STICKER_MAP:
        await message.answer(
            f"❌ اسم غير صحيح: {sticker_name}\n\n"
            f"الأسماء المتاحة: {', '.join(StickerManager.STICKER_MAP.keys())}"
        )
        return
    
    try:
        # Download file
        file = await message.bot.get_file(message.document.file_id)
        file_path = f"stickers/{StickerManager.STICKER_MAP[sticker_name]}"
        
        await message.bot.download_file(file.file_path, file_path)
        
        await message.answer(f"✅ تم رفع الـ sticker بنجاح: {sticker_name}")
        logger.info(f"Admin {message.from_user.id} uploaded sticker: {sticker_name}")
    except Exception as e:
        logger.error(f"Error uploading sticker: {e}", exc_info=True)
        await message.answer(f"❌ خطأ في رفع الـ sticker: {e}")

