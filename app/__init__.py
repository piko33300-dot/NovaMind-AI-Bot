# NovaMind AI Bot

NovaMind AI هو بوت Telegram عربي يعمل على مدار الساعة، ويجمع خدمات الذكاء الاصطناعي في واجهة موحدة مع نظام رصيد مجاني، إحالات، وإدارة مشرفين. المشروع مصمم للنشر على Railway مع PostgreSQL، ويعتمد على هيكل خدمات منفصل حتى يمكن تبديل المزود لاحقًا.

## أبرز المميزات

- واجهة Telegram عربية
- تسجيل مستخدم تلقائي عند أول استخدام
- رصيد مجاني يومي قابل للتعديل
- نظام إحالة ومكافآت
- لوحة إدارة للمشرفين فقط
- خدمة AI قابلة للتوسيع
- إعدادات خارجية عبر متغيرات البيئة
- دعم PostgreSQL على Railway
- قراءة/كتابة آمنة عبر SQLAlchemy Async

## هيكل المشروع

```text
NovaMind-AI-Bot/
├── app/
│   ├── __init__.py
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
└── .python-version
```

## المتطلبات

- Python 3.11+
- PostgreSQL (محلي أو على Railway)
- BotFather لإنشاء التوكن
- مفاتيح API للـ AI عند تفعيل الخدمات الفعلية

## متغيرات البيئة

انسخ ملف `.env.example` إلى `.env`، ثم عدّل القيم:

```env
TELEGRAM_BOT_TOKEN=your_bot_token
ADMIN_TG_IDS=123456789,987654321
DATABASE_URL=postgresql+asyncpg://user:password@host:5432/novamind
OPENAI_API_KEY=...
STABILITY_API_KEY=...
REMOVE_BG_API_KEY=...
ELEVENLABS_API_KEY=...
FREE_DAILY_CREDIT=25
INITIAL_BALANCE=100
REFERRAL_BONUS=50
REFERRAL_THRESHOLD=1
WEBHOOK_URL=
WEBHOOK_PATH=/webhook
```

## التشغيل المحلي

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python -m app.main
```

## التشغيل على Railway

1. أنشئ مشروع Railway جديدًا.
2. اربط مستودع GitHub `NovaMind-AI-Bot`.
3. أضف خدمة Web.
4. أضف PostgreSQL Database من Railway.
5. أضف متغيرات البيئة من `.env.example`.
6. استخدم الأمر التالي في إعدادات التشغيل:

```bash
python -m app.main
```

7. أنشئ البوت عبر BotFather.
8. أضف التوكن إلى `TELEGRAM_BOT_TOKEN`.
9. أعد تشغيل الخدمة.

## أوامر الإدارة

الأوامر المخصصة للمشرفين فقط:

- `/admin`
- `/admin_stats`
- `/set_daily_credit 25`
- `/set_service_cost image_generation 10`
- `/toggle_service image_generation off`
- `/broadcast نص الإشعار`
- `/ban 123456789`
- `/unban 123456789`

## نظام الرصيد والإحالات

- كل مستخدم جديد يحصل على رصيد أولي.
- يتم تجديد الرصيد المجاني يوميًا وفق قيمة `FREE_DAILY_CREDIT`.
- يتم خصم الخدمة من الرصيد المجاني أولاً ثم من الرصيد الأساسي.
- لا يمكن تكرار المكافأة للإحالة نفسها.
- لا يتم منح المكافأة أكثر من مرة لنفس المستخدم.
- يتم تسجيل العمليات في قاعدة البيانات.

## الخدمات الحالية

### تم تنفيذها فعليًا كهيكل وآلية

- توليد الصور
- الكتابة والذكاء الاصطناعي
- التلخيص
- الترجمة
- تحويل النص إلى صوت
- إنشاء الفيديو
- إزالة الخلفية

### تحتاج إلى مفتاح API حقيقي

- OpenAI API: الكتابة، التلخيص، الترجمة، الصور، الصوت
- Remove.bg: إزالة الخلفية
- Stability AI: إنشاء الفيديو أو تحسين الصور
- ElevenLabs: الصوت المتقدم

إذا لم توجد مفاتيح API، سيظهر للمستخدم رسالة واضحة بدلًا من التظاهر بأن الخدمة تعمل.

## الاختبارات

تمت إضافة اختبارات أساسية ويمكن تشغيلها عبر:

```bash
pytest -q
```

الاختبارات تشمل:

- تسجيل المستخدم
- رصيد اليومي
- الإحالات
- منع الرصيد المنخفض
- التحقق من صلاحية المشرف
- رسائل فشل الخدمة عند عدم وجود API

## ملاحظات مهمة

- لا يتم تخزين أي مفتاح سري داخل الملفات أو السجلات.
- كل إعداد خارجية يمر عبر متغيرات البيئة.
- المجدول الحالي لا يدّعي أن أي خدمة تعمل دون API الفعلية.
- هذا المشروع جاهز للبناء والتطوير، لكنه يحتاج مفاتيح حقيقية في بيئة الإنتاج لتفعيل الخدمات الفعلية.

## طريقة تغيير اسم البوت

- استخدم BotFather لتغيير اسم البوت أو الوصف.
- تعديل الرسائل داخل `app/bot/handlers.py`.
- تعديل أزرار القائمة من `app/bot/keyboards.py`.
- تعديل قائمة المشرفين من `ADMIN_TG_IDS`.

## الترخيص

هذا المشروع مخصص للاستخدام والتطوير الشخصي أو التجاري ضمن الإطار القانوني للمالك/المطور.
