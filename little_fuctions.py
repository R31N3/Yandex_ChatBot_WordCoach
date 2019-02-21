def timer(executable_function):  # декоратор, честно скопированный с habrahabr.ru и чуток доделанный
    import time

    def decorate(*args, **kwargs):
        time_point = time.time()
        result = executable_function(*args, **kwargs)
        print('Время выполнения функции "{}": {:f} секунд'
              .format(executable_function.__name__, time.time() - time_point))
        return result
    return decorate


def smart_timeout(timeout: int = 0.34):
    import time

    def wrap(executable_function):
        def decorate(*args, **kwargs):
            start_time = time.time()
            result = executable_function(*args, **kwargs)
            if time.time() - start_time < timeout:
                time.sleep(timeout - (time.time() - start_time))
            return result
        return decorate
    return wrap


def error_protection(executable_function):
    import time

    def decorate(*args, **kwargs):
        try:
            result = executable_function(*args, **kwargs)
        except Exception as exc:
            print("==========\nError:\n{}\nDate: {}\n=========="
                  .format(exc, time.strftime("%H.%M.%S - %d.%m.%Y", time.localtime())))
        else:
            return result
    return decorate


def language_match(word, translate):
    word, translate = word.lower(), translate.lower()
    if set(list(word)).intersection(set(list('abcdefghijklmnopqrstuvwxyz'))) \
        and set(list(translate)).intersection(set(list('абвгдеёжзийклмнопрстуфхцчшщъыьэюя')))\
        and not set(list(translate)).intersection(set(list('abcdefghijklmnopqrstuvwxyz')))\
        and not set(list(word)).intersection(set(list('абвгдеёжзийклмнопрстуфхцчшщъыьэюя'))):
        return True
    elif set(list(translate)).intersection(set(list('abcdefghijklmnopqrstuvwxyz'))) \
        and set(list(word)).intersection(set(list('абвгдеёжзийклмнопрстуфхцчшщъыьэюя')))\
        and not set(list(word)).intersection(set(list('abcdefghijklmnopqrstuvwxyz')))\
        and not set(list(translate)).intersection(set(list('абвгдеёжзийклмнопрстуфхцчшщъыьэюя'))):
        return 'miss'
    else:
        return False # (word, translate) is neither (rus, eng) nor (eng, rus)


def add_word(word, translate, id, database):
    if not language_match(word, translate):
        return False # incorrect format
    elif language_match(word, translate) == 'miss':
        word, translate = translate, word
    word, translate = word.capitalize(), translate.capitalize()
    dictionary = get_dictionary(id, database)
    dictionary['learned'].pop(word, None)
    ans = 0
    for k in ['to_learn', 'learned']:
        for words in dictionary[k].values():
            if translate in words:
                ans += 1
    if ans > 0:
        return 'rus_exist'
    if word in dictionary['to_learn']:
        if translate not in dictionary['to_learn'][word]:
            dictionary['to_learn'][word].append(translate)
            return dictionary
        else:
            return 'already exists'
    else:
        dictionary['to_learn'][word] = [translate]
    return dictionary


def del_word(word, id, database):
    if language_match(word, 'г'):
        dictionary = get_dictionary(id, database)
        if word in dictionary['to_learn'] or word in dictionary['learned']:
            dictionary['to_learn'].pop(word, None)
            dictionary['learned'].pop(word, None)
            return dictionary
        else:
            return 'no such word'
    elif language_match('v', word):
        dictionary = get_dictionary(id, database)
        found = False
        for eng in list(dictionary['to_learn'].keys()):
            if word in dictionary['to_learn'][eng]:
                dictionary['to_learn'][eng].remove(word)
                found = True
                if len(dictionary['to_learn'][eng]) == 0:
                    dictionary['to_learn'].pop(eng, None)
        for eng in list(dictionary['learned'].keys()):
            if word in dictionary['learned'][eng]:
                dictionary['learned'][eng].remove(word)
                found = True
                if len(dictionary['learned'][eng]) == 0:
                    dictionary['learned'].pop(eng, None)
        if found:
            return dictionary
        else:
            return 'no such word'
    else:
        return False # word is neither eng nor rus


