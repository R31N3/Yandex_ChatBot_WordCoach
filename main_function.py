# coding: utf-8
from __future__ import unicode_literals
import random
import json

Named = False


def find_difference(lst1, lst2):  # i = item
    return [i for i in lst1 if i not in lst2]


def read_data():
    with open("words.json", encoding="utf-8") as file:
        data = json.loads(file.read())
        return data


def read_answers_data(name):
    with open(name+".json", encoding="utf-8") as file:
        data = json.loads(file.read())
        return data


aliceAnswers = read_answers_data("data/answers_dict_example")


def aliceSpeakMap(myAns, withAccent=False):
    if withAccent:
        return myAns.strip()
    return myAns.replace("+", "").strip()


def map_answer(myAns, withAccent=False):
    if withAccent:
        return myAns.replace(".", "").replace(";", "").strip()
    return myAns.replace(".", "").replace(";", "").replace("+", "").strip()

def update_handler(handler, database, request):
    database.update_entries('users_info', request.user_id, {'handler': handler}, update_type='rewrite')
    

def IDontUnderstand(response, user_storage, buttons = ""):
    message = random.choice(aliceAnswers["cantTranslate"])
    response.set_text(aliceSpeakMap(message))
    response.set_tts(aliceSpeakMap(message, True))
    buttons, user_storage = get_suggests(user_storage)
    response.set_buttons(buttons)
    return response, user_storage

# Ну вот эта функция всем функциям функция, ага. Замена постоянному формированию ответа, ага, экономит 4 строчки!!
def message_return(response, user_storage, message, button, database, request, handler, warning, congrats, flag=False):
    # ща будет магия
    update_handler(handler, database, request)
    if warning:
        message = warning+ message
    text_message = message.split("Доступные")[0]
    if flag:
        response.set_text(aliceSpeakMap(text_message))
        response.set_tts(aliceSpeakMap(message, True))
    else:
        response.set_text(text_message)
        response.set_tts(message)
    buttons, user_storage = get_suggests(user_storage)
    response.set_buttons(button)
    return response, user_storage


