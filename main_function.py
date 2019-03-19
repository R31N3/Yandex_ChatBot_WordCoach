# coding: utf-8
from __future__ import unicode_literals
import json
from ans import *
from little_fuctions import *
import training
from words import words



aliceAnswers = read_answers_data("data/answers_dict_example")


# Ну вот эта функция всем функциям функция, ага. Замена постоянному формированию ответа, ага, экономит 4 строчки!!
def message_return(response, user_storage, message, button, database, request, mode):
    # ща будет магия
    noScreen = False if "screen" in request.interfaces.keys() else True
    update_mode(request.user_id, mode, database)
    if "card" in user_storage.keys() and message not in aliceAnswers["helloTextVariations"]:
        buttons, user_storage = get_suggests(user_storage)
        button, something = get_suggests({'suggests': [
            "Словарь",
            "Тренировка",
            "Наборы слов",
            "Помощь",
            "Настройки"
        ]})
        response.set_buttons(button)
        message = message.replace('4000 строк', 'четырех тысяч строк')
        message = message.replace('\n', ' - - ').replace(' pause ', ' - ') + ' - '
        response.set_tts(message + noScreen * "\n. Доступные команды: {}.".format(" - ".join(user_storage['suggests'])))
        response.set_card(user_storage["card"])
        return response, user_storage
    if ">" in message:
        response.set_text(message[message.index(">")+1:].replace('+;', '##!').replace('+', '').replace('##!', '+').replace(' pause ', ' '))
    else:
        response.set_text(message.replace('+;', '##!').replace('+', '').replace('##!', '+').replace(' pause ', ' '))

    message = message.replace('\n', ' - - ').replace(' pause ', ' - ') + noScreen * ' - '
    message = message.replace('(c)', ' - ').replace('(с)', ' - ')
    message = message.replace('(Английская пословица)', ' - Английская пословица.')
    message = message.replace('Гранде', 'Грандэ')
    message = message.replace('4000 строк', 'четырех тысяч строк')
    if 'Неизучено' in message or 'Изучено' in message:
        for i in range(1, 1002, 10):
            if 'Изучено {} слово'.format(i) in message:
                message = message.replace('Изучено {} слово'.format(i),
                                          'Изучено {} одно слово'.format(i//10*10 if i != 1 else ''))
                break
            if 'Неизучено {} слово' in message:
                message = message.replace('Неизучено {} слово'.format(i),
                                          'Неизучено {} одно слово'.format(i // 10 * 10 if i != 1 else ''))
                break
    if type(user_storage["suggests"][0]) != list:
        button, something = get_suggests({'suggests': list(map(lambda x:\
            x.replace(' pause ', ' ').replace('+ ', '##!').replace('+', '').replace('##!', '+'), user_storage['suggests']))})
    else:
        button, something = get_suggests({'suggests': list(map(lambda x: \
            x.replace(' pause ', ' ').replace('+ ', '##!').replace('+', '').replace('##!', '+'), user_storage['suggests'][0]))})
    if mode != 'training' and mode != 'settings' and not mode.startswith('add_set') and \
            not mode.startswith('show_added') and mode != 'translator':
        if type(user_storage["suggests"][0]) != list:
            response.set_tts(message + noScreen * "\n. Доступные команды: {}.".format(" - ".join(user_storage['suggests'])))
        else:
            response.set_tts(
                message + noScreen * "\n. Доступные команды: {}.".format(" - ".join(user_storage['suggests'][0])))
    elif mode == 'training':
        response.set_tts(message + noScreen * "\n. Варианты ответа: {}".format(" - ".join(user_storage['suggests'][:-1])))
    elif mode == 'settings':
        if type(user_storage["suggests"][0]) != list:
            response.set_tts(message + noScreen * " - ".join(user_storage['suggests']))
        else:
            response.set_tts(message + noScreen * " - ".join(user_storage['suggests'][0]))
    elif mode =='translator':
        response.set_tts(message)
    elif mode.startswith('add_set') or mode.startswith('show_added'):
        if len(user_storage['suggests']) >= 3 and user_storage['suggests'][-3] in {'Назад', 'Добавленные наборы'}:
            response.set_tts(message + ' - '.join(user_storage['suggests'][:-3]) + \
                             noScreen * "\n. Доступные команды: {}.".format(" - ".join(user_storage['suggests'][-3:])))
        elif user_storage['suggests'][-2] in {'Ещё', 'Назад', 'Добавленные наборы'}:
            response.set_tts(message + ' - '.join(user_storage['suggests'][:-2]) + \
                             noScreen * "\n. Доступные команды: {}.".format(" - ".join(user_storage['suggests'][-2:])))
        else:
            response.set_tts(message + ' - '.join(user_storage['suggests'][:-1]) + \
                             noScreen * "\n. Доступные команды: {}.".format(" - ".join(user_storage['suggests'][-1:])))
    buttons, user_storage = get_suggests(user_storage)
    print(buttons)
    response.set_buttons(button)
    return response, user_storage


def handle_dialog(request, response, user_storage, database, morph):
    from random import choice
    if not user_storage:
        user_storage = {"suggests": []}
    noScreen = False if "screen" in request.interfaces.keys() else True
    input_message = request.command.lower()
    input_message = input_message.replace("'", "`")
    input_message = input_message.replace('ё', 'е')
    while input_message and input_message[-1] == '.':
          input_message = input_message[:-1]
    if not input_message and not request.is_new_session:
        buttons, user_storage = get_suggests(user_storage)
        mode = ''
        update_mode(request.user_id, mode, database)
        return IDontUnderstand(response, user_storage, aliceAnswers["cantTranslate"])
    user_id = request.user_id
    user_storage = {'suggests': [
        "Словарь",
        "Тренировка",
        "Наборы слов",
        "Помощь",
        "Настройки"
    ]}
    # первый запуск/перезапуск диалога
    if request.is_new_session or not database.get_entry("users_info",  ['Named'],
                                                        {'request_id': user_id})[0][0]:
        if request.is_new_session and (database.get_entry("users_info", ['Name'],
                                                          {'request_id': user_id}) == 'null' or
                                       not database.get_entry("users_info", ['Name'], {'request_id': user_id})):
            output_message = "Тебя приветствует Word Coach, благодаря мне ты сможешь потренироваться в знании" \
                             " английского, а также ты можешь использовать меня в качестве словаря со своими" \
                             " собственными формулировками и ассоциациями для простого запоминания!\n"\
                             "Введите ваше имя."
            response.set_text(output_message)
            response.set_tts(output_message)
            database.add_entries("users_info", {"request_id": user_id})
            mode = "-2"
            update_mode(user_id, mode, database)
            buttons, user_storage = get_suggests({'suggests' : ['У человека нет имени']})

            return message_return(response, user_storage, output_message, buttons, database, request, mode)

        mode = database.get_entry("users_info", ['mode'], {'request_id': user_id})[0][0]
        if mode == "-2":
            if input_message == 'саша':
                output_message = 'Обрати внимание, имя "Саша" будет восприниматься как женское.' \
                                 ' Если тебе это не нравится, могу звать тебя Алекс или Александр.'
                mode = '-3'
                buttons, user_storage = get_suggests({'suggests' : ['Оставь имя "Саша"', 'Зови меня Алекс',
                                                     'Зови меня Александр','Установить другое имя']})
                return message_return(response, user_storage, output_message, buttons, database, request, mode)
            if input_message == 'женя':
                output_message = 'Обрати внимание, имя "Женя" будет восприниматься как женское.' \
                                 ' Если тебе это не нравится, могу звать тебя Евгений.'
                mode = '-3'
                buttons, user_storage = get_suggests({'suggests': ['Оставь имя "Женя"', 'Зови меня Евгений',
                                                                    'Установить другое имя']})
                return message_return(response, user_storage, output_message, buttons, database, request, mode)
            if input_message != 'у человека нет имени':
                database.update_entries('users_info', user_id, {'Named': True}, update_type='rewrite')
                user_storage["name"] = request.command
                database.update_entries('users_info', user_id, {'Name': input_message.capitalize()},
                                        update_type='rewrite')
            else:
                user_storage['suggests'] = [
                    "Словарь",
                    "Тренировка",
                    "Наборы слов",
                    "Помощь",
                    "Настройки"
                ]
                user_storage["card"] = {
                    "type": "BigImage",
                    "image_id": "1030494/7c51755386214beff775",
                    "title": "У человека нет имени",
                    "description": "Поняла вас, Сэр!",
                }
                mode = ''
                update_mode(user_id, mode, database)
                database.update_entries('users_info', user_id, {'Named': True}, update_type='rewrite')
                user_storage["name"] = request.command
                database.update_entries('users_info', user_id, {'Name': 'Noname'}, update_type='rewrite')
                return message_return(response, user_storage, "Поняла вас, Сэр!", [], database, request, mode)


        if mode == '-3':
            if input_message == 'зови меня александр':
                database.update_entries('users_info', user_id, {'Named': True}, update_type='rewrite')
                user_storage["name"] = request.command
                database.update_entries('users_info', user_id, {'Name': 'Александр'},
                                        update_type='rewrite')
            elif input_message == 'зови меня алекс':
                database.update_entries('users_info', user_id, {'Named': True}, update_type='rewrite')
                user_storage["name"] = request.command
                database.update_entries('users_info', user_id, {'Name': 'Алекс'},
                                        update_type='rewrite')
            elif input_message == 'оставь имя саша':
                database.update_entries('users_info', user_id, {'Named': True}, update_type='rewrite')
                user_storage["name"] = request.command
                database.update_entries('users_info', user_id, {'Name': 'Саша'},
                                        update_type='rewrite')
            elif input_message == 'зови меня евгений':
                database.update_entries('users_info', user_id, {'Named': True}, update_type='rewrite')
                user_storage["name"] = request.command
                database.update_entries('users_info', user_id, {'Name': 'Евгений'},
                                        update_type='rewrite')
            elif input_message == 'оставь имя женя':
                database.update_entries('users_info', user_id, {'Named': True}, update_type='rewrite')
                user_storage["name"] = request.command
                database.update_entries('users_info', user_id, {'Name': 'Женя'},
                                        update_type='rewrite')
            else:
                output_message = 'Хорошо, назови свое имя.'
                mode = "-2"
                update_mode(user_id, mode, database)
                buttons, user_storage = get_suggests({'suggests': ['У человека нет имени']})
                return message_return(response, user_storage, output_message, buttons, database, request, mode)

        output_message = hello(user_id, database)

        mode = ""
        buttons, user_storage = get_suggests(user_storage)
        return message_return(response, user_storage, output_message, buttons, database, request, mode)

    mode = get_mode(user_id, database)

    if input_message == 'настройки':
        mode = 'settings'
        output_message = 'Доступны следующие настройки:'
        dictionary = get_dictionary(user_id, database)
        count = len(dictionary['to_learn']) + len(dictionary['learned'])
        if count == 0:
            # buttons = ['Режим перевода', 'Сменить имя', 'Оценить навык', 'В начало']
            buttons = ['Сменить имя', 'В начало']
        else:
            # buttons = ['Режим перевода', 'Сменить имя', 'Очистить словарь', 'Оценить навык', 'В начало']
            buttons = ['Сменить имя', 'Очистить словарь', 'Оценить навык', 'В начало']
        buttons, user_storage = get_suggests({'suggests': buttons})
        return message_return(response, user_storage, output_message, buttons, database, request,
                              mode)

    if input_message.startswith('оценить') and mode == 'settings':
        mode = ''
        if not noScreen:
            output_message = 'Держи ссылку!'
            user_storage["suggests"] = [
                    ["Оценить!", "https://dialogs.yandex.ru/store/skills/b7c4a595-word-coach-trener-slov"]
            ]
        else:
            output_message = 'Ты можешь оценить навык на устройстве с экраном, мы будем рады любой твоей объективной оценке и комментарию.'
        buttons, user_storage = get_suggests(user_storage)
        return message_return(response, user_storage, output_message, buttons, database, request,
                              mode)

    if input_message.startswith('оценить') and mode == '':
        output_message = 'Спасибо за ваш отзыв. Я очень ценю каждое мнение!'
        buttons, user_storage = get_suggests(user_storage)
        mode = ''
        return message_return(response, user_storage, output_message, buttons, database, request,
                              mode)

    if input_message in {'сменить имя', 'поменять имя', 'установить другое имя'} and mode == 'settings':
        mode = 'change_name'
        output_message = 'Введи или назови новое имя.'
        buttons, user_storage = get_suggests({'suggests' : ['У человека нет имени', 'Отмена']})
        return message_return(response, user_storage, output_message, buttons, database, request,
                              mode)

    if input_message == 'женя' and mode == 'change_name':
        output_message = 'Обрати внимание, имя "Женя" будет восприниматься как женское.' \
                         ' Если тебе это не нравится, могу звать тебя Евгений.'
        mode = 'jen_name'
        buttons, user_storage = get_suggests({'suggests': ['Оставь имя "Женя"', 'Зови меня Евгений',
                                                           'Установить другое имя', 'Отмена']})
        return message_return(response, user_storage, output_message, buttons, database, request, mode)

    if mode == 'jen_name' and input_message != 'отмена' and 'начал' not in input_message:
        if input_message.startswith('оставь имя '):
            output_message = 'Хорошо, буду звать тебя Женя.'
            database.update_entries('users_info', user_id, {'Name': 'Женя'}, update_type='rewrite')
        elif input_message == 'зови меня евгений':
            output_message = 'Хорошо, буду звать тебя Евгений.'
            database.update_entries('users_info', user_id, {'Name': 'Евгений'}, update_type='rewrite')
        else:
            mode = 'change_name'
            output_message = 'Введи или назови новое имя.'
            buttons, user_storage = get_suggests({'suggests': ['У человека нет имени', 'Отмена']})
            return message_return(response, user_storage, output_message, buttons, database, request,
                                  mode)
        mode = ''
        buttons, user_storage = get_suggests(user_storage)
        return message_return(response, user_storage, output_message, buttons, database, request,
                              mode)

    if input_message == 'саша' and mode == 'change_name':
        output_message = 'Обрати внимание, имя "Саша" будет восприниматься как женское.' \
                         ' Если тебе это не нравится, могу звать тебя Алекс или Александр.'
        mode = 'sasha_name'
        buttons, user_storage = get_suggests({'suggests': ['Оставь имя "Саша"', 'Зови меня Алекс',
                                                           'Зови меня Александр', 'Установить другое имя', 'Отмена']})
        return message_return(response, user_storage, output_message, buttons, database, request,
                              mode)

    if mode == 'sasha_name' and input_message != 'отмена' and 'начал' not in input_message:
        if input_message.startswith('оставь имя '):
            output_message = 'Хорошо, буду звать тебя Саша.'
            database.update_entries('users_info', user_id, {'Name': 'Саша'}, update_type='rewrite')
        elif input_message == 'зови меня александр':
            output_message = 'Хорошо, буду звать тебя Александр.'
            database.update_entries('users_info', user_id, {'Name': 'Александр'}, update_type='rewrite')
        elif input_message == 'зови меня алекс':
            output_message = 'Хорошо, буду звать тебя Алекс.'
            database.update_entries('users_info', user_id, {'Name': 'Алекс'}, update_type='rewrite')
        else:
            mode = 'change_name'
            output_message = 'Введи или назови новое имя.'
            buttons, user_storage = get_suggests({'suggests': ['У человека нет имени', 'Отмена']})
            return message_return(response, user_storage, output_message, buttons, database, request,
                                  mode)
        mode = ''
        buttons, user_storage = get_suggests(user_storage)
        return message_return(response, user_storage, output_message, buttons, database, request,
                              mode)

    if input_message in {'переводчик', 'режим перевода', 'режим переводчика'} and  mode.endswith('dict'):
        mode = 'translator_inf'
        output_message = 'В режиме переводчика я смогу только переводить и добавлять в словарь.'
        buttons, user_storage = get_suggests({'suggests' : ['Включить режим', 'В начало']})
        return message_return(response, user_storage, output_message, buttons, database, request,
                              mode)

    if ((input_message.startswith('включи') and mode == 'translator_inf') or
            (mode.startswith('translator') and mode != 'translator_inf')) and \
            (not input_message.startswith('добавь') and input_message not in {'в начало', 'начало', 'сначала'}):
        if mode == 'translator_inf':
            mode = 'translator'
            output_message = 'Ок, включила режим переводчика. Просто скажи "В начало", когда закончишь.'
            buttons, user_storage = get_suggests({'suggests': ['В начало']})
            return message_return(response, user_storage, output_message, buttons, database, request,
                                  mode)
        else:
            if language_match('t', input_message):
                t = translate_text(input_message, 'ru-en')
                if t:
                    translation = ''.join(t)
            elif language_match('г', input_message):
                t = translate_text(input_message, 'en-ru')
                if t:
                    translation = ''.join(t)
            else:
                output_message = 'Не поняла, что вы хотите перевести'
                buttons, user_storage = get_suggests({'suggests' : ['В начало']})
                return message_return(response, user_storage, output_message, buttons, database, request,
                                      mode)
            if not t:
                output_message = choice(['Кажется, это нельзя перевести.', 'Затрудняюсь пеевести.'])
                buttons, user_storage = get_suggests({'suggests': ['В начало']})
                return message_return(response, user_storage, output_message, buttons, database, request,
                                      mode)
            output_message = '\nВот что я нашла:\n{} - {}'.format(input_message.capitalize(),
                                                                             translation.capitalize())
            buttons, user_storage = get_suggests(
                {'suggests': ['Добавь {} {}'.format(input_message.capitalize(), translation.capitalize()), 'В начало']})
            return message_return(response, user_storage, output_message, buttons, database, request,
                                  mode)


    if input_message == 'у человека нет имени' and mode == 'change_name':
        user_storage['suggests'] = [
            "Словарь",
            "Тренировка",
            "Наборы слов",
            "Помощь",
            "Настройки"
        ]
        user_storage["card"] = {
            "type": "BigImage",
            "image_id": "1030494/7c51755386214beff775",
            "title": "У человека нет имени.",
            "description": "Поняла вас, Сэр!",
        }
        mode = ''
        database.update_entries('users_info', user_id, {'Named': True}, update_type='rewrite')
        user_storage["name"] = request.command
        database.update_entries('users_info', user_id, {'Name': 'Noname'}, update_type='rewrite')
        return message_return(response, user_storage, "Поняла вас, Сэр!", [], database, request, mode)


    if mode == 'change_name' and input_message != 'отмена':
        mode = ''
        output_message = 'Хорошо, теперь твое имя - {}!'.format(input_message.capitalize())
        input_message = input_message.capitalize()
        database.update_entries('users_info', user_id, {'Name': input_message}, update_type='rewrite')
        buttons, user_storage = get_suggests(user_storage)
        return message_return(response, user_storage, output_message, buttons, database, request,
                              mode)


    if input_message in {'словарь', 'словарик'} and mode == '':
        dictionary = get_dictionary(user_id, database)
        name = get_name(user_id, database)
        count = len(dictionary['to_learn']) + len(dictionary['learned'])
        if name != 'Noname':
            output_message = '{}, в твоем словаре {} сл+ов'.format(name, count)\
                             + ending(count)+"."
        else:
            output_message = 'В твоем словаре {} сл+ов'.format(count) + ending(count)+"."
        if count == 0:
            mode = ''
            output_message += '\nТы можешь добавить в словарь готовые наборы слов или прочитать в разделе помощь о том,' \
                              ' как добавлять свои.'
            buttons, user_storage = get_suggests({'suggests': ['Наборы слов', 'Режим переводчика', 'В начало']})
        else:
            output_message += '\nВ разделе помощь ты можешь узнать, как добавлять или удалять слова.'
            buttons, user_storage = get_suggests({'suggests': ['Неизученные слова', 'Изученные слова', 'Наборы слов', 'Тренировка', 'Режим переводчика', 'В начало']})
            mode = '0_dict'
        return message_return(response, user_storage, output_message, buttons, database, request,
                              mode)

    if (input_message in {'изученные слова', 'ученные слова'} and mode == '0_dict')\
            or ((input_message in {'дальше', 'далее', 'еще'} or input_message == 'назад') and mode.endswith('_dict')):
        page = int(mode.split('_')[0])
        if input_message in {'дальше', 'далее', 'еще'} or input_message in {'изученные слова', 'ученные слова'}:
            mode = '{}_dict'.format(page + 1)
            page += 1
        elif input_message == 'назад':
            mode = '{}_dict'.format(page - 1)
            page -= 1
        output_message, max_page = envision_dictionary(user_id, database, False, page)
        if max_page == 0:
            output_message = 'У тебя еще нет изученных слов.'
        buttons = ['В начало']
        if page < max_page:
            buttons = ['Дальше'] + buttons
        if page > 1:
            buttons = ['Назад'] + buttons
        buttons, user_storage = get_suggests({'suggests' : buttons})
        return message_return(response, user_storage, output_message, buttons, database, request,
                              mode)

    if (input_message in {'неизученные слова', 'неученные слова'} and mode == '0_dict')\
            or ((input_message in {'дальше', 'далее', 'еще'} or input_message == 'назад') and mode.endswith('_dict_n')):
        page = int(mode.split('_')[0])
        if input_message in {'дальше', 'далее', 'еще'} or input_message in {'неизученные слова', 'неученные слова'}:
            mode = '{}_dict_n'.format(page + 1)
            page += 1
        else:
            mode = '{}_dict_n'.format(page - 1)
            page -= 1
        output_message, max_page = envision_dictionary(user_id, database, True, page)
        if max_page == 0:
            output_message = 'У тебя еще нет неизученных слов.\nМожешь добавить готовые наборы слов.'
            buttons = ['В начало', 'Наборы слов']
            mode = ''
        else:
            buttons = ['В начало']
            if page < max_page:
                buttons = ['Дальше'] + buttons
            if page > 1:
                buttons = ['Назад'] + buttons
        buttons, user_storage = get_suggests({'suggests' : buttons})
        return message_return(response, user_storage, output_message, buttons, database, request,
                              mode)

    if input_message in {'очисть словарь', 'почисть словарь', 'очисть слова', 'почисть слова', 'очистить словарь', 'очисти словарь'}\
            and (mode == '' or mode == '0_dict' or mode == 'settings'):
        update_dictionary(user_id, {'to_learn': {}, 'learned': {}}, database)
        output_message = 'Ваш словарь теперь пустой :)'
        buttons, user_storage = get_suggests(user_storage)
        mode = ''
        update_word_sets(user_id, set([]), database)
        return message_return(response, user_storage, output_message, buttons, database, request,
                              mode)

    if input_message in {'тренировка', 'тонировка'} and mode in {'', '0_dict'}:
        noScreen = False if "screen" in request.interfaces.keys() else True
        if not noScreen:
            update_mode(user_id, 'training_choice', database)
            mode = 'training_choice'
            update_stat_session('training', [0, 0], user_id, database)
            output_message = "В этом режиме нужно переводить слова из твоего словаря :)\n" + 'Я еще не научилась как следует воспринимать английскую речь, поэтому мы не будем переводить русские слова.' * noScreen + \
               'С английским языком я пока не так хорошо дружу, так что лучше используй кнопки при переводе русских слов. ' * (not noScreen) + \
               + choice(['Выбери режим', 'Осталось только выбрать режим'])
            buttons, user_storage = get_suggests(
                {'suggests': ['Русский -> Английский', 'Английский -> Русский', 'Совместный', 'В начало']})
            return message_return(response, user_storage, output_message, buttons, database, request,
                                  mode)
        else:
            mode = 'trainingen'
            update_mode(user_id, mode, database)
            update_stat_session('training', [0, 0], user_id, database)

    if mode == 'training_choice' and input_message in {'русский -> английский', 'английский -> русский', 'совместный'}:
        mode = 'training'
        if input_message == 'русский -> английский':
            mode += 'ru'
        elif input_message == 'английский -> русский':
            mode += 'en'
        else:
            mode += 't'
        update_mode(user_id, mode, database)
        update_stat_session('training', [0, 0], user_id, database)

    if ("помощь" in input_message or "что ты умеешь" in input_message):
        output_message = "Благодаря данному навыку ты можешь учить английский так, как тебе хочется! Ты можешь " \
                         "добавить слова, которые хочешь выучить, используя удобные тебе ассоциации, или же выбрать " \
                         "набор из доступных категорий, после чего испытать свои силы в тренировке!"
        buttons, user_storage = get_suggests({'suggests': ['Как добавлять слова?', 'Как удалять слова?', 'Справка о тренировках', 'Что делать?',
                                                           'В начало']})
        mode = 'help'
        return message_return(response, user_storage, output_message, buttons, database, request,
                              mode)

    if input_message in {'справка', 'справка о тренировках', 'справка о тренировке'} and mode == 'help':
        output_message = 'У каждого сл+ова есть его прогресс, изначально равный нулю. ' \
                         'После каждого правильного ответа на вопрос прогресс соответствующего сл+ова увеличивается на 1, ' \
                         'после неправильного - уменьшается на 2, но не опускается ниже нуля. ' \
                         'Сл+ово считается изученным, если его прогресс больше либо равен 4\n' \
                         'Для удобства, ты можешь называть только номер верного варианта.\n' \
                         'Приятных тренировок!'
        buttons, user_storage = get_suggests(
            {'suggests': ['Как добавлять слова?', 'Как удалять слова?', 'Что делать?',
                          'В начало']})
        mode = 'help'
        return message_return(response, user_storage, output_message, buttons, database, request,
                              mode)

    if input_message in {'как добавлять слова?', 'как добавить слова?', 'как добавить слово?',
                         'как добавлять слова', 'как добавить слова', 'как добавить слово'} \
        and mode == 'help':
        output_message = "Для занесения" \
                         ' слов в словарь используй команды, например, "Добавь слово hello привет".\nПолный список' \
                         " команд для этого: +; Аdd; Добавь слово; Добавь. \n А также ты можешь добавлять стандартные "\
                         "наборы слов из доступных категорий."
        buttons, user_storage = get_suggests(
            {'suggests': ['Как удалять слова?', 'Что делать?', 'В начало']})
        return message_return(response, user_storage, output_message, buttons, database, request,
                              mode)

    if input_message in {'как удалять слова?', 'как удалить слово?', 'как удалить слова?',
                         'как удалять слова', 'как удалить слово', 'как удалить слова'}\
                        and mode == 'help':
        output_message = "Ты можешь полностью очистить " \
                         'свой словарь или же удалить из него отдельное слово, используя, например, команду "Удали ' \
                         'hello".\nПолный список команд для этого: -; Del; Удали; Удали сл+ово.'
        buttons, user_storage = get_suggests(
            {'suggests': ['Как добавлять слова?', 'Что делать?', 'В начало']})
        return message_return(response, user_storage, output_message, buttons, database, request,
                              mode)

    if input_message in {'что делать?', 'что делать'} and mode == 'help':
        output_message = 'Учить английский!\nОднажды я тоже задавалась таким вопросом.' \
                         ' В итоге прочитала книгу Н.Г. Чернышевского "Что делать?" и начала учить английский!'
        mode = ''
        user_storage["card"] = {
            "type": "BigImage",
            "image_id": "965417/71f69697771ec2f09ff5",
            "title": "Что делать?",
            "description": "'Учить английский!\nОднажды я тоже задавалась таким вопросом. "
                           "В итоге прочитала книгу Н.Г. Чернышевского 'Что делать?' и начала учить английский!",
        }
        buttons, user_storage = get_suggests(user_storage)
        return message_return(response, user_storage, output_message, buttons, database, request,
                              mode)


    if (input_message in {'наборы слов', 'набор слов'} and mode in {'', '0_dict'}) or (input_message == 'назад' and mode == 'add_set 2'):
        added = get_word_sets(user_id, database)
        sets = sorted(list(set(list(words.keys())).difference(added)))
        if len(sets) == 0:
            gender = get_gender(user_id, database, morph)
            if gender == "masc" or str(gender) == "Noname":
                output_message = choice(['Ты добавил все наборы!', 'Тобой были добавлены все доступные наборы!',
                                         'Ты добавил все предлагаемые нами слова!'])
            else:
                output_message = choice(['Ты добавила все наборы!', 'Тобой были добавлены все доступные наборы!',
                                         'Ты добавила все предлагаемые нами слова!'])
            butts = {'suggests': ['Добавленные наборы', 'В начало']}
            buttons, user_storage = get_suggests(butts)
            mode = 'add_set 1'
            return message_return(response, user_storage, output_message, buttons, database, request,
                                  mode)
        gender = get_gender(user_id, database, morph)
        if gender == "masc" or str(gender) == "Noname":
            output_message = choice(['Вот наборы, которые ты ещ+е не добавил.', "Посмотри ещё недобавленные наборы."])\
                             + ('\nСтраница 1 из {}'.format((len(sets) + 3) // 4)
                             if (len(sets) + 3) // 4 > 1 else '')
        else:
            output_message = choice(['Вот наборы, которые ты ещ+е не добавила.', "Посмотри ещё недобавленные наборы."]) \
                             + ('\nСтраница 1 из {}'.format((len(sets) + 3) // 4)
                                if (len(sets) + 3) // 4 > 1 else '')

        butts = {'suggests': sets[0:4]}
        if (len(sets) != len(list(words.keys())) or len(added) > 0) and (mode == '' or mode == 'add_set 2'):
            butts['suggests'].append('Добавленные наборы')
        if len(sets) > 4:
            butts['suggests'].append('Ещё')
        butts['suggests'].append('В начало')
        buttons, user_storage = get_suggests(butts)
        mode = 'add_set 1'
        return message_return(response, user_storage, output_message, buttons, database, request,
                              mode)


    if input_message in {'еще', 'дальше'} and mode.startswith('add_set'):
        next_page = int(mode.split()[1]) + 1
        added = get_word_sets(user_id, database)
        sets = sorted(list(set(list(words.keys())).difference(added)))
        output_message = choice(['Ты можешь добавить наборы слов по следующим тематикам.',
                                 'Ты можешь выбрать наборы из представленного списка.',
                                 'Выбери нужный тебе набор из списка.']) \
                         + '\nСтраница {} из {}.'.format(next_page, (len(sets) + 3) // 4)
        butts = {'suggests': sets[next_page * 4 - 4:next_page * 4] + \
                             ['Назад'] + \
                             (['Ещё'] if len(sets) - 4 * (next_page - 1) > 4 else [])}
        butts['suggests'].append('В начало')
        buttons, user_storage = get_suggests(butts)
        mode = 'add_set {}'.format(next_page)
        return message_return(response, user_storage, output_message, buttons, database, request,
                              mode)

    if input_message == 'назад' and mode.startswith('add_set'):
        next_page = int(mode.split()[1]) - 1
        added = get_word_sets(user_id, database)
        sets = sorted(list(set(list(words.keys())).difference(added)))
        output_message = choice(['Ты можешь добавить наборы слов по следующим тематикам.',
                                 'Ты можешь выбрать наборы из представленного списка.',
                                 'Выбери нужный тебе набор из списка.']) \
                         + '\nСтраница {} из {}.'.format(next_page, (len(sets) + 3) // 4)
        butts = {'suggests': sets[next_page * 4 - 4:next_page * 4] + \
                             ['Назад'] + \
                             (['Ещё'] if len(list(words.keys())) - 4 * (next_page - 1) > 4 else [])}
        butts['suggests'].append('В начало')
        buttons, user_storage = get_suggests(butts)
        mode = 'add_set {}'.format(next_page)
        return message_return(response, user_storage, output_message, buttons, database, request,
                              mode)

    if (mode == 'add_set 1' and input_message.startswith('добавленные набор')) or (mode == 'show_added 2' and input_message == 'назад'):
        added = get_word_sets(user_id, database)
        sets = sorted(list(added))
        gender = get_gender(user_id, database, morph)
        if gender == "masc" or str(gender) == "Noname":
            output_message = 'Выбор набора исключит его из твоего словаря\nВот наборы, которые ты добавил.'\
                             + ('\nСтраница 1 из {}.'.format((len(sets) + 3) // 4)
                             if (len(sets) + 3) // 4 > 1 else '')
        else:
            output_message = 'Выбор набора исключит его из твоего словаря\nВот наборы, которые ты добавила.'\
                             + ('\nСтраница 1 из {}.'.format((len(sets) + 3) // 4)
                             if (len(sets) + 3) // 4 > 1 else '')
        butts = {'suggests': sets[0:4] + (['Ещё'] if len(sets) > 4 else [])}
        butts['suggests'].append('В начало')
        mode = 'show_added 1'
        buttons, user_storage = get_suggests(butts)
        return message_return(response, user_storage, output_message, buttons, database, request,
                              mode)

    if input_message in {'еще', 'дальше'} and mode.startswith('show_added'):
        next_page = int(mode.split()[1]) + 1
        added = get_word_sets(user_id, database)
        sets = sorted(list(added))
        gender = get_gender(user_id, database, morph)
        if gender == "masc" or str(gender) == "Noname":
            output_message = 'Вот наборы, которые ты добавил.' \
                             + '\nСтраница {} из {}.'.format(next_page, (len(sets) + 3) // 4)
        else:
            output_message = 'Вот наборы, которые ты добавила.' \
                             + '\nСтраница {} из {}.'.format(next_page, (len(sets) + 3) // 4)
        butts = {'suggests': sets[next_page * 4 - 4:next_page * 4] + \
                             ['Назад'] + \
                             (['Ещё'] if len(sets) - 4 * (next_page - 1) > 4 else [])}
        butts['suggests'].append('В начало')
        buttons, user_storage = get_suggests(butts)
        mode = 'show_added {}'.format(next_page)
        return message_return(response, user_storage, output_message, buttons, database, request,
                              mode)

    if input_message == 'назад' and mode.startswith('show_added'):
        next_page = int(mode.split()[1]) - 1
        added = get_word_sets(user_id, database)
        sets = sorted(list(added))
        gender = get_gender(user_id, database, morph)
        if gender == "masc" or str(gender) == "Noname":
            output_message = 'Вот наборы, которые ты добавил.' \
                             + '\nСтраница {} из {}.'.format(next_page, (len(sets) + 3) // 4)
        else:
            output_message = 'Вот наборы, которые ты добавила.' \
                             + '\nСтраница {} из {}.'.format(next_page, (len(sets) + 3) // 4)
        butts = {'suggests': sets[next_page * 4 - 4:next_page * 4] + \
                             ['Назад'] + \
                             (['Ещё'] if len(list(words.keys())) - 4 * (next_page - 1) > 4 else [])}
        butts['suggests'].append('В начало')
        buttons, user_storage = get_suggests(butts)
        mode = 'show_added {}'.format(next_page)
        return message_return(response, user_storage, output_message, buttons, database, request,
                              mode)

    if input_message.capitalize() in words and mode.startswith('show_added'):
        for word, translate in words[input_message.capitalize()].items():
            dictionary = del_word(word.capitalize().replace('+', ''), user_id, database)
            if dictionary != 'no such word' and dictionary:
                update_dictionary(user_id, dictionary, database)
        buttons, user_storage = get_suggests(user_storage)
        output_message = choice(['Удалила. Что будем делать?', 'Готово. Что делаем дальше?'])
        mode = ''
        added = get_word_sets(user_id, database)
        added.remove(input_message.capitalize())
        update_word_sets(user_id, added, database)
        return message_return(response, user_storage, output_message, buttons, database, request,
                              mode)


    if input_message.capitalize() in words and mode.startswith('add_set'):
        for word, translate in words[input_message.capitalize()].items():
            dictionary = add_word(word.replace('+', ''), translate.replace('+', ''), user_id, database)
            if dictionary != 'already exists' and dictionary != 'rus_exist' and dictionary:
                update_dictionary(user_id, dictionary, database)
        buttons, user_storage = get_suggests(user_storage)
        output_message = choice(['Добавила. Загляни в словарь.', 'Готово! Предлагаю тренировочку.',
                                 'Успешно! Я бы пошла тренировать новые слова :)', 'Сделано. Что будем делать теперь?'])
        mode = ''
        added = get_word_sets(user_id, database)
        added.add(input_message.capitalize())
        update_word_sets(user_id, added, database)
        return message_return(response, user_storage, output_message, buttons, database, request,
                              mode)

    if mode != '' and mode[0] == '!' and not input_message.startswith('добавь') and not input_message.startswith('в начало'):
        success = add_word(''.join(mode[1:]), input_message, user_id, database)
        answer = ''.join(mode[1:]), input_message
        answer = list(map(lambda x: x.capitalize(), answer))
        if language_match(answer[0], answer[1]) == 'miss':
            answer = answer[::-1]
        if success == 'already exists':
            output_message = choice(['В Вашем словаре уже есть такой перевод.', 'Словарь уже содержит такой перевод.',
                                     'Такой перевод уже есть в Вашем словаре.'])
        elif success == 'rus_exist':
            output_message = 'В твоем словаре уже есть слово с переводом {}'.format(answer[1])
        elif not success:
            output_message = 'Пара должна состоять из русского и английского сл+ова.'
        else:
            title = 'Слово' if answer[0].strip().count(' ') == 0 else 'Предложение'
            output_message = '{} "{}" с переводом "{}" добавлено в Ваш словарь.'.format(title, answer[0], answer[1])
            update_dictionary(user_id, success, database)
        if mode != 'translator':
            mode = ''
            buttons, user_storage = get_suggests(user_storage)
        else:
            buttons, user_storage = get_suggests({'suggests': ['В начало']})
        return message_return(response, user_storage, output_message, buttons, database, request,
                              mode)



    update_mode(user_id, mode, database)

    answer = classify(input_message, mode)
    handle = answer['class']
    answer = answer['answer']

    if handle == "add" and answer:
        answer = list(map(lambda x: x.capitalize(), answer))
        success = add_word(answer[0], answer[1], user_id, database)
        if language_match(answer[0], answer[1]) == 'miss':
            answer = answer[::-1]
        if success == 'already exists':
            output_message = choice(['В Вашем словаре уже есть такой перевод.', 'Словарь уже содержит такой перевод.',
                                     'Такой перевод уже есть в Вашем словаре.'])
        elif success == 'rus_exist':
            output_message = 'В твоем словаре уже есть слово с переводом {}'.format(answer[1])
        elif not success:
            output_message = 'Пара должна состоять из русского и английского сл+ова.'
        else:
            title = 'Слово' if answer[0].strip().count(' ') == 0 else 'Предложение'
            output_message = '{} "{}" с переводом "{}" добавлено в Ваш словарь.'.format(title, answer[0], answer[1])
            update_dictionary(user_id, success, database)
        if mode == 'training' :
            output_message += '\nРежим тренировки автоматически завершен.'
            stat = get_stat_session('training', user_id, database)
            output_message += '\nТы ответил на {} из {} моих вопросов.'.format(stat[1], stat[0])
        if mode != 'translator':
            mode = ''
            buttons, user_storage = get_suggests(user_storage)
        else:
            buttons, user_storage = get_suggests({'suggests': ['В начало']})
        return message_return(response, user_storage, output_message, buttons, database, request,
                              mode)

    elif handle == 'its me':
        output_message = 'Это я!'
        mode = ''
        buttons, user_storage = get_suggests(user_storage)
        return message_return(response, user_storage, output_message, buttons, database, request,
                              mode)

    elif handle == 'translate&suggest_to_add':
        if language_match('t', answer):
            t = translate_text(answer, 'ru-en')
            if t:
                translation = ''.join(t)
        elif language_match('г', answer):
            t = translate_text(answer, 'en-ru')
            if t:
                translation = ''.join(t)
        else:
            output_message = 'Не поняла, что вы хотите перевести.'
            mode = ''
            buttons, user_storage = get_suggests(user_storage)
            return message_return(response, user_storage, output_message, buttons, database, request,
                                  mode)
        if not t:
            output_message = choice(['Кажется, это нельзя перевести', 'Затрудняюсь пеевести']) + \
                             '\nТы можешь сказать или написать свой перевод, он будет добавлен в словарь.'
            buttons, user_storage = get_suggests({'suggests' : ['В начало']})
            mode = '!' + answer
            return message_return(response, user_storage, output_message, buttons, database, request,
                                  mode)
        if answer.count(' ') > 0:
            output_message = 'Попробую перевести твое предложение...'
        else:
            output_message = 'Попробую перевести твое слово...'
        output_message += '\nВот что у меня получилось:\n{} - {}'.format(answer.capitalize(), translation.capitalize())
        mode = '!' + answer
        output_message += '\nТы также можешь сказать или написать свой перевод, он будет добавлен в словарь.'
        buttons, user_storage = get_suggests({'suggests' : ['Добавь {} {}'.format(answer.capitalize(), translation.capitalize()), 'В начало']})
        return message_return(response, user_storage, output_message, buttons, database, request,
                              mode)

    elif handle == 'del' and answer != '' and answer:
        answer = answer.capitalize()
        success = del_word(answer.strip(), user_id, database)
        if success == 'no such word':
            output_message = choice(['В Вашем словаре нет такого слова.', "Данное слово отсутствует в Вашем словаре.",
                                     "Это слово не содержится в Вашем словаре."])
        elif not success:
            output_message = choice(['Слово должно быть русским или английским.', "Слово для перевода должно быть на"
                                                                                  " русском или английском"])
        else:
            output_message = 'Слово "{}" удалено из Вашего словаря.'.format(answer)
            update_dictionary(user_id, success, database)
        buttons, user_storage = get_suggests(user_storage)

        if mode == 'training':
            output_message += '\nРежим тренировки автоматически завершен.'
            stat = get_stat_session('training', user_id, database)
            output_message += '\nТы ответил на {} из {} моих вопросов.'.format(stat[1], stat[0])
            update_mode(user_id, mode, database)
        mode = ''
        return message_return(response, user_storage, output_message, buttons, database, request,
                              mode)

    elif (input_message == 'отмена' or 'начал' in input_message) and (mode == 'help' or
                                                    mode.startswith('add_set') or
                                                    mode == '' or
                                                    mode.endswith('_dict') or
                                                    mode.endswith('_dict_n') or
                                                    mode == 'settings' or
                                                    mode == 'change_name' or
                                                    mode == 'suggest_to_add' or
                                                    mode.startswith('show_added') or
                                                    mode.startswith('translator') or
                                                    mode == 'sasha_name' or
                                                    mode == 'jen_name' or
                                                    mode[0] == '!' or
                                                    mode == 'training_choice'):
        buttons, user_storage = get_suggests(user_storage)
        output_message = choice(['Ок, начнем с начала.', 'Что будем делать теперь?',
                                'Чтобы начать, не нужно быть великим, но чтобы стать великим, необходимо начать. (Из книги "Куриный бульон для души")',
                                'Не важно, насколько тяжело прошлое, вы всегда можете начать сначала. (c) Ариана Гранде',
                                'Главная удача в жизни — умение начинать всё сначала. (c) Мария Фариса',
                                'Доброе начало — уже полдела. (c) Александр Парвус',
                                'Начиная что-либо, всегда думай о конце. (Английская пословица)',
                                'Хорошее начало – половина сражения. (Английская пословица)',
                                'Хорошее начало обеспечивает хороший конец. (Английская пословица)',
                                'Конец одного пути, всегда начало другого. (c) Мадам Ворна',
                                'Первый шаг — всегда самый трудный. Мы начали с книги по Python, а сейчас вы видите работу 4000 строк нашего кода:)'])
        mode = ''
        if output_message.startswith('Первый шаг'):
            user_storage["card"] = {
                "type": "BigImage",
                "image_id": "1540737/048c917a4dc6b05b5cb7",
                "title": "У тебя все получится!",
                "description": output_message,
            }
        return message_return(response, user_storage, output_message, buttons, database, request,
                              mode)

    elif handle == 'use_mode':
        if get_mode(user_id, database).startswith('training'):
            output_message = training.main(get_q(user_id, database), answer, 'revise&next', user_id, database, request)
            if get_mode(user_id, database).startswith('training'):
                but = training.get_buttons(get_q(user_id, database), user_id, database)
                stor = {'suggests': but + (['Закончить тренировку'] if get_q(user_id, database) != '###empty' else [])}
            else:
                stor = {'suggests': user_storage['suggests']}
                update_mode(user_id, '', database)
            buttons, user_storage = get_suggests(stor)
            mode = get_mode(user_id, database)
            return message_return(response, user_storage, output_message, buttons, database, request,
                              mode)

    if input_message in ['не хочется', 'в следующий раз', 'выход', "не хочу", 'выйти']:
        choice = choice(aliceAnswers["quitTextVariations"])
        response.set_text(choice)
        response.set_tts(choice)
        response.end_session = True
        return response, user_storage

    buttons, user_storage = get_suggests(user_storage)
    mode = ''
    update_mode(user_id, mode, database)
    return IDontUnderstand(response, user_storage, aliceAnswers["cantTranslate"])
