# دليل متقدم للإيموجي المتحرك والملصقات

## نظرة عامة

البوت يدعم ثلاثة أنواع من الإيموجي المتحرك:

### 1. الملصقات المتحركة (TGS) ✅ المستخدم حالياً
- **الصيغة**: TGS (Telegram Sticker)
- **الوصف**: ملف JSON مبني على Lottie مضغوط (Gzipped)
- **المميزات**: خفيفة، دقة عالية (Vector)، 60 إطار/ثانية
- **الاستخدام**: `send_sticker_if_available()`

### 2. إيموجي النرد/التفاعل (Dice Emoji) 🎲
- **الصيغ المدعومة**: 🎲, 🎯, 🏀, ⚽, 🎰, 🎳
- **الاستخدام**: `send_dice_emoji(bot, chat_id, "🎲")`
- **مثال**:
```python
from bot.sticker_helpers import send_dice_emoji
await send_dice_emoji(bot, user_id, "🎲")
```

### 3. إيموجي مخصص (Custom Emoji) - Premium
- **يتطلب**: `custom_emoji_id` من Telegram
- **الاستخدام**: `send_custom_emoji()`
- **ملاحظة**: يحتاج إعداد خاص من Telegram

## إنشاء ملفات TGS

### الطريقة الموصى بها: Adobe After Effects

1. **التصميم**:
   - صمم الإيموجي/الملصق في After Effects
   - استخدم Vector layers للحصول على أفضل جودة

2. **التصدير**:
   - ثبت إضافة [Bodymovin-TG](https://github.com/ed-asriyan/bodymovin-tg)
   - تصدير مباشر إلى `.tgs`

3. **النتيجة**:
   - ملف `.tgs` جاهز للاستخدام

### من Lottie JSON:

```bash
# تثبيت lottie2tg
npm install -g lottie2tg

# التحويل
lottie2tg input.json output.tgs
```

### من SVG (يتطلب خطوات إضافية):

⚠️ **SVG لا يدعم مباشرة** - يجب التحويل:

1. حول SVG إلى Lottie JSON:
   - استخدم [LottieFiles](https://lottiefiles.com/)
   - أو أدوات أخرى مثل `svg-to-lottie`

2. حول Lottie JSON إلى TGS:
```bash
lottie2tg converted.json output.tgs
```

## أفضل الممارسات

### 1. حجم الملف:
- **الحد الأقصى**: 64 KB
- **الموصى به**: أقل من 32 KB
- استخدم compression في After Effects

### 2. المدة:
- **الموصى به**: 1-3 ثواني
- تجنب الحلقات الطويلة جداً

### 3. الدقة:
- استخدم Vector layers للحصول على أفضل جودة
- تجنب الصور النقطية (Raster)

### 4. الأداء:
- قلل عدد الـ layers
- استخدم shapes بدلاً من masks معقدة

## أمثلة الكود

### إرسال ملصق TGS:
```python
from bot.sticker_helpers import send_sticker_if_available

# في handler
await send_sticker_if_available(bot, user_id, "success")
```

### إرسال إيموجي نرد:
```python
from bot.sticker_helpers import send_dice_emoji

# إرسال نرد
await send_dice_emoji(bot, user_id, "🎲")

# إرسال سهم
await send_dice_emoji(bot, user_id, "🎯")
```

### إرسال إيموجي مخصص (Premium):
```python
from bot.sticker_helpers import send_custom_emoji

await send_custom_emoji(
    bot=bot,
    chat_id=user_id,
    text="مرحباً 👻",
    emoji_id="546546546546...",  # من Telegram
    offset=7,  # موقع الإيموجي في النص
    length=2   # طول placeholder
)
```

## استكشاف الأخطاء

### المشكلة: الملف كبير جداً
**الحل**: 
- قلل المدة
- استخدم compression
- قلل عدد الـ layers

### المشكلة: الجودة منخفضة
**الحل**:
- استخدم Vector layers
- تجنب الصور النقطية
- تأكد من export settings في After Effects

### المشكلة: الملف لا يعمل
**الحل**:
- تأكد من أن الملف بصيغة `.tgs` صحيحة
- تحقق من أن الملف غير تالف
- جرب تحويله مرة أخرى

## الموارد المفيدة

- [Bodymovin-TG Documentation](https://github.com/ed-asriyan/bodymovin-tg)
- [LottieFiles](https://lottiefiles.com/) - مكتبة animations
- [Telegram Bot API - Stickers](https://core.telegram.org/bots/api#stickers)
- [aiogram Documentation](https://docs.aiogram.dev/)

