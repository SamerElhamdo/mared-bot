# Mared Bot - Telegram Subscription Management Bot

بوت تيليغرام لإدارة الاشتراكات المدفوعة لقناة تيليغرام باستخدام Python و aiogram.

## المميزات

- ✅ إدارة اشتراكات مدفوعة للقناة
- ✅ إضافة/إزالة المستخدمين تلقائياً من القناة
- ✅ واجهة سهلة باستخدام Inline Keyboard
- ✅ دعم عدة خطط اشتراك (أسبوعي/شهري/سنوي)
- ✅ تجربة مجانية (مرة واحدة لكل مستخدم)
- ✅ نظام إحالة (Referral System) مع نقاط
- ✅ دفع بالعملات المشفرة (قابل للتوسعة)
- ✅ قاعدة بيانات PostgreSQL مع SQLAlchemy
- ✅ Clean Architecture / Services Pattern
- ✅ دعم تعدد اللغات (جاهز للبناء)
- ✅ Logging منظم
- ✅ Docker Compose جاهز للنشر

## المتطلبات

- Python 3.11+
- PostgreSQL 16+
- Docker & Docker Compose (للنشر)

## التثبيت والتشغيل

### 1. استنساخ المشروع

```bash
git clone <repository-url>
cd mared-bot
```

### 2. إعداد متغيرات البيئة

انسخ ملف `.env.example` إلى `.env` واملأ القيم:

```bash
cp .env.example .env
```

عدّل ملف `.env`:

```env
# Telegram Bot Configuration
BOT_TOKEN=your_bot_token_here
CHANNEL_ID=your_channel_id_here

# Database Configuration
DATABASE_URL=postgresql://postgres:postgres@db:5432/mared_bot

# Crypto Payment Configuration
CRYPTO_PROVIDER=manual
CRYPTO_WALLET_ADDRESS=your_wallet_address_here

# Bot Configuration
ADMIN_USER_IDS=123456789,987654321
FREE_TRIAL_DAYS=7

# Logging
LOG_LEVEL=INFO
```

### 3. الحصول على BOT_TOKEN