def handle_dialog(request, response, user_storage, database):
    # request.command - сообщение от пользователя
    warning_message = ""
    congrats = ""
    user_storage = user_storage
    if not user_storage:
        user_storage = {"suggests" : []}
    input_message = request.command.lower().strip("?!.")

    # первый запуск/перезапуск диалога
    if request.is_new_session or not database.get_entry("users_info",  ['Named'], {'request_id': request.user_id})[0][0]:
        if request.is_new_session and (database.get_entry("users_info", ['Name'],
                                                          {'request_id': request.user_id}) == 'null'
                                       or not database.get_entry("users_info", ['Name'], {'request_id': request.user_id})):
            output_message = "Тебя приветствует #Навзание#, благодаря мне ты сможешь потренироваться в знании" \
                             " английского, а также ты можешь использовать меня в качестве словаря со своими" \
                             " собственными формулировками и ассоциациями для простого запоминания!"
            response.set_text(aliceSpeakMap(output_message))
            response.set_tts(aliceSpeakMap(output_message))
            database.add_entries("users_info", {"request_id": request.user_id})
            handler = "asking name"
            update_handler(handler, database, request)
            return response, user_storage
        handler = database.get_entry("users_info", ['handler'], {'request_id': request.user_id})[0][0]
        if handler == "asking name":
            database.update_entries('users_info', request.user_id, {'Named': True}, update_type='rewrite')
            user_storage["name"] = request.command
            database.update_entries('users_info', request.user_id, {'Name': input_message}, update_type='rewrite')

        user_storage['suggests'] = [
            "Дальше я ничего не придумал",
            "Помощь, но она тут от старого навыка, да."
        ]

        Named = database.get_entry("users_info", ['Named'], {'request_id': request.user_id})[0][0]

        if not Named:
            output_message = random.choice(aliceAnswers["helloTextVariations"]).capitalize()+" Доступные разделы: " \
                     + ", ".join(user_storage['suggests'])
        else:
            output_message = random.choice(aliceAnswers["continueTextVariations"]).capitalize()+" Доступные разделы: " \
                     + ", ".join(user_storage['suggests'])
        handler = "other_next"
        buttons, user_storage = get_suggests(user_storage)
        return message_return(response, user_storage, output_message, buttons, database, request, handler, warning_message, congrats, True)

    handler = database.get_entry("users_info", ['handler'], {'request_id': request.user_id})[0][0]

    if "помощь" in input_message or input_message in "а что ты умеешь":
        output_message = "В данной игре ты пройдешь путь карьерного роста от безработного до" \
                         " главы собственной компании, в то же время на нем тебе придется следить и бороться с самыми" \
                         " злейшими врагами программистов: голодом и плохим настроением! Проживая день за днем, " \
                         "тебе придется питаться и развлекать себя, дабы не умереть от стресса. Перемещайся по разделам," \
                         "выполняй желаемые действия и переходи на следующий день, всё просто! Удачи! Доступные разделы: {}".format(
            "\n".join(user_storage["suggests"])
        )
        buttons, user_storage = get_suggests(user_storage)
        return message_return(response, user_storage, output_message, buttons, database, request,
                              handler, warning_message, congrats)

    if handler.endswith("other_next"):
        print(input_message in "помощь")
        if input_message == "источник дохода" or input_message == "доход":
            handler = "profit_page"
        elif input_message == "образование и курсы" or input_message == "образование" or input_message == "курсы":
            handler = "education_page"
        elif input_message == "основная информация" or input_message == "информация":
            handler = "start_page"

    # Основная стартовая страница с основными данными игрока(основной раздел data)
    if handler.startswith("start_page"):
        # start_page
        if input_message == "назад" and not handler.endswith("job"):
            splitted = handler.split("->")
            if handler.endswith("next"):
                handler = "->".join(splitted[:-3])
            else:
                if len(splitted) > 1:
                    handler = "->".join(splitted[:-2])
                else:
                    handler = "null"
            handler = "null" if not handler else handler

        if handler.endswith("other") or handler == "null":
            user_storage['suggests'] = [
                "Основная информация",
                "Источник дохода",
                "Образование и курсы",
                "Помощь",
                "Следующий день"
            ]

            handler = "other->other_next"

            output_message = "Похоже, мы вернулись в начало.\nДоступные опции: {}".format(
                ", ".join(user_storage['suggests']))

            buttons, user_storage = get_suggests(user_storage)
            return message_return(response, user_storage, output_message, buttons, database, request, handler, warning_message, congrats)

        if handler == "start_page":
            money = database.get_entry("users_info", ['Money'], {'request_id': request.user_id})[0][0]
            exp = database.get_entry("users_info", ['Exp'], {'request_id': request.user_id})[0][0]
            food = database.get_entry("users_info", ['Food'], {'request_id': request.user_id})[0][0]
            mood = database.get_entry("users_info", ['Mood'], {'request_id': request.user_id})[0][0]
            health = database.get_entry("users_info", ['Health'], {'request_id': request.user_id})[0][0]
            date = database.get_entry("users_info", ['Day'], {'request_id': request.user_id})[0][0]

            user_storage['suggests'] = [
                "Восполнение сытости",
                "Восполнение здоровья",
                "Восполнение настроения",
                "Назад",
                "Следующий день"
            ]

            handler += "->start_next"

            output_message = "Ваши деньги: {} \nВаш накопленный опыт: {} \nВаша сытость: {} \nВаше настроение: {}" \
                             " \nВаше здоровье: {} \nДней с начала игры прошло: {} \nДоступные опции: {}"\
                .format(money, exp, food, mood, health, date, ", ".join(user_storage['suggests']))

            buttons, user_storage = get_suggests(user_storage)
            return message_return(response, user_storage, output_message, buttons, database, request, handler, warning_message, congrats)

        # start_page -> start_next
        if handler.endswith("start_next"):
            if input_message == "восполнение сытости" or input_message == "голод" or input_message == "сытость":
                handler += "->food_recharge"
            elif input_message == "восполнение здоровья" or input_message == "здоровье":
                handler += "->health_recharge"
            elif input_message == "восполнение настроения" or input_message == "настроение":
                handler += "->mood_recharge"

        if handler.count("food"):
            # start_page -> start_next -> food_recharge
            if handler.endswith("food_recharge"):
                food = database.get_entry("users_info", ['Food'], {'request_id': request.user_id})[0][0]
                index = database.get_entry("users_info", ['Lvl'], {'request_id': request.user_id})[0][0]
                food_list = read_answers_data("data/start_page_list")["food"][index]
                lst = [i + " - цена {}, восполнение {}".format(food_list[i][0], food_list[i][1]) for i in
                                            food_list.keys()]
                user_storage['suggests'] = [i for i in
                                            food_list.keys()]+["Назад", "Следующий день"]
                handler += "->next"

                output_message = "Ваш голод: {} \nСписок продуктов:\n {}"\
                    .format(food, ",\n".join(lst)
                            + "\n Доступные опции: Назад")

                buttons, user_storage = get_suggests(user_storage)
                return message_return(response, user_storage, output_message, buttons, database, request, handler, warning_message, congrats)

            # start_page -> start_next -> food_recharge -> food_next
            if handler.endswith("next"):
                food = database.get_entry("users_info", ['Food'], {'request_id': request.user_id})[0][0]
                if food != 100:
                    index = database.get_entry("users_info", ['Lvl'], {'request_id': request.user_id})[0][0]
                    money = database.get_entry("users_info", ['Money'], {'request_id': request.user_id})[0][0]
                    product = ""
                    product_price = 0
                    product_weight = 0
                    food_list = read_answers_data("data/start_page_list")["food"][index]
                    for i in food_list.keys():
                        if i.lower().startswith(input_message):
                            product = i
                            product_price = food_list[i][0]
                            product_weight = food_list[i][1]

                    if product:
                        if money - int(int(product_price)) >= 0:
                            food = food + int(product_weight) if (food + int(product_weight)) % 100 and (food + int(product_weight))\
                                                            < 100  else 100
                            database.update_entries('users_info', request.user_id, {'Food': food},
                                                    update_type='rewrite')
                            database.update_entries('users_info', request.user_id, {'Money': money - int(int(product_price))},
                                                    update_type='rewrite')
                            output_message = "Продукт {} успешно преобретен.\nВаша сытость: {} \n Ваши финансы: {} \n Список продуктов: \n{}"\
                                .format(product, food, money - int(product_price), ",\n".join(user_storage['suggests'][:-1]) + "\n Доступные команды: Назад, Следующий день")
                        else:
                            output_message = "Продукт {} нельзя преобрести, не хватает денег: {} \nВаша сытость: {} \n Ваши финансы: {} \n Список продуктов: \n{} "\
                                .format(product, int(product_price) - money, food, money, ",\n".join(user_storage['suggests'][:-1]) + "\n Доступные команды: Назад, Следующий день")
                    else:
                        output_message = "Продукт {} не найден, повторите запрос \n Ваша сытость: {} \n Ваши финансы: {}".format(input_message, food, money)
                else:
                    output_message = "Вы не голодны. \n  Список продуктов: \n {} \nДоступные команды: Назад, Следующий день".format(
                        ",\n".join(user_storage['suggests'][:-1])
                    )

                buttons, user_storage = get_suggests(user_storage)
                return message_return(response, user_storage, output_message, buttons, database, request, handler, warning_message, congrats)

    update_handler(handler, database, request)

    if input_message in ['нет', 'не хочется', 'в следующий раз', 'выход', "не хочу", 'выйти']:
        choice = random.choice(aliceAnswers["quitTextVariations"])
        response.set_text(aliceSpeakMap(choice))
        response.set_tts(aliceSpeakMap(choice,True))
        response.end_session = True
        return response, user_storage

    buttons, user_storage = get_suggests(user_storage)
    return IDontUnderstand(response, user_storage)


def get_suggests(user_storage):
    if "suggests" in user_storage.keys():
        suggests = [
            {'title': suggest, 'hide': True}
            for suggest in user_storage['suggests']
        ]
    else:
        suggests = []

    return suggests, user_storage
