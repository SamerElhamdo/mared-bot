# دليل استخدام Animated Emoji (Stickers)

هذا الدليل يشرح كيفية إضافة واستخدام الـ animated emoji (ملفات .tgs) في البوت.

## نظرة عامة

البوت يدعم إرسال animated stickers من ملفات `.tgs` في نقاط محددة من التفاعل:
- رسالة الترحيب
- تفعيل التجربة المجانية
- تأكيد الدفع
- اختيار طريقة الدفع

## إضافة Stickers

### الطريقة 1: عبر البوت (للمسؤولين)

1. تأكد من أنك مسؤول (مضاف في `ADMIN_USER_IDS` في `.env`)
2. أرسل `/upload_sticker` للبوت
3. أرسل ملف `.tgs` مع إضافة اسم الـ sticker في الـ caption

**الأسماء المتاحة:**
- `success` - للنجاح (يُرسل مع رسالة الترحيب)
- `trial` - للتجربة المجانية
- `payment` - للدفع
- `confirm` - لتأكيد الدفع
- `error` - للأخطاء
- `warning` - للتحذيرات
- `trc20` - لشبكة TRC20
- `bsc` - لشبكة BSC
- `plans` - للخطط
- `subscribe` - للاشتراك
- `subscriptions` - للاشتراكات
- `referral` - لنظام الإحالة
- `info` - للمعلومات
- `back` - لزر الرجوع

**مثال:**
```
1. أرسل: /upload_sticker
2. أرسل ملف: success.tgs
3. في الـ caption: success
```

### الطريقة 2: يدوياً

1. ضع ملفات `.tgs` في مجلد `stickers/`
2. استخدم الأسماء التالية:
   - `success.tgs`
   - `trial.tgs`
   - `payment.tgs`
   - `confirm.tgs`
   - `error.tgs`
   - `warning.tgs`
   - `trc20.tgs`
   - `bsc.tgs`
   - `plans.tgs`
   - `subscribe.tgs`
   - `subscriptions.tgs`
   - `referral.tgs`
   - `info.tgs`
   - `back.tgs`

## متى يتم إرسال Stickers

### تلقائياً:
- **رسالة الترحيب** (`/start`): يرسل `success.tgs` إذا كان متوفر
- **تفعيل التجربة**: يرسل `trial.tgs` عند تفعيل التجربة المجانية
- **تأكيد الدفع**: يرسل `payment.tgs` عند تأكيد الدفع بنجاح
- **اختيار طريقة الدفع**: يرسل `payment.tgs` عند اختيار الدفع

### يدوياً (للمستقبل):
يمكن إضافة stickers في أي مكان في الكود باستخدام:
```python
from bot.sticker_helpers import send_sticker_if_available

await send_sticker_if_available(bot, chat_id, "sticker_name")
```

## إنشاء ملفات .tgs

### من Lottie (.json):
```bash
# استخدام lottie2tg
lottie2tg input.json output.tgs
```

### من After Effects:
1. تصدير كـ Lottie (.json)
2. تحويل إلى .tgs باستخدام `lottie2tg`

### أدوات مفيدة:
- [lottie2tg](https://github.com/ed-asriyan/lottie2tg) - لتحويل Lottie إلى .tgs
- [TGS to GIF](https://tgs-to-gif.com/) - لمعاينة الـ stickers
- [LottieFiles](https://lottiefiles.com/) - مكتبة كبيرة من Lottie animations

## التحقق من Stickers

### عرض قائمة Stickers:
```
/list_stickers
```

سيظهر قائمة بجميع الـ stickers وحالتها (✅ متوفر / ❌ غير متوفر)

## ملاحظات مهمة

1. **الحجم**: ملفات .tgs يجب أن تكون صغيرة (عادة < 64KB)
2. **التنسيق**: فقط ملفات .tgs مدعومة (Telegram Sticker format)
3. **الاختيارية**: إذا لم يكن الـ sticker متوفر، سيتم إرسال الرسالة بدون sticker
4. **الأداء**: الـ stickers تُرسل قبل الرسائل بفترة قصيرة (0.3 ثانية)

## هيكل الملفات

```
mared-bot/
├── stickers/
│   ├── success.tgs
│   ├── trial.tgs
│   ├── payment.tgs
│   └── ...
└── bot/
    ├── stickers.py          # إدارة الـ stickers
    ├── sticker_helpers.py    # دوال مساعدة
    └── admin_handlers.py     # أوامر المسؤول
```

## استكشاف الأخطاء

### الـ sticker لا يُرسل:
1. تحقق من أن الملف موجود في `stickers/`
2. تحقق من اسم الملف (يجب أن يطابق الاسم في `STICKER_MAP`)
3. تحقق من السجلات: `docker-compose logs bot`

### خطأ في رفع الـ sticker:
1. تأكد من أنك مسؤول
2. تأكد من أن الملف هو `.tgs`
3. تأكد من أن الاسم في الـ caption صحيح

## أمثلة

### إضافة sticker جديد:
```python
# في bot/stickers.py
STICKER_MAP = {
    # ... existing stickers
    "new_sticker": "new_sticker.tgs",
}

# في bot/handlers.py
await send_sticker_if_available(bot, chat_id, "new_sticker")
```

