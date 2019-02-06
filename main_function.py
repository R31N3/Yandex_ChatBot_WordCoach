# coding: utf-8
from __future__ import unicode_literals
import random
import json
from ans import *

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


def map_answer(myAns, withAccent=False):
    if withAccent:
        return myAns.replace(".", "").replace(";", "").strip()
    return myAns.replace(".", "").replace(";", "").replace("+", "").strip()

def update_handler(handler, database, request):
    database.update_entries('users_info', request.user_id, {'handler': handler}, update_type='rewrite')


def IDontUnderstand(response, user_storage, buttons = ""):
    message = random.choice(aliceAnswers["cantTranslate"])
    response.set_text(message)
    response.set_tts(message)
    buttons, user_storage = get_suggests(user_storage)
    response.set_buttons(buttons)
    return response, user_storage

# Ну вот эта функция всем функциям функция, ага. Замена постоянному формированию ответа, ага, экономит 4 строчки!!
def message_return(response, user_storage, message, button, database, request, handler, flag=False):
    # ща будет магия
    update_handler(handler, database, request)
    response.set_text(message)
    response.set_tts(message)
    buttons, user_storage = get_suggests(user_storage)
    response.set_buttons(button)
    return response, user_storage


def handle_dialog(request, response, user_storage, database):
    if not user_storage:
        user_storage = {"suggests" : []}
    input_message = request.command.lower()

    # первый запуск/перезапуск диалога
    if request.is_new_session or not database.get_entry("users_info",  ['Named'], {'request_id': request.user_id})[0][0]:
        if request.is_new_session and (database.get_entry("users_info", ['Name'],
                                                          {'request_id': request.user_id}) == 'null'
                                       or not database.get_entry("users_info", ['Name'], {'request_id': request.user_id})):
            output_message = "Тебя приветствует #Навзание#, благодаря мне ты сможешь потренироваться в знании" \
                             " английского, а также ты можешь использовать меня в качестве словаря со своими" \
                             " собственными формулировками и ассоциациями для простого запоминания!"
            response.set_text(output_message)
            response.set_tts(output_message)
            database.add_entries("users_info", {"request_id": request.user_id})
            handler = "-2"
            update_handler(handler, database, request)
            return response, user_storage
        handler = database.get_entry("users_info", ['handler'], {'request_id': request.user_id})[0][0]
        if handler == "-2":
            database.update_entries('users_info', request.user_id, {'Named': True}, update_type='rewrite')
            user_storage["name"] = request.command
            database.update_entries('users_info', request.user_id, {'Name': input_message}, update_type='rewrite')

        user_storage['suggests'] = [
            "Выведи имя",
            "Помощь, но она тут от старого навыка, да."
        ]

        output_message = random.choice(aliceAnswers["helloTextVariations"]).capitalize()+" Доступные разделы: " \
                     + ", ".join(user_storage['suggests'])
        handler = "-1"
        buttons, user_storage = get_suggests(user_storage)
        return message_return(response, user_storage, output_message, buttons, database, request, handler, True)

    handler = database.get_entry("users_info", ['handler'], {'request_id': request.user_id})[0][0]
    answer = classify(input_message, handler)
    handle = answer['class']
    warning = answer['warning']
    answer = answer['answer']
    if handle == "add":
        words = database.get_entry("users_info", ['handler'], {'request_id': request.user_id})[0][0] \
                + answer[0] + "#$"
        translates = database.get_entry("users_info", ['handler'], {'request_id': request.user_id})[0][0]\
                + answer[1] + "#$"
        database.update_entries('users_info', request.user_id, {'words': words}, update_type='rewrite')
        database.update_entries('users_info', request.user_id, {'translates': translates}, update_type='rewrite')
        output_message = "Слово {} добавлено с переводом {}. \n {}".format(answer[0], answer[1],
                                database.get_entry("users_info", ['handler'], {'request_id': request.user_id})[0][0],
                                database.get_entry("users_info", ['handler'], {'request_id': request.user_id})[0][0])
        buttons, user_storage = get_suggests(user_storage)
        return message_return(response, user_storage, output_message, buttons, database, request,
                              handler)

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
                              handler)

    if handler.endswith("-1"):
        if input_message == "Выведи имя" or input_message == "Имя":
            output_message = "Имя пользователя: {}".format(database.get_entry("users_info", ['Name'],
                                                                              {'request_id': request.user_id})[0][0])
            buttons, user_storage = get_suggests(user_storage)
            return message_return(response, user_storage, output_message, buttons, database, request,
                                  handler)

    update_handler(handler, database, request)

    if input_message in ['нет', 'не хочется', 'в следующий раз', 'выход', "не хочу", 'выйти']:
        choice = random.choice(aliceAnswers["quitTextVariations"])
        response.set_text(choice)
        response.set_tts(choice,True)
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
