from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, CommandStart
from aiogram.exceptions import TelegramBadRequest
from database.models import Plan, SubscriptionStatus
from database.base import get_session
from services.user_service import UserService
from services.subscription_service import SubscriptionService
from services.payment_service import PaymentService
from services.referral_service import ReferralService
from bot.keyboards import (
    get_main_menu_keyboard,
    get_plans_keyboard,
    get_plan_details_keyboard,
    get_payment_keyboard,
    get_referral_keyboard,
    get_subscriptions_keyboard,
    get_info_keyboard,
)
from bot.texts import Texts
from bot.channel_manager import ChannelManager
from config.settings import settings
import logging

logger = logging.getLogger(__name__)

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message):
    """Handle /start command"""
    try:
        # Get or create user
        user = UserService.get_or_create_user(
            telegram_id=message.from_user.id,
            username=message.from_user.username,
            first_name=message.from_user.first_name,
            last_name=message.from_user.last_name,
            language_code=message.from_user.language_code or "ar"
        )
        
        # Check for referral code
        if len(message.text.split()) > 1:
            referral_code = message.text.split()[1]
            referrer = UserService.get_user_by_referral_code(referral_code)
            if referrer and referrer.id != user.id:
                ReferralService.process_referral(referrer.id, user.id)
                logger.info(f"Processed referral: {referrer.id} -> {user.id}")
        
        # Send welcome message (only new message for welcome)
        await message.answer(
            Texts.WELCOME,
            reply_markup=get_main_menu_keyboard()
        )
    except Exception as e:
        logger.error(f"Error in cmd_start: {e}", exc_info=True)
        await message.answer(Texts.ERROR_OCCURRED)


@router.message(Command("menu"))
async def cmd_menu(message: Message):
    """Handle /menu command"""
    try:
        await message.answer(
            Texts.MAIN_MENU,
            reply_markup=get_main_menu_keyboard()
        )
    except Exception as e:
        logger.error(f"Error in cmd_menu: {e}", exc_info=True)
        await message.answer(Texts.ERROR_OCCURRED)


@router.callback_query(F.data == "menu")
async def callback_menu(callback: CallbackQuery):
    """Handle menu callback"""
    try:
        await callback.message.edit_text(
            Texts.MAIN_MENU,
            reply_markup=get_main_menu_keyboard()
        )
        await callback.answer()
    except TelegramBadRequest:
        await callback.answer()
    except Exception as e:
        logger.error(f"Error in callback_menu: {e}", exc_info=True)
        await callback.answer(Texts.ERROR_OCCURRED, show_alert=True)


@router.callback_query(F.data == "plans")
async def callback_plans(callback: CallbackQuery):
    """Handle plans callback"""
    try:
        with get_session() as session:
            plans = session.query(Plan).filter(Plan.is_active == True).all()
        
        if not plans:
            await callback.message.edit_text(
                "⚠️ لا توجد خطط متاحة حالياً",
                reply_markup=get_main_menu_keyboard()
            )
            await callback.answer()
            return
        
        await callback.message.edit_text(
            Texts.PLANS_TITLE,
            reply_markup=get_plans_keyboard(plans)
        )
        await callback.answer()
    except TelegramBadRequest:
        await callback.answer()
    except Exception as e:
        logger.error(f"Error in callback_plans: {e}", exc_info=True)
        await callback.answer(Texts.ERROR_OCCURRED, show_alert=True)


@router.callback_query(F.data.startswith("plan_"))
async def callback_plan_details(callback: CallbackQuery):
    """Handle plan details callback"""
    try:
        plan_id = int(callback.data.split("_")[1])
        
        with get_session() as session:
            plan = session.query(Plan).filter(Plan.id == plan_id).first()
        
        if not plan:
            await callback.answer("الخطة غير موجودة", show_alert=True)
            return
        
        can_use_trial = UserService.can_use_free_trial(callback.from_user.id)
        
        await callback.message.edit_text(
            Texts.format_plan_details(plan),
            reply_markup=get_plan_details_keyboard(plan_id, can_use_trial)
        )
        await callback.answer()
    except TelegramBadRequest:
        await callback.answer()
    except Exception as e:
        logger.error(f"Error in callback_plan_details: {e}", exc_info=True)
        await callback.answer(Texts.ERROR_OCCURRED, show_alert=True)


