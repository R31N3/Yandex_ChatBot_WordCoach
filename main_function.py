# coding: utf-8
from __future__ import unicode_literals
import random
import json
from ans import *
from little_fuctions import *


def read_answers_data(name):
    with open(name+".json", encoding="utf-8") as file:
        data = json.loads(file.read())
        return data


aliceAnswers = read_answers_data("data/answers_dict_example")


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
def message_return(response, user_storage, message, button, database, request, handler):
    # ща будет магия
    update_handler(handler, database, request)
    response.set_text(message)
    response.set_tts(message)
    buttons, user_storage = get_suggests(user_storage)
    response.set_buttons(button)
    return response, user_storage


def handle_dialog(request, response, user_storage, database):
    if not user_storage:
        user_storage = {"suggests": []}
    input_message = request.command.lower()

    # первый запуск/перезапуск диалога
    if request.is_new_session or not database.get_entry("users_info",  ['Named'],
                                                        {'request_id': request.user_id})[0][0]:
        if request.is_new_session and (database.get_entry("users_info", ['Name'],
                                                          {'request_id': request.user_id}) == 'null'or
                                       not database.get_entry("users_info", ['Name'], {'request_id': request.user_id})):
            output_message = "Тебя приветствует Тренер слов, благодаря мне ты сможешь потренироваться в знании" \
                             " английского, а также ты можешь использовать меня в качестве словаря со своими" \
                             " собственными формулировками и ассоциациями для простого запоминания!\n \"" \
                             "Введите ваше имя"
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
            "Помощь",
            "Покажи словарь",
            "Очистить словарь"
        ]

        output_message = random.choice(aliceAnswers["helloTextVariations"]).capitalize()+" Доступные разделы: " + ", "\
            .join(user_storage['suggests'])
        handler = "-1"
        buttons, user_storage = get_suggests(user_storage)
        return message_return(response, user_storage, output_message, buttons, database, request, handler)

    handler = database.get_entry("users_info", ['handler'], {'request_id': request.user_id})[0][0]

    if input_message == 'покажи словарь':
        output_message = envision_dictionary(request.user_id, database)
        buttons, user_storage = get_suggests(user_storage)
        return message_return(response, user_storage, output_message, buttons, database, request,
                              handler)

    if input_message == 'очистить словарь':
        update_dictionary(request.user_id, {'to_learn': {}, 'learned': {}}, database)
        output_message = 'Ваш словарь теперь пустой :)'
        buttons, user_storage = get_suggests(user_storage)
        return message_return(response, user_storage, output_message, buttons, database, request,
                              handler)

    answer = classify(input_message, handler)
    handle = answer['class']
    warning = answer['warning']
    answer = answer['answer']

    if handle == "add":
        success = add_word(answer[0], answer[1], request.user_id, database)
        if language_match(answer[0], answer[1]) == 'miss':
            answer = answer[::-1]
        if success == 'already exists':
            output_message = 'В Вашем словаре уже есть такой перевод'
        elif not success:
            output_message = 'Пара должна состоять из русского и английского слова'
        else:
            output_message = "Слово {} добавлено с переводом {} добавлено в Ваш словарь.".format(answer[0], answer[1])
            update_dictionary(request.user_id, success, database)
        buttons, user_storage = get_suggests(user_storage)
        return message_return(response, user_storage, output_message, buttons, database, request,
                              handler)
    elif handle == 'del':
        success = del_word(answer.strip(), request.user_id, database)
        if success == 'no such word':
            output_message = 'В Вашем словаре нет такого слова'
        elif not success:
            output_message = 'Слово должно быть русским или английским'
        else:
            output_message = 'Слово {} удалено из Вашего словаря'.format(answer)
            update_dictionary(request.user_id, success, database)
        buttons, user_storage = get_suggests(user_storage)
        return message_return(response, user_storage, output_message, buttons, database, request,
                              handler)

    if "помощь" in input_message or input_message in "а что ты умеешь":
        output_message = "Благодаря данному навыку ты можешь запоминать слова так, как тебе хочется! \nДля занесения" \
                         " слова в словарь используй команды, например, 'Добавь слово hello привет'.\nПолный список" \
                         " команд для этого: +; Аdd; Добавь слово; Добавь. \nТак же ты можешь полностью очистить " \
                         "свой словарь или же удалить отдельно слово из него, используя, например, команду 'Удали" \
                         "hello'.\n Полный список команд для этого: -; Del; Удали."
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
        response.set_tts(choice, True)
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
