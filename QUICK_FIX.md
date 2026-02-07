# إصلاح سريع لمشكلة Port 5432 في Dokploy

## المشكلة
```
Error: Bind for 127.0.0.1:5432 failed: port is already allocated
```

## الحل السريع

### الخيار 1: استخدام ملف docker-compose.dokploy.yml

في Dokploy:
1. اذهب إلى إعدادات المشروع
2. اختر "Custom Docker Compose File"
3. أدخل: `docker-compose.dokploy.yml`

### الخيار 2: تعديل docker-compose.yml مباشرة

استبدل `docker-compose.yml` بالمحتوى التالي:

```yaml
version: '3.8'

services:
  db:
    image: postgres:16-alpine
    container_name: mared_bot_db
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: mared_bot
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5
    # لا تعريض منفذ - الاتصال عبر الشبكة الداخلية فقط
    networks:
      - default

  bot:
    build: .
    container_name: mared_bot
    depends_on:
      db:
        condition: service_healthy
    environment:
      DATABASE_URL: postgresql://postgres:postgres@db:5432/mared_bot
    env_file:
      - .env
    volumes:
      - .:/app
    restart: unless-stopped
    command: sh -c "python -m alembic upgrade head && python -m bot.main"
    networks:
      - default

volumes:
  postgres_data:

networks:
  default:
    driver: bridge
```

**المفتاح**: لا يوجد `ports:` في خدمة `db` - هذا يمنع تعريض المنفذ للخارج ويحل مشكلة التعارض.

### الخيار 3: استخدام قاعدة بيانات Dokploy الخارجية

إذا كان Dokploy يوفر قاعدة بيانات منفصلة:

1. أنشئ قاعدة بيانات PostgreSQL في Dokploy
2. احصل على connection string
3. حدّث `.env`:
   ```env
   DATABASE_URL=postgresql://user:pass@host:5432/dbname
   ```
4. استخدم `docker-compose.yml` بدون خدمة `db`:
   ```yaml
   version: '3.8'
   
   services:
     bot:
       build: .
       container_name: mared_bot
       environment:
         DATABASE_URL: ${DATABASE_URL}
       env_file:
         - .env
       restart: unless-stopped
       command: sh -c "python -m alembic upgrade head && python -m bot.main"
   ```

## بعد الإصلاح

1. احذف الـ containers القديمة في Dokploy
2. أعد النشر
3. تحقق من السجلات

