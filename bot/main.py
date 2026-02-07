import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from config.settings import settings
from bot.handlers import router
from bot.admin_handlers import admin_router
from bot.channel_manager import ChannelManager
from utils.logging import setup_logging
from database.base import init_db, get_session
from services.subscription_service import SubscriptionService
import signal
import sys

logger = setup_logging()


async def check_expired_subscriptions(bot: Bot, channel_manager: ChannelManager):
    """Periodically check and expire subscriptions"""
    while True:
        try:
            expired_count = SubscriptionService.check_and_expire_subscriptions()
            
            if expired_count > 0:
                logger.info(f"Expired {expired_count} subscriptions")
                
                # Remove expired users from channel
                # Get recently expired subscriptions (in the last hour)
                from datetime import datetime, timedelta
                from database.models import Subscription, SubscriptionStatus
                
                with get_session() as session:
                    one_hour_ago = datetime.utcnow() - timedelta(hours=1)
                    expired_subs = session.query(Subscription).filter(
                        Subscription.status == SubscriptionStatus.EXPIRED,
                        Subscription.updated_at >= one_hour_ago
                    ).all()
                    
                    for sub in expired_subs:
                        try:
                            await channel_manager.remove_user(sub.user.telegram_id)
                            # Send notification (optional)
                            try:
                                await bot.send_message(
                                    sub.user.telegram_id,
                                    "❌ تم إزالتك من القناة بسبب انتهاء الاشتراك."
                                )
                            except:
                                pass
                        except Exception as e:
                            logger.error(f"Error removing user {sub.user.telegram_id}: {e}")
            
            # Check every hour
            await asyncio.sleep(3600)
        except Exception as e:
            logger.error(f"Error in check_expired_subscriptions: {e}", exc_info=True)
            await asyncio.sleep(3600)


async def main():
    """Main function to run the bot"""
    logger.info("Starting bot...")
    
    # Initialize database
    try:
        init_db()
        logger.info("Database initialized")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}", exc_info=True)
        sys.exit(1)
    
    # Initialize bot and dispatcher
    bot = Bot(
        token=settings.BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    
    dp = Dispatcher()
    # Include admin router first (more specific handlers)
    dp.include_router(admin_router)
    # Include main router (general handlers)
    dp.include_router(router)
    
    # Initialize channel manager
    channel_manager = ChannelManager(bot)
    
    # Start background task for checking expired subscriptions
    asyncio.create_task(check_expired_subscriptions(bot, channel_manager))
    
    # Start polling
    logger.info("Bot started, waiting for messages...")
    try:
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(f"Error in polling: {e}", exc_info=True)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)