@router.callback_query(F.data.startswith("trial_"))
async def callback_trial(callback: CallbackQuery):
    """Handle trial activation callback"""
    try:
        plan_id = int(callback.data.split("_")[1])
        
        # Check if user can use trial
        if not UserService.can_use_free_trial(callback.from_user.id):
            await callback.answer(Texts.TRIAL_ALREADY_USED, show_alert=True)
            return
        
        # Check if user already has active subscription
        if SubscriptionService.has_active_subscription(callback.from_user.id):
            await callback.answer("لديك اشتراك نشط بالفعل", show_alert=True)
            return
        
        # Create trial subscription
        user = UserService.get_user_by_telegram_id(callback.from_user.id)
        subscription = SubscriptionService.create_subscription(
            user.id,
            plan_id,
            is_trial=True
        )
        
        # Mark trial as used
        UserService.mark_free_trial_used(callback.from_user.id)
        
        # Add user to channel
        channel_manager = ChannelManager(callback.bot)
        await channel_manager.add_user(callback.from_user.id)
        
        # Send success message (new message for trial activation)
        await callback.message.answer(
            Texts.TRIAL_ACTIVATED.format(
                days=settings.FREE_TRIAL_DAYS,
                end_date=subscription.end_date.strftime("%Y-%m-%d %H:%M")
            ),
            reply_markup=get_main_menu_keyboard()
        )
        await callback.answer("تم تفعيل التجربة المجانية بنجاح!")
    except Exception as e:
        logger.error(f"Error in callback_trial: {e}", exc_info=True)
        await callback.answer(Texts.ERROR_OCCURRED, show_alert=True)


@router.callback_query(F.data.startswith("pay_"))
async def callback_pay(callback: CallbackQuery):
    """Handle payment callback"""
    try:
        plan_id = int(callback.data.split("_")[1])
        
        with get_session() as session:
            plan = session.query(Plan).filter(Plan.id == plan_id).first()
        
        if not plan:
            await callback.answer("الخطة غير موجودة", show_alert=True)
            return
        
        # Check if user already has active subscription
        if SubscriptionService.has_active_subscription(callback.from_user.id):
            await callback.answer("لديك اشتراك نشط بالفعل", show_alert=True)
            return
        
        # Create payment
        user = UserService.get_user_by_telegram_id(callback.from_user.id)
        payment = PaymentService.create_payment(
            user.id,
            plan_id,
            float(plan.price),
            plan.currency,
            provider=settings.CRYPTO_PROVIDER,
            wallet_address=settings.CRYPTO_WALLET_ADDRESS
        )
        
        await callback.message.edit_text(
            Texts.PAYMENT_INSTRUCTIONS.format(
                plan_name=plan.name_ar or plan.name,
                amount=plan.price,
                currency=plan.currency,
                wallet_address=settings.CRYPTO_WALLET_ADDRESS
            ),
            reply_markup=get_payment_keyboard(payment.id, settings.CRYPTO_WALLET_ADDRESS),
            parse_mode="Markdown"
        )
        await callback.answer()
    except TelegramBadRequest:
        await callback.answer()
    except Exception as e:
        logger.error(f"Error in callback_pay: {e}", exc_info=True)
        await callback.answer(Texts.ERROR_OCCURRED, show_alert=True)


@router.callback_query(F.data.startswith("confirm_payment_"))
async def callback_confirm_payment(callback: CallbackQuery):
    """Handle payment confirmation callback"""
    try:
        payment_id = int(callback.data.split("_")[2])
        
        payment = PaymentService.get_payment(payment_id)
        if not payment:
            await callback.answer("الدفعة غير موجودة", show_alert=True)
            return
        
        if payment.user.telegram_id != callback.from_user.id:
            await callback.answer("ليس لديك صلاحية لهذه الدفعة", show_alert=True)
            return
        
        if payment.status.value == "completed":
            await callback.answer("تم تأكيد هذه الدفعة مسبقاً", show_alert=True)
            return
        
        # Confirm payment (admin should verify manually or via webhook)
        # For now, we'll auto-confirm (in production, add admin verification)
        success = PaymentService.confirm_payment(payment_id)
        
        if success:
            # Add user to channel
            channel_manager = ChannelManager(callback.bot)
            await channel_manager.add_user(callback.from_user.id)
            
            # Send success message (new message for payment confirmation)
            await callback.message.answer(
                Texts.PAYMENT_CONFIRMED,
                reply_markup=get_main_menu_keyboard()
            )
            await callback.answer("تم تأكيد الدفع بنجاح!")
        else:
            await callback.answer("فشل تأكيد الدفع", show_alert=True)
    except Exception as e:
        logger.error(f"Error in callback_confirm_payment: {e}", exc_info=True)
        await callback.answer(Texts.ERROR_OCCURRED, show_alert=True)


