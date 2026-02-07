from typing import Dict
from database.models import Plan, Subscription, Payment
from datetime import datetime


class Texts:
    """Text messages for the bot (ready for i18n)"""
    
    WELCOME = """مرحباً بك في بوت إدارة الاشتراكات! 🎉

استخدم الأزرار أدناه للتنقل في القائمة."""

    MAIN_MENU = """القائمة الرئيسية

اختر من الخيارات أدناه:"""

    PLANS_TITLE = """📋 الخطط والأسعار

اختر الخطة المناسبة لك:"""

    PLAN_DETAILS = """📋 تفاصيل الخطة

الاسم: {name}
المدة: {duration_days} يوم
السعر: {price} {currency}

{description}"""

    SUBSCRIPTION_ACTIVE = """✅ اشتراكك نشط

الخطة: {plan_name}
تاريخ البداية: {start_date}
تاريخ الانتهاء: {end_date}
الحالة: {status}"""

    SUBSCRIPTION_EXPIRED = """❌ اشتراكك منتهي

الخطة: {plan_name}
تاريخ الانتهاء: {end_date}

يمكنك تجديد اشتراكك من القائمة الرئيسية."""

    NO_SUBSCRIPTION = """⚠️ ليس لديك اشتراك نشط حالياً

يمكنك الاشتراك من القائمة الرئيسية."""

    TRIAL_ACTIVATED = """🎉 تم تفعيل التجربة المجانية!

مدة التجربة: {days} يوم
تاريخ الانتهاء: {end_date}

تم إضافتك للقناة بنجاح!"""

    TRIAL_ALREADY_USED = """⚠️ لقد استخدمت التجربة المجانية مسبقاً

يمكنك الاشتراك في إحدى الخطط المدفوعة."""

    PAYMENT_INSTRUCTIONS = """💳 تعليمات الدفع

الخطة: {plan_name}
المبلغ: {amount} {currency}

يرجى إرسال المبلغ إلى العنوان التالي:
`{wallet_address}`

بعد إتمام الدفع، اضغط على زر "✅ تأكيد الدفع"."""

    PAYMENT_PENDING = """⏳ في انتظار تأكيد الدفع

رقم الدفعة: {payment_id}
المبلغ: {amount} {currency}

سيتم تفعيل اشتراكك بعد تأكيد الدفع."""

    PAYMENT_CONFIRMED = """✅ تم تأكيد الدفع بنجاح!

تم تفعيل اشتراكك وإضافتك للقناة."""

    REFERRAL_CODE = """🎁 كود الإحالة الخاص بك

`{referral_code}`

شارك هذا الكود مع أصدقائك واحصل على نقاط عند اشتراكهم!"""

    REFERRAL_STATS = """📊 إحصائيات الإحالة

إجمالي الإحالات: {total_referrals}
إجمالي النقاط: {total_points}

كل إحالة ناجحة = {points_per_referral} نقطة"""

    NO_POINTS = """⚠️ ليس لديك نقاط حالياً

احصل على النقاط من خلال نظام الإحالة."""

    ERROR_OCCURRED = """❌ حدث خطأ

يرجى المحاولة مرة أخرى أو التواصل مع الدعم."""

    CHANNEL_ADDED = """✅ تم إضافتك للقناة بنجاح!"""

    CHANNEL_REMOVED = """❌ تم إزالتك من القناة بسبب انتهاء الاشتراك."""

    @staticmethod
    def format_plan_details(plan: Plan) -> str:
        """Format plan details"""
        duration_text = {
            "weekly": "أسبوعي",
            "monthly": "شهري",
            "yearly": "سنوي"
        }
        duration = duration_text.get(plan.duration.value, plan.duration.value)
        
        return Texts.PLAN_DETAILS.format(
            name=plan.name_ar or plan.name,
            duration_days=plan.duration_days,
            price=plan.price,
            currency=plan.currency,
            description=f"المدة: {duration}"
        )
    
    @staticmethod
    def format_subscription(subscription: Subscription) -> str:
        """Format subscription info"""
        if subscription.status.value in ["expired", "cancelled"]:
            return Texts.SUBSCRIPTION_EXPIRED.format(
                plan_name=subscription.plan.name_ar or subscription.plan.name,
                end_date=subscription.end_date.strftime("%Y-%m-%d %H:%M")
            )
        else:
            status_text = {
                "active": "نشط",
                "trial": "تجربة مجانية"
            }
            return Texts.SUBSCRIPTION_ACTIVE.format(
                plan_name=subscription.plan.name_ar or subscription.plan.name,
                start_date=subscription.start_date.strftime("%Y-%m-%d %H:%M"),
                end_date=subscription.end_date.strftime("%Y-%m-%d %H:%M"),
                status=status_text.get(subscription.status.value, subscription.status.value)
            )

