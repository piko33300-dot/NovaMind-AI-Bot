# NovaMind AI Bot

NovaMind AI هو بوت Telegram عربي يعمل على مدار الساعة، ويجمع خدمات الذكاء الاصطناعي في مكان واحد مع نظام رصيد مجاني، إحالات، وإدارة مشرفين. المشروع مصمم للنشر على Railway مع PostgreSQL، مع طبقة مزودات منفصلة حتى يمكن تغيير المصدر لاحقًا.

## ماذا يتضمن المشروع

- واجهة Telegram عربية
- تسجيل المستخدم تلقائيًا عند أول استخدام
- رصيد مجاني يومي قابل للتعديل
- تكلفة خدمات قابلة للتغيير
- نظام إحالات ومكافآت
- لوحة إدارة للمشرفين فقط
- طبقة مزودات مستقلة
- إعدادات تشغيل عبر متغيرات البيئة
- دعم PostgreSQL على Railway

## هيكل المشروع

```text
NovaMind-AI-Bot/
├── app/
│   ├── __init__.py
│   ├── config.py
│   ├── database.py
│   ├── models.py
│   ├── service_layer.py
│   ├── providers.py
│   ├── main.py
│   └── bot/
│       ├── __init__.py
│       ├── keyboards.py
│       └── handlers.py
├── tests/
│   └── test_core.py
├── .env.example
├── .gitignore
├── Procfile
├── pytest.ini
├── requirements.txt
├── README.md
```

## إعداد البيئة

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

## متغيرات البيئة

```env
TELEGRAM_BOT_TOKEN=your_bot_token
ADMIN_TG_IDS=123456789,987654321
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/novamind
OPENAI_API_KEY=
STABILITY_API_KEY=
REMOVE_BG_API_KEY=
ELEVENLABS_API_KEY=
FREE_DAILY_CREDIT=25
INITIAL_BALANCE=100
REFERRAL_BONUS=50
REFERRAL_THRESHOLD=1
WEBHOOK_URL=
WEBHOOK_PATH=/webhook
```

## التشغيل المحلي

```bash
python -m app.main
```

إذا لم يتم تعيين `TELEGRAM_BOT_TOKEN`، ستتوقف العملية مع رسالة واضحة.

## النشر على Railway

1. أنشئ مشروعًا جديدًا على Railway.
2. اربط مستودع GitHub `NovaMind-AI-Bot`.
3. أضف خدمة Web.
4. أضف قاعدة بيانات PostgreSQL.
5. أضف متغيرات البيئة السابقة.
6. استخدم الأمر التالي:

```bash
python -m app.main
```

7. أنشئ البوت عبر BotFather.
8. ضع التوكن في `TELEGRAM_BOT_TOKEN`.
9. أعد تشغيل الخدمة.

## أوامر الإدارة

الأوامر الآتية مخصصة للمشرفين فقط:

- `/admin`
- `/admin_stats`
- `/set_daily_credit 25`
- `/set_service_cost image_generation 10`
- `/toggle_service image_generation off`
- `/broadcast رسالة عامة`
- `/ban 123456789`
- `/unban 123456789`

## نظام الرصيد والإحالات

- كل مستخدم جديد يحصل على رصيد أولي.
- يتم تجديد الرصيد المجاني يوميًا وفق `FREE_DAILY_CREDIT`.
- تُخصم الخدمات من الرصيد المجاني أولاً ثم من الرصيد الأساسي.
- لا يُسمح بتكرار مكافأة الإحالة لنفس المستخدم.
- تُسجل كل العمليات في قاعدة البيانات.

## الخدمات

### الخدمات التي تم توضيحها كهيكل

- توليد الصور
- الكتابة والذكاء الاصطناعي
- التلخيص
- الترجمة
- تحويل النص إلى صوت
- إنشاء الفيديو
- إزالة الخلفية

### الخدمات التي تحتاج مفاتيح API حقيقية

- OpenAI API
- Remove.bg
- Stability AI
- ElevenLabs

إذا لم تتوفر مفاتيح API، سيظهر للمستخدم رسالة واضحة بدلًا من الادعاء بأن الخدمة جاهزة.

## الاختبارات

```bash
pytest -q
```

الاختبارات الأساسية تغطي:

- تسجيل المستخدم
- رصيد اليومي
- الإحالات
- منع الرصيد المنخفض
- صلاحية المشرف
- فشل الخدمات عند عدم توفر API

## ملاحظات الأمان

- لا يتم تخزين أي مفتاح سري داخل GitHub أو السجلات.
- جميع القيم الحساسة تُمرر عبر متغيرات البيئة.
- لا يُعرض المفتاح في الرسائل أو أثناء التشغيل.

## طريقة تغيير اسم البوت ورسائمه

- استخدم BotFather لتغيير اسم البوت.
- تعديل الرسائل داخل `app/bot/handlers.py`.
- تعديل أزرار القائمة داخل `app/bot/keyboards.py`.
- تعديل قائمة المشرفين عبر `ADMIN_TG_IDS`.

## التحديات الحالية

- لا يمكن اختبار الخدمات الخارجية فعليًا بدون مفاتيح API حقيقية.
- هذا المشروع جاهز للبنية الأساسية والتطوير، لكنه يحتاج إعدادات حقيقية في بيئة الإنتاج لتفعيل الخدمات الفعلية.
