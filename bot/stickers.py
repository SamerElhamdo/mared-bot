"""
Sticker management for animated emojis (.tgs files)
"""
import os
from typing import Optional, Dict
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

# Directory to store sticker files
STICKERS_DIR = Path("stickers")
STICKERS_DIR.mkdir(exist_ok=True)


class StickerManager:
    """Manage animated emoji stickers"""
    
    # Default sticker file names (you'll upload .tgs files with these names)
    STICKER_MAP = {
        # Menu icons
        "plans": "plans.tgs",
        "subscribe": "subscribe.tgs",
        "subscriptions": "subscriptions.tgs",
        "referral": "referral.tgs",
        "info": "info.tgs",
        "back": "back.tgs",
        
        # Payment icons
        "payment": "payment.tgs",
        "trial": "trial.tgs",
        "confirm": "confirm.tgs",
        
        # Status icons
        "success": "success.tgs",
        "error": "error.tgs",
        "warning": "warning.tgs",
        
        # Network icons
        "trc20": "trc20.tgs",
        "bsc": "bsc.tgs",
    }
    
    @staticmethod
    def get_sticker_path(sticker_name: str) -> Optional[Path]:
        """Get path to sticker file"""
        filename = StickerManager.STICKER_MAP.get(sticker_name)
        if not filename:
            return None
        
        path = STICKERS_DIR / filename
        if path.exists():
            return path
        return None
    
    @staticmethod
    def list_available_stickers() -> Dict[str, bool]:
        """List all available stickers and their status"""
        result = {}
        for name, filename in StickerManager.STICKER_MAP.items():
            path = STICKERS_DIR / filename
            result[name] = path.exists()
        return result
    
    @staticmethod
    def add_sticker(sticker_name: str, file_path: str) -> bool:
        """Add or update a sticker file"""
        try:
            if sticker_name not in StickerManager.STICKER_MAP:
                logger.warning(f"Unknown sticker name: {sticker_name}")
                return False
            
            # Copy file to stickers directory
            import shutil
            dest_path = STICKERS_DIR / StickerManager.STICKER_MAP[sticker_name]
            shutil.copy2(file_path, dest_path)
            logger.info(f"Added sticker {sticker_name} -> {dest_path}")
            return True
        except Exception as e:
            logger.error(f"Error adding sticker {sticker_name}: {e}")
            return False

