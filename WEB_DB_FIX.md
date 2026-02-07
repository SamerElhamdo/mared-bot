# إصلاح مشكلة الاتصال بقاعدة البيانات في Web UI

## المشكلة
خدمة الويب لا تستطيع الاتصال بقاعدة البيانات - خطأ "could not translate host name 'db' to address"

## الحل

### 1. تأكد من أن DATABASE_URL صحيح

في `docker-compose.yml`، تأكد من أن `DATABASE_URL` يستخدم اسم الخدمة `db`:

```yaml
environment:
  DATABASE_URL: postgresql://postgres:postgres@db:5432/mared_bot
```

### 2. تحقق من ملف .env

إذا كان ملف `.env` يحتوي على `DATABASE_URL` مختلف (مثل `localhost`)، قم بتعليقه أو حذفه:

```env
# DATABASE_URL=postgresql://postgres:postgres@localhost:5432/mared_bot  # ❌ خطأ
# DATABASE_URL في docker-compose.yml سيتم استخدامه ✅
```

### 3. إعادة بناء وتشغيل الخدمات

```bash
docker-compose down
docker-compose build web
docker-compose up -d
```

### 4. التحقق من الاتصال

```bash
# تحقق من أن الخدمات تعمل
docker-compose ps

# تحقق من السجلات
docker-compose logs web | grep -i database
docker-compose logs db

# اختبار الاتصال من داخل container الويب
docker-compose exec web ping db
```

### 5. إذا استمرت المشكلة

#### أ. تحقق من الشبكة Docker:
```bash
docker network ls
docker network inspect <network_name>
```

#### ب. تأكد من أن جميع الخدمات على نفس الشبكة:
Docker Compose ينشئ شبكة افتراضية تلقائياً. لا حاجة لتحديد `networks` يدوياً.

#### ج. تحقق من أن `depends_on` يعمل:
```yaml
depends_on:
  db:
    condition: service_healthy
```

#### د. أضف retry logic في الكود:
تم إضافة `startup_check.py` الذي يتحقق من الاتصال قبل بدء الخادم.

## ملاحظات

- `DATABASE_URL` في `environment` في docker-compose.yml يتجاوز القيمة في `.env`
- اسم الخدمة `db` يجب أن يكون مطابقاً لاسم الخدمة في docker-compose.yml
- تأكد من أن خدمة `db` تعمل وتكون `healthy` قبل بدء خدمة `web`

