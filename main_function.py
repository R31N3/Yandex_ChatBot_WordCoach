# coding: utf-8
from __future__ import unicode_literals
import random
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
    response.set_text(message)
    if mode != 'training':
        response.set_tts(message.replace('\n', '. ') + "\n. Доступные команды: {}.".format(", ".join(user_storage['suggests'])))
    else:
        response.set_tts(message.replace('\n', '. ') + "\n. Варианты ответа: {}".format(", ".join(user_storage['suggests'][:-1])))
    buttons, user_storage = get_suggests(user_storage)
    response.set_buttons(button)
    return response, user_storage


def handle_dialog(request, response, user_storage, database):
    if not user_storage:
        user_storage = {"suggests": []}
    input_message = request.command.lower()
    input_message = input_message.replace("'", "`")
    input_message = input_message.replace('ё', 'е')
    user_id = request.user_id
    user_storage['suggests'] = [
        "Помощь",
        "Словарь",
        "Тренировка",
        "Наборы слов"
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
                             "Введите ваше имя"
            response.set_text(output_message)
            response.set_tts(output_message)
            database.add_entries("users_info", {"request_id": user_id})
            mode = "-2"
            update_mode(user_id, mode, database)
            return response, user_storage
        mode = database.get_entry("users_info", ['mode'], {'request_id': user_id})[0][0]
        if mode == "-2":
            database.update_entries('users_info', user_id, {'Named': True}, update_type='rewrite')
            user_storage["name"] = request.command
            database.update_entries('users_info', user_id, {'Name': input_message}, update_type='rewrite')

        output_message = random.choice(aliceAnswers["helloTextVariations"]).capitalize()
        mode = ""
        buttons, user_storage = get_suggests(user_storage)
        return message_return(response, user_storage, output_message, buttons, database, request, mode)

    mode = get_mode(user_id, database)

    if input_message in {'словарь', 'словарик'} and mode == '':
        dictionary = get_dictionary(user_id, database)
        output_message = 'Слов в словаре: {}'.format(len(dictionary['to_learn']) + len(dictionary['learned']))
        buttons, user_storage = get_suggests({'suggests': ['Неизученные слова', 'Изученные слова', 'Очисть словарь', 'В начало']})
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

    if input_message in {'очисть словарь', 'почисть словарь', 'очисть слова', 'почисть слова'}\
            and (mode == '' or mode == '0_dict'):
        update_dictionary(user_id, {'to_learn': {}, 'learned': {}}, database)
        output_message = 'Ваш словарь теперь пустой :)'
        buttons, user_storage = get_suggests(user_storage)
        mode = ''
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
        buttons, user_storage = get_suggests({'suggests': ['Как добавлять слова?', 'Как удалять слова?', 'Что делать?',
                                                           'В начало']})
        mode = 'help'
        return message_return(response, user_storage, output_message, buttons, database, request,
                              mode)

    if input_message in {'как добавлять слова?', 'как добавить слова?', 'как добавить слово?',
                         'как добавлять слова', 'как добавить слова', 'как добавить слово'} \
                        and mode == 'help':
        output_message = "Для занесения" \
                         " слова в словарь используй команды, например, 'Добавь слово hello привет'.\nПолный список" \
                         " команд для этого: +; Аdd; Добавь слово; Добавь. \n А также ты можешь добавлять стандартные" \
                         "наборы слов из доступных категорий."
        buttons, user_storage = get_suggests(
            {'suggests': ['Как удалять слова?', 'Что делать?', 'В начало']})
        return message_return(response, user_storage, output_message, buttons, database, request,
                              mode)

    if input_message in {'как удалять слова?', 'как удалить слово?', 'как удалить слова?',
                         'как удалять слова', 'как удалить слово', 'как удалить слова'}\
                        and mode == 'help':
        output_message = "Ты можешь полностью очистить " \
                         "свой словарь или же удалить из него отдельное слово, используя, например, команду 'Удали" \
                         "hello'.\nПолный список команд для этого: -; Del; Удали; Очисть словарь."
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

    if input_message in {'в начало', 'начало'} and (mode == 'help' or mode.startswith('add_set') or mode == '' or mode.endswith('_dict') or mode.endswith('_dict_n')):
        buttons, user_storage = get_suggests(user_storage)
        output_message = 'Ок, начнем с начала ;)'
        mode = ''
        return message_return(response, user_storage, output_message, buttons, database, request,
                              mode)

    if (input_message in {'наборы слов', 'набор слов'} and mode == '') or (input_message == 'назад' and mode == 'add_set 2'):
        output_message = 'Ты можешь добавить наборы слов по следующим тематикам.'\
                         + '\nСтраница 1 из {}'.format((len(list(words.keys())) + 3) // 4)\
                         if (len(list(words.keys())) + 3) // 4 > 1 else ''
        butts = {'suggests': list(words.keys())[0:4] + (['Ещё'] if len(list(words.keys())) > 4 else [])}
        butts['suggests'].append('В начало')
        buttons, user_storage = get_suggests(butts)
        mode = 'add_set 1'
        return message_return(response, user_storage, output_message, buttons, database, request,
                              mode)

    if input_message in {'еще', 'дальше'} and mode.startswith('add_set'):
        next_page = int(mode.split()[1]) + 1
        output_message = 'Ты можешь добавить наборы слов по следующим тематикам.' \
                         + '\nСтраница {} из {}'.format(next_page, (len(list(words.keys())) + 3) // 4)
        butts = {'suggests': list(words.keys())[next_page * 4 - 4:next_page * 4] + \
                             ['Назад'] + \
                             (['Ещё'] if len(list(words.keys())) - 4 * (next_page - 1) > 4 else [])}
        butts['suggests'].append('В начало')
        buttons, user_storage = get_suggests(butts)
        mode = 'add_set {}'.format(next_page)
        return message_return(response, user_storage, output_message, buttons, database, request,
                              mode)

    if input_message == 'назад' and mode.startswith('add_set'):
        next_page = int(mode.split()[1]) - 1
        output_message = 'Ты можешь добавить наборы слов по следующим тематикам.' \
                         + '\nСтраница {} из {}'.format(next_page, (len(list(words.keys())) + 3) // 4)
        butts = {'suggests': list(words.keys())[next_page * 4 - 4:next_page * 4] + \
                             ['Назад'] + \
                             (['Ещё'] if len(list(words.keys())) - 4 * (next_page - 1) > 4 else [])}
        butts['suggests'].append('В начало')
        buttons, user_storage = get_suggests(butts)
        mode = 'add_set {}'.format(next_page)
        return message_return(response, user_storage, output_message, buttons, database, request,
                              mode)

    if input_message.capitalize() in words and mode.startswith('add_set'):
        for word, translate in words[input_message.capitalize()].items():
            dictionary = add_word(word, translate, user_id, database)
            if dictionary != 'already exists' and dictionary:
                update_dictionary(user_id, dictionary, database)
        buttons, user_storage = get_suggests(user_storage)
        output_message = 'Добавил, теперь потренируемся?'
        mode = ''
        return message_return(response, user_storage, output_message, buttons, database, request,
                              mode)

    update_mode(user_id, mode, database)

    if input_message in ['нет', 'не хочется', 'в следующий раз', 'выход', "не хочу", 'выйти']:
        choice = random.choice(aliceAnswers["quitTextVariations"])
        response.set_text(choice)
        response.set_tts(choice, True)
        response.end_session = True
        return response, user_storage

    answer = classify(input_message, mode)
    handle = answer['class']
    warning = answer['warning']
    answer = answer['answer']

    if handle == "add":
        success = add_word(answer[0], answer[1], user_id, database)
        if language_match(answer[0], answer[1]) == 'miss':
            answer = answer[::-1]
        if success == 'already exists':
            output_message = 'В Вашем словаре уже есть такой перевод.'
        elif not success:
            output_message = 'Пара должна состоять из русского и английского слова.'
        else:
            output_message = "Слово {} добавлено с переводом {} добавлено в Ваш словарь.".format(answer[0], answer[1])
            update_dictionary(user_id, success, database)
        buttons, user_storage = get_suggests(user_storage)
        if warning:
            output_message += '\nРежим тренировки автоматически завершен.'
            mode = ''
            update_mode(user_id, mode, database)
        return message_return(response, user_storage, output_message, buttons, database, request,
                              mode)

    elif handle == 'del':
        success = del_word(answer.strip(), user_id, database)
        if success == 'no such word':
            output_message = 'В Вашем словаре нет такого слова.'
        elif not success:
            output_message = 'Слово должно быть русским или английским.'
        else:
            output_message = 'Слово {} удалено из Вашего словаря.'.format(answer)
            update_dictionary(user_id, success, database)
        buttons, user_storage = get_suggests(user_storage)
        if warning:
            output_message += '\nРежим тренировки автоматически завершен.'
            mode = ''
            update_mode(user_id, mode, database)
        return message_return(response, user_storage, output_message, buttons, database, request,
                              mode)

    elif handle == 'use_mode':
        if get_mode(user_id, database) == 'training':
            output_message = training.main(get_q(user_id, database), answer, 'revise&next', user_id, database)
            if get_mode(user_id, database) == 'training':
                but = training.get_buttons(get_q(user_id, database), user_id, database)
                stor = {'suggests': but + ['Закончить тренировку']}
            else:
                stor = {'suggests': user_storage['suggests']}
                update_mode(user_id, '', database)
            buttons, user_storage = get_suggests(stor)
            mode = get_mode(user_id, database)
            return message_return(response, user_storage, output_message, buttons, database, request,
                              mode)

    buttons, user_storage = get_suggests(user_storage)
    mode = ''
    update_mode(user_id, mode, database)
    return IDontUnderstand(response, user_storage, aliceAnswers["cantTranslate"])
