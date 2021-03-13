import tempfile

from telegram.ext import Updater, CommandHandler, CallbackContext, MessageHandler
from telegram.ext.filters import Filters
from telegram.update import Update

from cloudmersive_image import ImageProcessor

TELEGRAM_TOKEN_FILE = '../src/telegram_bot_access_token'


class TelegramBot:
    """Class to initialize and startup bot"""

    def __init__(self):
        with open(TELEGRAM_TOKEN_FILE) as tf:
            token = tf.read().strip()

        self.updater = Updater(token)
        self.dp = self.updater.dispatcher

        self.init_handlers()

    def init_handlers(self):
        """Initialize chat message handlers"""
        self.dp.add_handler(CommandHandler('hello', TelegramBotCallback.answer_hello))
        self.dp.add_handler(MessageHandler(Filters.photo, TelegramBotCallback.describe_photo))

    def startup(self):
        self.updater.start_polling()
        self.updater.idle()


class TelegramBotCallback:
    @staticmethod
    def answer_hello(update: Update, callback: CallbackContext):
        """Answers to /hello command in chat. Vocative can be specified as an additional space separated parameter:
        /hello {vocative}

        In: /hello World
        Out: Hello, World!
        """
        bot = callback.bot
        chat_id = update.message.chat_id
        if callback.args:
            name = ' '.join(callback.args)
            bot.send_message(chat_id=chat_id, text=f'Hello, {name}!')
        else:
            bot.send_message(chat_id=chat_id, text=f'Hello!')

    @staticmethod
    def describe_photo(update: Update, callback: CallbackContext):
        """Answer to image in chat with its description in English"""

        bot = callback.bot
        photo = update.effective_message.photo[-1]  # The last photo is the largest one
        photo_fp = bot.get_file(photo).download(out=tempfile.NamedTemporaryFile())
        photo_path = photo_fp.name

        ip = ImageProcessor()
        photo_desc = ip.recognize_image(photo_path)

        if not photo_desc.successful:
            msg = "Sorry, cannot recognize anything on this image :("
        elif not photo_desc.highconfidence:
            msg = f"I'm not sure about this, but it looks like...\n\n{photo_desc.best_outcome.description}"
        else:
            msg = f"Oh, I know what it is!\n\n{photo_desc.best_outcome.description}"

        bot.send_message(chat_id=update.message.chat_id, text=msg)


if __name__ == '__main__':
    tb = TelegramBot()
    tb.startup()
