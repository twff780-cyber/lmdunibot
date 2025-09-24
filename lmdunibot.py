import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

# --- إعدادات البوت ---
TOKEN = "8147477964:AAEuL6BP35OH-AJYFy0C5tZ03_bBVygKF-I"

# إعداد تسجيل الأخطاء والمعلومات
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# --- تخزين حالة المستخدم ---
user_modes = {}  # مفتاحه هو user_id وقيمته إما "text" أو "unicode" أو None

# --- دوال التحويل ---

def text_to_unicode(text: str) -> str:
    return '-'.join(f'U+{ord(char):04X}' for char in text)

def unicode_to_text(unicode_string: str) -> str:
    try:
        codes = unicode_string.strip().split('-')
        chars = [chr(int(code.upper().replace('U+', ''), 16)) for code in codes]
        return ''.join(chars)
    except (ValueError, IndexError):
        return "⚠️ صيغة اليونيكود غير صالحة. تأكد أنها مكتوبة بالشكل الصحيح."

# --- أوامر البوت ---

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_modes[update.effective_user.id] = None
    await update.message.reply_text("""
👋 مرحبًا بك!

أرسل /text للدخول في وضع تحويل النص إلى يونيكود.
أرسل /unicode للدخول في وضع تحويل اليونيكود إلى نص.
أرسل /stop للخروج من الوضع الحالي.
""")

async def text_mode_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_modes[update.effective_user.id] = "text"
    await update.message.reply_text("✅ تم تفعيل وضع تحويل النص إلى يونيكود. أرسل أي نص الآن!")

async def unicode_mode_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_modes[update.effective_user.id] = "unicode"
    await update.message.reply_text("✅ تم تفعيل وضع تحويل اليونيكود إلى نص. أرسل الأكواد الآن!")

async def stop_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_modes[update.effective_user.id] = None
    await update.message.reply_text("🛑 تم إيقاف الوضع النشط. أرسل أمرًا جديدًا للبدء.")

# --- التعامل مع الرسائل العادية ---

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    mode = user_modes.get(user_id)

    if mode == "text":
        result = text_to_unicode(update.message.text)
        await update.message.reply_text(result)
    elif mode == "unicode":
        result = unicode_to_text(update.message.text)
        await update.message.reply_text(result)
    else:
        await update.message.reply_text("❓ لم يتم تفعيل أي وضع. أرسل /text أو /unicode للبدء.")

# --- تشغيل البوت ---
def main():
    print("✅ البوت قيد التشغيل...")

    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("text", text_mode_command))
    application.add_handler(CommandHandler("unicode", unicode_mode_command))
    application.add_handler(CommandHandler("stop", stop_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    application.run_polling()

if __name__ == '__main__':
    main()