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

    update_mode(request.user_id, mode, database)
    if ">" in message:
        response.set_text(message[message.index(">")+1:])
    else:
        response.set_text(message)
    if mode != 'training' and mode != 'settings' and not mode.startswith('add_set') and \
            not mode.startswith('show_added') and mode != 'translator':
        response.set_tts(message.replace('\n', ' - - ') + "\n. Доступные команды: {}.".format(" - - ".join(user_storage['suggests'])))
    elif mode == 'training':
        response.set_tts(message.replace('\n', ' - - ') + "\n. Варианты ответа: {}".format(" - - ".join(user_storage['suggests'][:-1])))
    elif mode == 'settings':
        response.set_tts(message.replace('\n', ' - - ') + " - - ".join(user_storage['suggests']))
    elif mode =='translator':
        response.set_tts(message.replace('\n', ' - - '))
    elif mode.startswith('add_set') or mode.startswith('show_added'):
        if len(user_storage['suggests']) >= 3 and user_storage['suggests'][-3] in {'Назад', 'Добавленные наборы'}:
            response.set_tts(message.replace('\n', ' - - ') + ' - '.join(user_storage['suggests'][:-3]) + \
                             "\n. Доступные команды: {}.".format(" - - ".join(user_storage['suggests'][-3:])))
        elif user_storage['suggests'][-2] in {'Ещё', 'Назад', 'Добавленные наборы'}:
            response.set_tts(message.replace('\n', ' - - ') + ' - - '.join(user_storage['suggests'][:-2]) + \
                             "\n. Доступные команды: {}.".format(" - - ".join(user_storage['suggests'][-2:])))
        else:
            response.set_tts(message.replace('\n', ' - ') + ' - - '.join(user_storage['suggests'][:-1]) + \
                             "\n. Доступные команды: {}.".format(" - - ".join(user_storage['suggests'][-1:])))
    buttons, user_storage = get_suggests(user_storage)
    response.set_buttons(button)
    return response, user_storage


