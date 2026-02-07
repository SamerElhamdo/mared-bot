# إصلاح مشكلة Network في Dokploy

## المشكلة
```
Error: container is not connected to the network tele-mared-bot-t1blvw_default
```

## السبب
هذا يحدث عندما:
1. Docker Compose يحاول إعادة استخدام container قديم
2. Container قديم غير متصل بالشبكة الجديدة
3. تعريف الشبكة في docker-compose.yml يسبب تعارض

## الحل

### الحل 1: إزالة تعريف الشبكة الصريح (موصى به)

تم تحديث `docker-compose.yml` و `docker-compose.dokploy.yml` لإزالة تعريف `networks` الصريح. Docker Compose سينشئ شبكة افتراضية تلقائياً.

**استخدم الملفات المحدثة:**
- `docker-compose.yml` - بدون networks
- `docker-compose.dokploy.yml` - بدون networks

### الحل 2: حذف Containers القديمة في Dokploy

في Dokploy:
1. اذهب إلى المشروع
2. احذف جميع الـ containers القديمة
3. احذف الـ volumes القديمة (إذا لزم الأمر)
4. أعد النشر

### الحل 3: استخدام أوامر Docker مباشرة

إذا كان Dokploy يسمح بالوصول إلى السيرفر:

```bash
# حذف containers القديمة
docker rm -f mared_bot mared_bot_db

# حذف الشبكات القديمة
docker network prune -f

# إعادة النشر
docker-compose up -d --force-recreate
```

### الحل 4: إضافة restart policy

تم إضافة `restart: unless-stopped` في docker-compose.yml.

## التحقق من الإصلاح

بعد النشر، تحقق من:

```bash
# التحقق من الـ containers
docker ps

# التحقق من الشبكة
docker network ls

# التحقق من الاتصال
docker exec mared_bot ping -c 2 db
```

## ملاحظات مهمة

1. **لا تحتاج** إلى تعريف `networks` صراحة - Docker Compose ينشئها تلقائياً
2. **لا تحتاج** إلى `expose` - الاتصال الداخلي يعمل تلقائياً
3. **استخدم** `depends_on` لضمان ترتيب البدء الصحيح

## الملفات المحدثة

- ✅ `docker-compose.yml` - بدون networks
- ✅ `docker-compose.dokploy.yml` - بدون networks

## الخطوات التالية

1. احذف المشروع القديم في Dokploy (أو احذف containers فقط)
2. أعد النشر باستخدام الملفات المحدثة
3. تحقق من السجلات