@router.callback_query(F.data == "my_subscriptions")
async def callback_my_subscriptions(callback: CallbackQuery):
    """Handle my subscriptions callback"""
    try:
        user = UserService.get_user_by_telegram_id(callback.from_user.id)
        if not user:
            await callback.answer("المستخدم غير موجود", show_alert=True)
            return
        
        subscriptions = SubscriptionService.get_user_subscriptions(user.id)
        
        if not subscriptions:
            text = Texts.NO_SUBSCRIPTION
        else:
            # Show latest subscription
            latest = subscriptions[0]
            text = Texts.format_subscription(latest)
        
        await callback.message.edit_text(
            text,
            reply_markup=get_subscriptions_keyboard()
        )
        await callback.answer()
    except TelegramBadRequest:
        await callback.answer()
    except Exception as e:
        logger.error(f"Error in callback_my_subscriptions: {e}", exc_info=True)
        await callback.answer(Texts.ERROR_OCCURRED, show_alert=True)


@router.callback_query(F.data == "referral")
async def callback_referral(callback: CallbackQuery):
    """Handle referral callback"""
    try:
        user = UserService.get_user_by_telegram_id(callback.from_user.id)
        if not user:
            await callback.answer("المستخدم غير موجود", show_alert=True)
            return
        
        await callback.message.edit_text(
            Texts.REFERRAL_CODE.format(referral_code=user.referral_code),
            reply_markup=get_referral_keyboard(user.referral_code),
            parse_mode="Markdown"
        )
        await callback.answer()
    except TelegramBadRequest:
        await callback.answer()
    except Exception as e:
        logger.error(f"Error in callback_referral: {e}", exc_info=True)
        await callback.answer(Texts.ERROR_OCCURRED, show_alert=True)


@router.callback_query(F.data.startswith("copy_referral_"))
async def callback_copy_referral(callback: CallbackQuery):
    """Handle copy referral code callback"""
    referral_code = callback.data.replace("copy_referral_", "")
    referral_link = f"https://t.me/{callback.message.bot.username}?start={referral_code}"
    
    await callback.answer(
        f"رابط الإحالة:\n{referral_link}",
        show_alert=True
    )


@router.callback_query(F.data == "referral_stats")
async def callback_referral_stats(callback: CallbackQuery):
    """Handle referral stats callback"""
    try:
        user = UserService.get_user_by_telegram_id(callback.from_user.id)
        if not user:
            await callback.answer("المستخدم غير موجود", show_alert=True)
            return
        
        stats = ReferralService.get_referral_stats(user.id)
        
        from services.referral_service import REFERRAL_POINTS
        
        await callback.message.edit_text(
            Texts.REFERRAL_STATS.format(
                total_referrals=stats["total_referrals"],
                total_points=stats["total_points"],
                points_per_referral=REFERRAL_POINTS
            ),
            reply_markup=get_referral_keyboard(user.referral_code)
        )
        await callback.answer()
    except TelegramBadRequest:
        await callback.answer()
    except Exception as e:
        logger.error(f"Error in callback_referral_stats: {e}", exc_info=True)
        await callback.answer(Texts.ERROR_OCCURRED, show_alert=True)


@router.callback_query(F.data == "redeem_points")
async def callback_redeem_points(callback: CallbackQuery):
    """Handle redeem points callback"""
    try:
        user = UserService.get_user_by_telegram_id(callback.from_user.id)
        if not user:
            await callback.answer("المستخدم غير موجود", show_alert=True)
            return
        
        total_points = ReferralService.get_user_total_points(user.id)
        
        if total_points == 0:
            await callback.answer(Texts.NO_POINTS, show_alert=True)
            return
        
        # For now, just show points (can be extended with redemption options)
        await callback.message.edit_text(
            f"🎁 نقاطك الحالية: {total_points}\n\n"
            "سيتم إضافة خيارات الاستبدال قريباً.",
            reply_markup=get_referral_keyboard(user.referral_code)
        )
        await callback.answer()
    except TelegramBadRequest:
        await callback.answer()
    except Exception as e:
        logger.error(f"Error in callback_redeem_points: {e}", exc_info=True)
        await callback.answer(Texts.ERROR_OCCURRED, show_alert=True)


@router.callback_query(F.data == "info")
async def callback_info(callback: CallbackQuery):
    """Handle info callback"""
    try:
        info_text = """ℹ️ معلومات البوت

هذا البوت لإدارة الاشتراكات المدفوعة لقناة تيليغرام.

المميزات:
• خطط اشتراك متعددة
• تجربة مجانية
• نظام إحالة
• دفع بالعملات المشفرة

للتواصل: @support"""
        
        await callback.message.edit_text(
            info_text,
            reply_markup=get_info_keyboard()
        )
        await callback.answer()
    except TelegramBadRequest:
        await callback.answer()
    except Exception as e:
        logger.error(f"Error in callback_info: {e}", exc_info=True)
        await callback.answer(Texts.ERROR_OCCURRED, show_alert=True)