def name(id, database):
    name = get_name(id, database)
    if name == 'Noname':
        return False
    else:
        return name

def get_dictionary(id, database):
    eng_words = database.get_entry("users_info", ['eng_words'], {'request_id': id})[0][0].split("#$")
    words_to_learn = {}
    rus_words = database.get_entry("users_info", ['rus_words'], {'request_id': id})[0][0].split("#$")
    for i in range(len(eng_words)):
        words_to_learn[eng_words[i]] = rus_words[i].split("$%")
    words_to_learn.pop('', None)

    learned_eng_words = database.get_entry("users_info", ['learned_eng_words'], {'request_id': id})[0][0].split("#$")
    learned_words = {}
    learned_rus_words = database.get_entry("users_info", ['learned_rus_words'], {'request_id': id})[0][0].split("#$")
    for i in range(len(learned_eng_words)):
        learned_words[learned_eng_words[i]] = learned_rus_words[i].split("$%")
    learned_words.pop('', None)
    dct = {
        "to_learn": words_to_learn,
        "learned": learned_words
    }
    return dct


def get_progress_mode(mode, id, database):
    if mode == "training":
        dct = {}
        score = database.get_entry("users_info", ['training_score'], {'request_id': id})[0][0].split("#$")
        if score[0]:
            for i in score:
                lst = i.split(":")
                dct[lst[0]] = int(lst[1])
        return dct
    else:
        return False


def update_progress(mode, id, score, database):
    if mode == "training":
        database.update_entries('users_info', id,
                                {'training_score': "#$".join([key+":"+str(score[key]) for key in score.keys()])},
                                update_type='rewrite')


def get_stat(id, database, modes_count = 1):
    for x in range(1, modes_count + 1):
        yield (x, get_progress_mode(x, id, database))
    dictionary = get_dictionary(id, database)
    yield ('learned', len(dictionary['learned'].keys()))
    yield ('to_learn', len(dictionary['to_learn'].keys()))


def update_dictionary(id, words_to_add, database):
    eng_words = []
    rus_words = []
    to_learn = words_to_add["to_learn"]
    for i in to_learn.keys():
        eng_words.append(i)
        rus_words.append("$%".join(to_learn[i]))
    database.update_entries('users_info', id, {'eng_words': "#$".join(eng_words),
                                               'rus_words': "#$".join(rus_words)}, update_type='rewrite')

    learned_eng_words = []
    learned_rus_words = []
    learned = words_to_add["learned"]
    for i in learned.keys():
        learned_eng_words.append(i)
        learned_rus_words.append("$%".join(learned[i]))
    database.update_entries('users_info', id, {'learned_eng_words': "#$".join(learned_eng_words),
                                               'learned_rus_words': "#$".join(learned_rus_words)})

def ending(count):
    if count % 10 == 1:
        return 'о'
    elif 2 <= (count % 10) <=4:
        return 'а'
    else:
        return ''

def envision_dictionary(id, database, to_learn, page):
    dictionary = get_dictionary(id, database)
    dictionary['to_learn'] = dictionary['to_learn'][::-1]
    dictionary['learned'] = dictionary['learned'][::-1]
    s = ''
    if to_learn:
        if page == 1: s += 'Неизучено {} сл+ов'.format(len(dictionary['to_learn'])) + ending(len(dictionary['to_learn']))
        for eng, rus in list(dictionary['to_learn'].items())[page*10 - 10:page*10]:
            s += '\n{} - {}'.format(eng, ', '.join(rus))
        max_page = (len(list(dictionary['to_learn'].items())) + 9) // 10
        s += '\nСтраница {} из {}'.format(page, max_page)
    else:
        if page == 1: s += 'Изучено {} сл+ов'.format(len(dictionary['learned'])) + ending(len(dictionary['learned']))
        for eng, rus in list(dictionary['learned'].items())[page*10 - 10:page*10]:
            s += '\n{} - {}'.format(eng, ', '.join(rus))
        max_page = (len(list(dictionary['learned'].items())) + 9) // 10
        s += '\nСтраница {} из {}'.format(page, max_page)
    return s, max_page


