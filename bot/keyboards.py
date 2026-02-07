from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from typing import List, Optional
from database.models import Plan


def get_back_button(callback_data: str = "menu") -> InlineKeyboardButton:
    """Get back button"""
    return InlineKeyboardButton(text="⬅️ رجوع", callback_data=callback_data)


def get_main_menu_keyboard() -> InlineKeyboardMarkup:
    """Main menu keyboard"""
    keyboard = [
        [InlineKeyboardButton(text="📋 الخطط والأسعار", callback_data="plans")],
        [InlineKeyboardButton(text="💳 اشتراك", callback_data="subscribe")],
        [InlineKeyboardButton(text="📊 اشتراكاتي", callback_data="my_subscriptions")],
        [InlineKeyboardButton(text="🎁 نظام الإحالة", callback_data="referral")],
        [InlineKeyboardButton(text="ℹ️ معلومات", callback_data="info")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_plans_keyboard(plans: List[Plan], show_back: bool = True) -> InlineKeyboardMarkup:
    """Plans selection keyboard"""
    keyboard = []
    for plan in plans:
        plan_name = plan.name_ar or plan.name
        button_text = f"{plan_name} - {plan.price} {plan.currency}"
        keyboard.append([
            InlineKeyboardButton(
                text=button_text,
                callback_data=f"plan_{plan.id}"
            )
        ])
    
    if show_back:
        keyboard.append([get_back_button("menu")])
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_plan_details_keyboard(plan_id: int, can_use_trial: bool = False) -> InlineKeyboardMarkup:
    """Plan details keyboard"""
    keyboard = []
    
    if can_use_trial:
        keyboard.append([
            InlineKeyboardButton(
                text="🆓 تجربة مجانية",
                callback_data=f"trial_{plan_id}"
            )
        ])
    
    keyboard.append([
        InlineKeyboardButton(
            text="💳 الدفع والاشتراك",
            callback_data=f"pay_{plan_id}"
        )
    ])
    keyboard.append([get_back_button("plans")])
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_payment_network_keyboard(plan_id: int) -> InlineKeyboardMarkup:
    """Payment network selection keyboard"""
    keyboard = [
        [
            InlineKeyboardButton(
                text="💎 USDT (TRC20)",
                callback_data=f"pay_network_{plan_id}_TRC20"
            )
        ],
        [
            InlineKeyboardButton(
                text="💎 USDT (BSC)",
                callback_data=f"pay_network_{plan_id}_BSC"
            )
        ],
        [get_back_button(f"plan_{plan_id}")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_payment_keyboard(payment_id: int, wallet_address: str) -> InlineKeyboardMarkup:
    """Payment instructions keyboard"""
    keyboard = [
        [
            InlineKeyboardButton(
                text="✅ تأكيد الدفع",
                callback_data=f"confirm_payment_{payment_id}"
            )
        ],
        [get_back_button("menu")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_referral_keyboard(referral_code: str) -> InlineKeyboardMarkup:
    """Referral menu keyboard"""
    keyboard = [
        [
            InlineKeyboardButton(
                text="📋 نسخ كود الإحالة",
                callback_data=f"copy_referral_{referral_code}"
            )
        ],
        [
            InlineKeyboardButton(
                text="📊 إحصائياتي",
                callback_data="referral_stats"
            )
        ],
        [
            InlineKeyboardButton(
                text="🎁 استبدال النقاط",
                callback_data="redeem_points"
            )
        ],
        [get_back_button("menu")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_subscriptions_keyboard() -> InlineKeyboardMarkup:
    """My subscriptions keyboard"""
    keyboard = [
        [get_back_button("menu")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_info_keyboard() -> InlineKeyboardMarkup:
    """Info menu keyboard"""
    keyboard = [
        [get_back_button("menu")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)
