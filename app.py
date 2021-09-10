import telebot
from utils import CalculateFXRates, FormatError, APIError
from config import TOKEN

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=["start", "help"])
def help(message: telebot.types.Message):
    text = """Бот конвертирует евро, доллары и рубли друг в друга
    формат сообщения: <сумма> <из валюты> <в валюту>
    пример: 19 долларов рубли
    помощь: /help
    все валюты: /iwantmore"""

    bot.reply_to(message, text)

#можно спросить у бота весь список доступных валют
#в словаре, который присылает API, куча валют. Код универсальный и может конвертировать
# любую валюту в любую валюту (а еще в золото, серебро и еще что-то там).
# При желании можно дополнить словарь выше
#и принимать любые валюты на русском языке, но я этого не стал делать.
# Однако уже можно спросить у бота 100 RUB XAU и узнать,
# сколько золота можно купить на 100 рублей (крайне мало), чтобы узнать,
# какие доступны валюты нужно отдать команду /iwantmore
@bot.message_handler(commands=["iwantmore"])
def all_currencies(message: telebot.types.Message):
    text = "Available currencies"
    #просто распечатывает все ключи из словаря с валютами, полученного по API
    for key in CalculateFXRates.get_FX_rates()["rates"]:
        text = ", ".join((text, key))
    bot.reply_to(message, text)

@bot.message_handler(func=lambda message: True)
def say_rate(message: telebot.types.Message):
    try:
        text = CalculateFXRates.converter(message)
    except APIError as e:
        bot.reply_to(message, f"Ошибка API\n {e}")
    except FormatError as e:
        bot.reply_to(message, f"Неверный формат\n{e}")
    except Exception as e:
        bot.reply_to(message, f"Не удалось обработать команду\n{e}")
    else:
        bot.reply_to(message, text)

bot.polling()