def get_stat_session(mode, id, database):
    if mode == 'training':
        return [database.get_entry("users_info", ['q_count'], {'request_id': id})[0][0],
                database.get_entry("users_info", ['q_true'], {'request_id': id})[0][0]]
    else:
        return False


def update_stat_session(mode, data, id, database):
    if mode == 'training':
        database.update_entries('users_info', id, {'q_count': data[0], 'q_true': data[1]})
        return True
    else:
        return False


def get_suggests(user_storage):
    if "suggests" in user_storage.keys():
        suggests = []
        for suggest in user_storage['suggests']:
            if type(suggest) != list:
                suggests.append({'title': suggest, 'hide': True})
            else:
                print(suggest)
                suggests.append({'title': suggest[0], "url": suggest[1], 'hide': False})
                print(suggests)
    else:
        suggests = []

    return suggests, user_storage


def IDontUnderstand(response, user_storage, answer):
    import random
    message = random.choice(answer)
    response.set_text(message)
    response.set_tts(message + "Доступные команды: {}.".format(" ,".join(user_storage['suggests'])))
    buttons, user_storage = get_suggests(user_storage)
    response.set_buttons(buttons)
    return response, user_storage


def read_answers_data(name):
    import json
    with open(name+".json", encoding="utf-8") as file:
        data = json.loads(file.read())
        return data


aliceAnswers = read_answers_data("data/answers_dict_example")


def get_mode(id, database):
    return database.get_entry("users_info", ['mode'], {'request_id': id})[0][0]


def update_mode(id, mode, database):
    database.update_entries('users_info', id, {'mode': mode}, update_type='rewrite')
    return True


def get_q(id, database):
    return database.get_entry("users_info", ['q'], {'request_id': id})[0][0]


def update_q(id, q, database):
    database.update_entries('users_info', id, {'q': q}, update_type='rewrite')
    return True


def get_name(id, database):
    return database.get_entry("users_info", ['Name'], {'request_id': id})[0][0]


def translate_text(text, lang):
    import requests
    # lang: en-ru - с английского на русский, ru-en - с русского на английский
    try:
        key = "trnsl.1.1.20190206T150145Z.7764248d93f72476.2644ce5f93cfd028b00d8f8fe6f4f1855d7e7b10"
        request = "https://translate.yandex.net/api/v1.5/tr.json/translate?key={}&text={}&lang={}".format(key,
                                                                                                          text, lang)
        response = requests.get(request)

        if response.json()["text"][0] == text:
            return False

        if response:
            return response.json()["text"][0]

        return "Ошибка выполнения запроса:\nHttp статус:", response.status_code, "(", response.reason, \
               ")\n Саша, чини, твой косяк(наверное)"
    except:
        return False


def get_word_sets(id, database):
    sets = set(database.get_entry("users_info", ['word_sets'], {'request_id': id})[0][0].split("#$"))
    return sets if sets != {''} else set()


def update_word_sets(id, word_sets, database):
    database.update_entries('users_info', id, {'word_sets': "#$".join(list(word_sets))}, update_type='rewrite')
    return True


def get_gender(id, database, morph):
    name = database.get_entry("users_info", ['Name'], {'request_id': id})[0][0]
    if name != "Noname":
        gender = morph.parse(name)[0].tag.gender
        gender = gender if gender else "masc"
    else:
        gender = "Noname"
    return gender

def hello(id, database):
    from random import choice
    name = get_name(id, database)
    if name != "Noname":
        return choice(aliceAnswers["helloTextVariations"]["gender"]).format(name)
    return choice(aliceAnswers["helloTextVariations"]["no_gender"])
