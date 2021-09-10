import requests
import json
from config import keys



class Error(Exception):
    pass

class FormatError(Error):
    pass

class APIError(Error):
    pass

class CalculateFXRates():
    @staticmethod
    def converter(message):
        command = message.text.split()
        if len(command) != 3:
            raise FormatError("Неверное число параметров. Нужно 3 параметра через пробел")
        # русский человек введет число с десятичной запятой, а питону нужно, чтобы
        # разряд отмечался точкой, поэтому меняю в числе запятую на точку, если она там есть
        command[0] = command[0].replace(",", ".")
        try:
            amount = float(command[0])
        except:
            raise FormatError("Неверный тип данных. Сумма для конвертации должна быть числом")
        # валюта 1 — откуда конвертировать, валюта 2 — куда
        currency_1, currency_2 = command[1], command[2]
        # проверяем, что человек прислал сообщение на русском и
        # переводим русский язык в приемлемый формат с помощью словаря выше
        if currency_1 in keys:
            currency_1 = keys[currency_1]
        if currency_2 in keys:
            currency_2 = keys[currency_2]
        # проверяем, что такие валюты есть в словаре с валютами, который получен по API
        allowed_cur = CalculateFXRates.get_FX_rates()["rates"]
        if currency_1 not in allowed_cur or currency_2 not in allowed_cur:
            raise FormatError("Такая валюта не поддерживается")
        # вызываем фунцию для конвертации и умножаем ее результат на
        # сумму, которую просил пользователь
        res = round(amount * CalculateFXRates.convert(currency_1, currency_2), 2)
        res = f"Стоимость {amount} {currency_1} составляет {res} {currency_2} "
        return res
        # отвечаем на сообщение пользователя актуальным курсом валют

    #получаем по API курсы валют и преобразуем ответ в словарь
    @staticmethod
    def get_FX_rates():
        r = requests.get("http://api.exchangeratesapi.io/v1/latest?access_key=f81884514bc6951ad295b9b7688dddce")
        FX_dictionary = json.loads(r.content)
        #API дает ответ в виде словаря. По ключу "success" приходит True, если всё ок, и False, если
        #что-то пошло не так. В последнем случае по ключам "code" и "info" можно вытащить из
        # запроса код и подробное описание ошибки. Чтобы не надо было лезть в документацию,
        #выводим информацию об ошибках API в консоль
        if not FX_dictionary["success"]:
            raise APIError(f"API request failed with code {FX_dictionary['code']} because {FX_dictionary['info']}")
        return FX_dictionary
#конвертируем одну валюту в другую
    @staticmethod
    def convert(currency_1, currency_2):
        FX_dictionary = CalculateFXRates.get_FX_rates()
        # по API приходит словарь, по ключу "rates" в нем другой словарь с названиями
        #валют и их курсом к евро. Берем валюты, которые переданы в функцию
        #и считаем их курс к евро по очереди
        EUR_to_currency_1 = FX_dictionary["rates"][currency_1]
        EUR_to_currency_2 = FX_dictionary["rates"][currency_2]
        #возвращаем курс валюты 1 к валюте 2
        return EUR_to_currency_2/EUR_to_currency_1
