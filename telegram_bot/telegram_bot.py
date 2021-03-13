import logging
import os
import tempfile

from telegram.ext import Updater, CommandHandler, CallbackContext, MessageHandler
from telegram.ext.filters import Filters
from telegram.update import Update

from cloudmersive_image import ImageProcessor

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
HEROKU_APP_URL = 'https://image-description-telegram-bot.herokuapp.com/'


class TelegramBot:
    """Class to initialize and startup bot"""

    def __init__(self):
        self.updater = Updater(TELEGRAM_TOKEN)
        self.dp = self.updater.dispatcher

        self.init_handlers()

        self.port = int(os.environ.get('TELEGRAM_WEBHOOK_PORT', 5000))

    def init_handlers(self):
        """Initialize chat message handlers"""
        self.dp.add_handler(CommandHandler('hello', TelegramBotCallback.answer_hello))
        self.dp.add_handler(MessageHandler(Filters.photo, TelegramBotCallback.describe_photo))
        self.dp.add_error_handler(TelegramBotCallback.log_error)

    def startup(self):
        self.updater.start_webhook(listen='0.0.0.0', port=self.port, url_path=TELEGRAM_TOKEN)
        self.updater.bot.setWebhook(HEROKU_APP_URL + TELEGRAM_TOKEN)
        self.updater.idle()


class TelegramBotCallback:
    @staticmethod
    def start(update: Update, context: CallbackContext):
        """Answers to /start with general info about chat bot"""
        update.message.reply_text('Hello! This is what I can do for you:'
                                  '  - /start — show this text'
                                  '  - message with image — description in English')

    @staticmethod
    def answer_hello(update: Update, context: CallbackContext):
        """Answers to /hello command in chat. Vocative can be specified as an additional space separated parameter:
        /hello {vocative}

        In: /hello World
        Out: Hello, World!
        """
        if context.args:
            name = ' '.join(context.args)
            update.message.reply_text(f'Hello, {name}!')
        else:
            update.message.reply_text('Hello!')

    @staticmethod
    def describe_photo(update: Update, context: CallbackContext):
        """Answer to image in chat with its description in English"""

        bot = context.bot
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

        update.message.reply_text(msg)

    @staticmethod
    def log_error(update, context):
        """Log Errors caused by Updates."""
        logger.warning(f'Update "{update}" caused error "{context.error}"')


if __name__ == '__main__':
    tb = TelegramBot()
    tb.startup()
