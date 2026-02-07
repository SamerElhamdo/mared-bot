# Architecture Documentation

## نظرة عامة على البنية

المشروع مبني باستخدام Clean Architecture / Services Pattern لضمان قابلية الصيانة والتوسعة.

## الهيكل العام

```
┌─────────────────────────────────────────┐
│         Bot Handlers Layer              │
│  (handlers.py, keyboards.py, texts.py) │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│         Services Layer                   │
│  (user, subscription, payment, referral) │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│         Database Layer                  │
│  (models.py, base.py)                   │
└─────────────────────────────────────────┘
```

## الطبقات (Layers)

### 1. Bot Handlers Layer (`bot/`)

**المسؤولية**: معالجة الرسائل والتفاعلات مع المستخدم

- `handlers.py`: معالجات الرسائل والـ callbacks
- `keyboards.py`: تعريفات Inline Keyboards
- `texts.py`: النصوص والرسائل (جاهز لـ i18n)
- `channel_manager.py`: إدارة عضوية القناة
- `main.py`: نقطة الدخول الرئيسية

**المبادئ**:
- Handlers بسيطة وتركز على التفاعل فقط
- كل المنطق في Services
- استخدام `edit_message_text` بدلاً من رسائل جديدة

### 2. Services Layer (`services/`)

**المسؤولية**: منطق العمل (Business Logic)

- `user_service.py`: إدارة المستخدمين
- `subscription_service.py`: إدارة الاشتراكات
- `payment_service.py`: إدارة المدفوعات
- `referral_service.py`: نظام الإحالة

**المبادئ**:
- Services مستقلة عن Bot framework
- كل Service مسؤول عن domain واحد
- استخدام Database session management

### 3. Database Layer (`database/`)

**المسؤولية**: إدارة البيانات

- `models.py`: SQLAlchemy models
- `base.py`: Database connection و session management

**المبادئ**:
- استخدام ORM (SQLAlchemy)
- Migrations عبر Alembic
- Relationships واضحة

## تدفق البيانات

### مثال: إنشاء اشتراك جديد

```
User clicks "Subscribe" button
    ↓
Handler receives callback
    ↓
Handler calls SubscriptionService.create_subscription()
    ↓
Service creates Subscription in database
    ↓
Service returns Subscription object
    ↓
Handler calls ChannelManager.add_user()
    ↓
Handler sends success message
```

## إضافة ميزة جديدة

### مثال: إضافة مزود دفع جديد

1. **إنشاء Payment Provider**:
   ```python
   # services/payment_providers/stripe_provider.py
   class StripePaymentProvider:
       def create_payment(self, amount, currency):
           # Stripe logic
           pass
   ```

2. **تحديث PaymentService**:
   ```python
   # services/payment_service.py
   def create_payment(..., provider="stripe"):
       if provider == "stripe":
           # Use StripeProvider
       elif provider == "manual":
           # Use manual
   ```

3. **تحديث Handler**:
   ```python
   # bot/handlers.py
   @router.callback_query(F.data == "pay_stripe")
   async def callback_pay_stripe(callback):
       # Handle Stripe payment
   ```

## إدارة الأخطاء

### Error Handling Strategy

1. **في Services**: 
   - رفع exceptions واضحة
   - Logging للأخطاء

2. **في Handlers**:
   - Try/except لكل handler
   - رسائل خطأ واضحة للمستخدم
   - Logging مفصل

3. **في Database**:
   - Session rollback عند الخطأ
   - استخدام context managers

## Logging

- **Levels**: INFO, WARNING, ERROR
- **Format**: Timestamp, Logger name, Level, Message
- **Output**: Console + File (`bot.log`)

## Testing (جاهز للتطوير)

يمكن إضافة tests في `tests/`:

```
tests/
├── test_services/
│   ├── test_user_service.py
│   ├── test_subscription_service.py
│   └── ...
├── test_handlers/
│   └── test_handlers.py
└── conftest.py
```

## التوسعة المستقبلية

### إضافة ميزات جديدة

1. **Admin Panel**:
   - إنشاء `admin/` directory
   - Admin handlers منفصلة
   - Middleware للتحقق من Admin

2. **Webhooks**:
   - إنشاء `webhooks/` directory
   - Webhook handlers للدفع

3. **i18n**:
   - استخدام `aiogram-i18n` أو `gettext`
   - تحديث `texts.py` لدعم multiple languages

4. **Caching**:
   - إضافة Redis للـ caching
   - Cache للخطط والاشتراكات النشطة

## Best Practices

1. **Separation of Concerns**: كل layer مسؤول عن شيء واحد
2. **Dependency Injection**: Services مستقلة
3. **Error Handling**: معالجة شاملة للأخطاء
4. **Logging**: Logging في كل المستويات
5. **Type Hints**: استخدام type hints حيث ممكن
6. **Documentation**: توثيق الوظائف المهمة