def handle_dialog(request, response, user_storage, database, morph):
    from random import choice
    if not user_storage:
        user_storage = {"suggests": []}
    input_message = request.command.lower()
    input_message = input_message.replace("'", "`")
    input_message = input_message.replace('ё', 'е')
    user_id = request.user_id
    user_storage['suggests'] = [
        "Словарь",
        "Тренировка",
        "Наборы слов",
        "Помощь",
        "Настройки"
    ]
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
            if input_message != 'у человека нет имени':
                database.update_entries('users_info', user_id, {'Named': True}, update_type='rewrite')
                user_storage["name"] = request.command
                database.update_entries('users_info', user_id, {'Name': input_message.capitalize()},
                                        update_type='rewrite')
            else:
                database.update_entries('users_info', user_id, {'Named': True}, update_type='rewrite')
                user_storage["name"] = request.command
                database.update_entries('users_info', user_id, {'Name': 'Noname'}, update_type='rewrite')

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
            elif input_message == 'оставь имя "саша"':
                database.update_entries('users_info', user_id, {'Named': True}, update_type='rewrite')
                user_storage["name"] = request.command
                database.update_entries('users_info', user_id, {'Name': 'Саша'},
                                        update_type='rewrite')
            else:
                output_message = 'Хорошо, назови свое имя.'
                mode = "-2"
                update_mode(user_id, mode, database)
                buttons, user_storage = get_suggests({'suggests': ['У человека нет имени']})
                return message_return(response, user_storage, output_message, buttons, database, request, mode)

        output_message = choice(aliceAnswers["helloTextVariations"])
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
            buttons = ['Режим перевода', 'Сменить имя', 'В начало']
        else:
            buttons = ['Режим перевода', 'Сменить имя', 'Очистить словарь', 'В начало']
        buttons, user_storage = get_suggests({'suggests': buttons})
        return message_return(response, user_storage, output_message, buttons, database, request,
                              mode)

    if input_message in {'сменить имя', 'поменять имя', 'установить другое имя'} and mode == 'settings':
        mode = 'change_name'
        output_message = 'Введи новое имя.'
        buttons, user_storage = get_suggests({'suggests' : ['У человека нет имени', 'Отмена']})
        return message_return(response, user_storage, output_message, buttons, database, request,
                              mode)

    if input_message == 'саша' and mode == 'change_name':
        output_message = 'Обрати внимание, имя "Саша" будет восприниматься как женское.' \
                         ' Если тебе это не нравится, могу звать тебя Алекс или Александр.'
        mode = 'sasha_name'
        buttons, user_storage = get_suggests({'suggests': ['Оставь имя "Саша"', 'Зови меня Алекс',
                                                           'Зови меня Александр', 'Установить другое имя', 'Отмена']})

    if mode == 'sasha_name' and input_message != 'отмена' and 'начал' not in input_message:
        if input_message == 'оставь имя "саша"':
            output_message = 'Хорошо, буду звать тебя Саша.'
        elif input_message == 'зови меня александр':
            output_message = 'Хорошо, буду звать тебя Александр.'
        elif input_message == 'зови меня алекс':
            output_message = 'Хорошо, буду звать тебя Алекс.'
        else:
            mode = 'change_name'
            output_message = 'Введи новое имя.'
            buttons, user_storage = get_suggests({'suggests': ['У человека нет имени', 'Отмена']})
            return message_return(response, user_storage, output_message, buttons, database, request,
                                  mode)
        mode = ''
        buttons, user_storage = get_suggests(user_storage)
        return message_return(response, user_storage, output_message, buttons, database, request,
                              mode)

    if input_message in {'переводчик', 'режим перевода', 'режим переводчика'} and  mode == 'settings':
        mode = 'translator_inf'
        output_message = 'В режиме переводчика я смогу только переводить и добавлять в словарь.'
        buttons, user_storage = get_suggests({'suggests' : ['Включить режим', 'В начало']})
        return message_return(response, user_storage, output_message, buttons, database, request,
                              mode)

    if ((input_message.startswith('включи') and mode == 'translator_inf') or
            (mode.startswith('translator') and mode != 'translator_inf')) and \
            (input_message[0] != '+' and input_message not in {'в начало', 'начало', 'сначала'}):
        if mode == 'translator_inf':
            mode = 'translator'
            output_message = 'Ок, включила режим переводчика. Просто скажи "В начало", когда закончишь.'
            buttons, user_storage = get_suggests({'suggests': ['В начало']})
            return message_return(response, user_storage, output_message, buttons, database, request,
                                  mode)
        else:
            if language_match('t', input_message):
                translation = ''.join(translate_text(input_message, 'ru-en'))
            elif language_match('г', input_message):
                translation = ''.join(translate_text(input_message, 'en-ru'))
            else:
                output_message = 'Не поняла, что вы хотите перевести'
                buttons, user_storage = get_suggests({'suggests' : ['В начало']})
                return message_return(response, user_storage, output_message, buttons, database, request,
                                      mode)

            output_message = '\nВот что я нашла:\n{} - {}'.format(input_message.capitalize(),
                                                                             translation.capitalize())
            buttons, user_storage = get_suggests(
                {'suggests': ['+ {} {}'.format(input_message.capitalize(), translation.capitalize()), 'В начало']})
            return message_return(response, user_storage, output_message, buttons, database, request,
                                  mode)


    if input_message == 'у человека нет имени' and mode == 'change_name':
        mode = ''
        output_message = 'Поняла вас, Сэр!'
        database.update_entries('users_info', user_id, {'Name': 'Noname'}, update_type='rewrite')
        buttons, user_storage = get_suggests(user_storage)
        return message_return(response, user_storage, output_message, buttons, database, request,
                              mode)


    if mode == 'change_name':
        mode = ''
        output_message = 'Хорошо, буду называть тебя {}!'.format(input_message.capitalize())
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
            output_message = '{}, в твоем словаре {} слов'.format(name, count)\
                             + ending(count)+"."
        else:
            output_message = 'В твоем словаре {} слов'.format(count) + ending(count)+"."
        if count == 0:
            mode = ''
            output_message += '\nТы можешь добавить в словарь готовые наборы слов'
            buttons, user_storage = get_suggests({'suggests': ['Наборы слов', 'В начало']})
        else:
            buttons, user_storage = get_suggests({'suggests': ['Неизученные слова', 'Изученные слова', 'В начало']})
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

    if input_message == 'тренировка' and mode == '':
        update_mode(user_id, 'training', database)
        mode = 'training'
        update_stat_session('training', [0, 0], user_id, database)

    if ("помощь" in input_message or "что ты умеешь" in input_message) and mode == '':
        output_message = "Благодаря данному навыку ты можешь учить английский так, как тебе хочется! Ты можешь " \
                         "добавить слова, которые хочешь выучить, используя удобные тебе ассоциации, или же выбрать " \
                         "набор из доступных категорий, после чего испытать свои силы в тренировке!"
        buttons, user_storage = get_suggests({'suggests': ['Как добавлять слова?', 'Как удалять слова?', 'Справка о тренировках', 'Что делать?',
                                                           'В начало']})
        mode = 'help'
        return message_return(response, user_storage, output_message, buttons, database, request,
                              mode)

    if input_message in {'справка', 'справка о тренировках'} and mode == 'help':
        output_message = 'У каждого слова есть его прогресс, изначально равный нулю. ' \
                         'После каждого правильного ответа на вопрос прогресс соответствующего слова увеличивается на 1, ' \
                         'после неправильного - уменьшается на 2, но не опускается ниже нуля. ' \
                         'Слово считается изученным, если его прогресс больше либо равен 4\n' \
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
                         ' слова в словарь используй команды, например, "Добавь слово hello привет".\nПолный список' \
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
                         'hello".\nПолный список команд для этого: -; Del; Удали; Очисть словарь.'
        buttons, user_storage = get_suggests(
            {'suggests': ['Как добавлять слова?', 'Что делать?', 'В начало']})
        return message_return(response, user_storage, output_message, buttons, database, request,
                              mode)

    if input_message in {'что делать?', 'что делать'} and mode == 'help':
        output_message = 'Учить английский!\nОднажды я тоже задавался таким вопросом. '\
                         'В итоге прочитал Н.Г. Чернышевского "Что делать?" и начал учить английский!'
        mode = ''
        buttons, user_storage = get_suggests(user_storage)
        return message_return(response, user_storage, output_message, buttons, database, request,
                              mode)


    if (input_message in {'наборы слов', 'набор слов'} and mode == '') or (input_message == 'назад' and mode == 'add_set 2'):
        added = get_word_sets(user_id, database)
        sets = sorted(list(set(list(words.keys())).difference(added)))
        if len(sets) == 0:
            gender = get_gender(user_id, database, morph)
            print(gender)
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
        print(gender)
        if gender == "masc" or str(gender) == "Noname":
            output_message = choice(['Вот наборы, которые ты еще не добавил.', "Посмотри ещё недобавленные наборы."])\
                             + ('\nСтраница 1 из {}'.format((len(sets) + 3) // 4)
                             if (len(sets) + 3) // 4 > 1 else '')
        else:
            output_message = choice(['Вот наборы, которые ты еще не добавила.', "Посмотри ещё недобавленные наборы."]) \
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
            dictionary = del_word(word.capitalize(), user_id, database)
            if dictionary != 'no such word' and dictionary:
                update_dictionary(user_id, dictionary, database)
        buttons, user_storage = get_suggests(user_storage)
        output_message = 'Удалила. Что будем делать?'
        mode = ''
        added = get_word_sets(user_id, database)
        added.remove(input_message.capitalize())
        update_word_sets(user_id, added, database)
        return message_return(response, user_storage, output_message, buttons, database, request,
                              mode)


    if input_message.capitalize() in words and mode.startswith('add_set'):
        for word, translate in words[input_message.capitalize()].items():
            dictionary = add_word(word, translate, user_id, database)
            if dictionary != 'already exists' and dictionary:
                update_dictionary(user_id, dictionary, database)
        buttons, user_storage = get_suggests(user_storage)
        output_message = 'Добавила, теперь потренируемся?'
        mode = ''
        added = get_word_sets(user_id, database)
        added.add(input_message.capitalize())
        update_word_sets(user_id, added, database)
        return message_return(response, user_storage, output_message, buttons, database, request,
                              mode)

    if mode != '' and mode[0] == '!' and input_message[0] != '+':
        success = add_word(''.join(mode[1:]), input_message, user_id, database)
        answer = ''.join(mode[1:]), input_message
        answer = list(map(lambda x: x.capitalize(), answer))
        if language_match(answer[0], answer[1]) == 'miss':
            answer = answer[::-1]
        if success == 'already exists':
            output_message = choice(['В Вашем словаре уже есть такой перевод.', 'Словарь уже содержит такой перевод.',
                                     'Такой перевод уже есть в Вашем словаре.'])
        elif not success:
            output_message = 'Пара должна состоять из русского и английского слова.'
        else:
            output_message = 'Слово "{}" с переводом "{}" добавлено в Ваш словарь.'.format(answer[0], answer[1])
            update_dictionary(user_id, success, database)
        buttons, user_storage = get_suggests(user_storage)
        mode = ''
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
        elif not success:
            output_message = 'Пара должна состоять из русского и английского слова.'
        else:
            output_message = 'Слово "{}" с переводом "{}" добавлено в Ваш словарь.'.format(answer[0], answer[1])
            update_dictionary(user_id, success, database)
        if mode == 'training' :
            output_message += '\nРежим тренировки автоматически завершен.'
            stat = get_stat_session('training', user_id, database)
            output_message += '\nТы ответил на {} из {} моих вопросов.'.format(stat[1], stat[0])
            update_mode(user_id, mode, database)
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
            translation = ''.join(translate_text(answer, 'ru-en'))
        elif language_match('г', answer):
            translation = ''.join(translate_text(answer, 'en-ru'))
        else:
            output_message = 'Не поняла, что вы хотите перевести.'
            mode = ''
            buttons, user_storage = get_suggests(user_storage)
            return message_return(response, user_storage, output_message, buttons, database, request,
                                  mode)
        if answer.count(' ') > 0:
            output_message = 'Попробую перевести Ваше предложение...'
        else:
            output_message = 'Попробую перевести Ваще слово...'
        output_message += '\nВот что у меня получилось:\n{} - {}'.format(answer.capitalize(), translation.capitalize())
        mode = '!' + answer
        output_message += '\nВы также можете сказать или написать свой перевод, он будет добавлен в словарь.'
        buttons, user_storage = get_suggests({'suggests' : ['+ {} {}'.format(answer.capitalize(), translation.capitalize()), 'В начало']})
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
                                                    mode == 'sasha_name'):
        buttons, user_storage = get_suggests(user_storage)
        output_message = 'Ок, начнем с начала ;)'
        mode = ''
        return message_return(response, user_storage, output_message, buttons, database, request,
                              mode)

    elif handle == 'use_mode':
        if get_mode(user_id, database) == 'training':
            output_message = training.main(get_q(user_id, database), answer, 'revise&next', user_id, database)
            if get_mode(user_id, database) == 'training':
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
        choice = random.choice(aliceAnswers["quitTextVariations"])
        response.set_text(choice)
        response.set_tts(choice, True)
        response.end_session = True
        return response, user_storage

    buttons, user_storage = get_suggests(user_storage)
    mode = ''
    update_mode(user_id, mode, database)
    return IDontUnderstand(response, user_storage, aliceAnswers["cantTranslate"])
