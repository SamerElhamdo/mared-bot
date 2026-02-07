# إصلاح مشكلة Dokploy - Port Already Allocated

## المشكلة

```
Error: Bind for 127.0.0.1:5432 failed: port is already allocated
```

هذا الخطأ يحدث لأن المنفذ 5432 (PostgreSQL) مستخدم بالفعل على السيرفر.

## الحلول

### الحل 1: استخدام docker-compose.dokploy.yml (موصى به)

في Dokploy، استخدم ملف `docker-compose.dokploy.yml` بدلاً من `docker-compose.yml`:

1. في إعدادات المشروع في Dokploy:
   - اختر "Custom Docker Compose File"
   - حدد `docker-compose.dokploy.yml`

2. أو قم بتغيير اسم الملف:
   ```bash
   mv docker-compose.yml docker-compose.local.yml
   mv docker-compose.dokploy.yml docker-compose.yml
   ```

### الحل 2: استخدام قاعدة بيانات خارجية

إذا كان Dokploy يوفر قاعدة بيانات PostgreSQL منفصلة:

1. في Dokploy، أنشئ قاعدة بيانات PostgreSQL جديدة
2. احصل على connection string
3. حدّث `.env`:
   ```env
   DATABASE_URL=postgresql://user:password@external-db-host:5432/mared_bot
   ```
4. حدّث `docker-compose.yml` لإزالة خدمة `db`:
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
       volumes:
         - .:/app
       restart: unless-stopped
       command: sh -c "python -m alembic upgrade head && python -m bot.main"
   ```

### الحل 3: تغيير المنفذ (إذا كنت تحتاج الوصول من الخارج)

إذا كنت تحتاج الوصول إلى قاعدة البيانات من خارج Docker:

```yaml
services:
  db:
    # ... other config ...
    ports:
      - "5433:5432"  # استخدام منفذ مختلف
```

ثم حدّث `DATABASE_URL` إذا كنت تصل من خارج Docker:
```env
DATABASE_URL=postgresql://postgres:postgres@db:5432/mared_bot  # داخل Docker
# أو
DATABASE_URL=postgresql://postgres:postgres@localhost:5433/mared_bot  # من خارج Docker
```

### الحل 4: إيقاف PostgreSQL المحلي (إذا كان موجود)

إذا كان PostgreSQL يعمل محلياً على السيرفر:

```bash
# Ubuntu/Debian
sudo systemctl stop postgresql
sudo systemctl disable postgresql

# أو
sudo service postgresql stop
```

## التحقق من المنفذ المستخدم

```bash
# تحقق من المنفذ 5432
sudo lsof -i :5432
# أو
sudo netstat -tulpn | grep 5432
```

## بعد الإصلاح

1. أعد تشغيل المشروع في Dokploy
2. تحقق من السجلات:
   ```bash
   docker-compose logs bot
   docker-compose logs db
   ```
3. تأكد من أن قاعدة البيانات تعمل:
   ```bash
   docker-compose exec db psql -U postgres -d mared_bot -c "SELECT 1;"
   ```

## ملاحظات مهمة

- **لا تحتاج** إلى تعريض منفذ قاعدة البيانات للخارج إذا كانت الخدمات في نفس Docker network
- استخدام `expose` بدلاً من `ports` يسمح بالاتصال الداخلي فقط
- Dokploy عادة يوفر قاعدة بيانات منفصلة - استخدمها إذا كانت متاحة