1. افتح [@BotFather](https://t.me/BotFather) على تيليغرام
2. أرسل `/newbot` واتبع التعليمات
3. انسخ الـ Token الذي يعطيه لك

### 4. الحصول على CHANNEL_ID

1. أنشئ قناة على تيليغرام
2. أضف البوت كـ Administrator في القناة
3. للحصول على Channel ID:
   - أرسل رسالة في القناة
   - افتح الرابط: `https://api.telegram.org/bot<BOT_TOKEN>/getUpdates`
   - ابحث عن `"chat":{"id":-1001234567890}` (الرقم السالب هو Channel ID)

### 5. تشغيل المشروع

#### باستخدام Docker Compose (موصى به)

```bash
docker-compose up -d
```

#### بدون Docker

```bash
# إنشاء virtual environment
python -m venv venv
source venv/bin/activate  # على Windows: venv\Scripts\activate

# تثبيت المتطلبات
pip install -r requirements.txt

# تشغيل migrations
alembic upgrade head

# تهيئة الخطط الافتراضية
python scripts/init_plans.py

# تشغيل البوت
python -m bot.main
```

### 6. تهيئة الخطط الافتراضية

بعد تشغيل قاعدة البيانات لأول مرة، قم بتشغيل:

```bash
python scripts/init_plans.py
```

أو إذا كنت تستخدم Docker:

```bash
docker-compose exec bot python scripts/init_plans.py
```

## بنية المشروع

```
mared-bot/
├── alembic/              # Database migrations
├── bot/                  # Bot handlers and logic
│   ├── handlers.py      # Message and callback handlers
│   ├── keyboards.py     # Inline keyboard definitions
│   ├── texts.py         # Text messages (i18n ready)
│   ├── channel_manager.py  # Channel membership management
│   └── main.py          # Bot entry point
├── config/              # Configuration
│   └── settings.py      # Settings and environment variables
├── database/            # Database layer
│   ├── base.py         # Database connection and base
│   └── models.py        # SQLAlchemy models
├── services/            # Business logic services
│   ├── user_service.py
│   ├── subscription_service.py
│   ├── payment_service.py
│   └── referral_service.py
├── utils/               # Utilities
│   ├── logging.py       # Logging setup
│   └── referral_code.py # Referral code generation
├── scripts/             # Utility scripts
│   └── init_plans.py   # Initialize default plans
├── docker-compose.yml   # Docker Compose configuration
├── Dockerfile          # Docker image definition
├── requirements.txt    # Python dependencies
└── README.md          # This file
```

## الاستخدام

### الأوامر الأساسية

- `/start` - بدء البوت (رسالة ترحيب)
- `/menu` - عرض القائمة الرئيسية

### القوائم والتنقل

البوت يستخدم Inline Keyboards للتنقل:

1. **القائمة الرئيسية**:
   - 📋 الخطط والأسعار
   - 💳 اشتراك
   - 📊 اشتراكاتي
   - 🎁 نظام الإحالة
   - ℹ️ معلومات

2. **الخطط**: عرض جميع الخطط المتاحة مع إمكانية اختيار خطة

3. **تفاصيل الخطة**: 
   - زر "🆓 تجربة مجانية" (إذا متاح)
   - زر "💳 الدفع والاشتراك"

4. **الدفع**: تعليمات الدفع مع زر "✅ تأكيد الدفع"

5. **نظام الإحالة**:
   - عرض كود الإحالة
   - إحصائيات الإحالة
   - استبدال النقاط

### زر الرجوع

جميع القوائم تحتوي على زر "⬅️ رجوع" للعودة للقائمة السابقة.

## قاعدة البيانات

### الجداول

- `users` - معلومات المستخدمين
- `plans` - خطط الاشتراك
- `subscriptions` - الاشتراكات
- `payments` - المدفوعات
- `referrals` - الإحالات
- `referral_points` - نقاط الإحالة

### Migrations

استخدم Alembic لإدارة migrations:

```bash
# إنشاء migration جديد
alembic revision --autogenerate -m "description"

# تطبيق migrations
alembic upgrade head

# التراجع عن migration
alembic downgrade -1
```

## نظام الدفع

حالياً النظام يدعم الدفع اليدوي (Manual):
1. المستخدم يختار خطة
2. يحصل على عنوان المحفظة
3. يرسل المبلغ
4. يضغط "✅ تأكيد الدفع"
5. (في الإنتاج: يحتاج تأكيد من Admin)

### إضافة مزود دفع جديد

1. أنشئ ملف في `services/payment_providers/`
2. أنشئ class يرث من `BasePaymentProvider`
3. أضف المنطق في `PaymentService`

## نظام الإحالة

- كل مستخدم لديه كود إحالة فريد
- عند تسجيل مستخدم جديد عبر رابط الإحالة، يحصل المُحيل على نقاط
- النقاط قابلة للاستبدال (يمكن إضافة خيارات الاستبدال)

## المهام المجدولة

البوت يتحقق تلقائياً من الاشتراكات المنتهية كل ساعة:
- يغير حالة الاشتراك إلى "منتهي"
- يزيل المستخدم من القناة
- يرسل إشعار للمستخدم

## النشر على Dokploy

1. ارفع المشروع إلى Git repository
2. في Dokploy:
   - أنشئ مشروع جديد
   - اختر Git repository
   - اختر Docker Compose
   - أضف متغيرات البيئة من `.env`
   - انشر

## التطوير المستقبلي

- [ ] إضافة مزودي دفع إضافيين (Stripe, PayPal, etc.)
- [ ] واجهة Admin للتحكم في الخطط والمدفوعات
- [ ] نظام إشعارات متقدم
- [ ] إحصائيات مفصلة
- [ ] دعم تعدد اللغات الكامل
- [ ] Webhook للدفع التلقائي
- [ ] نظام استبدال النقاط الكامل

## الأمان

- ⚠️ **لا تضع secrets في الكود**
- استخدم متغيرات البيئة فقط
- تأكد من حماية `.env` في `.gitignore`
- استخدم HTTPS في الإنتاج
- راجع صلاحيات البوت في القناة

## الدعم

للأسئلة والمشاكل، افتح Issue في Repository.

## الترخيص

[أضف الترخيص هنا]

