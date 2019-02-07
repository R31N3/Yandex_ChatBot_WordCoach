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

def name(id, database):
    if named:
        return True #name вытащить из database
    else:
        return False #noname


def language_match(word, translate):
    if set(list(word)).intersection(set(list('abcdefghijklmnopqrstuvwxyz'))) \
        and  set(list(translate)).intersection(set(list('абвгдеёжзийклмнопрстуфхцчшщъыьэюя'))):
        return True
    elif set(list(translate)).intersection(set(list('abcdefghijklmnopqrstuvwxyz'))) \
        and  set(list(word)).intersection(set(list('абвгдеёжзийклмнопрстуфхцчшщъыьэюя'))):
        return 'miss'
    else:
        return False #(word, translate) is neither (rus, eng) nor (eng, rus)


def add_word(word, translate, id, database):
    if language_match(word, translate) == False:
        return False #incorrect format
    elif language_match(word, translate) == 'miss':
        word, translate = translate, word
    dictionary = get_dictionary(id, database)
    dictionary['learned'].pop(word, None)
    if word in dictionary['to_learn']:
        if translate not in dictionary['to_learn'][word]:
            dictionary['to_learn'][word].append(translate)
            return dictionary
        else:
            return 'already exists'
    else:
        dictionary['to_learn'][word] = [translate]
    return dictionary
    pass


def del_word(word, id, database):
    if language_match(word, 'г'):
        dictionary = get_dictionary(id, database)
        if word in dictionary['to_learn'] or word in dictionary['learned']:
            dictionary['to_learn'][word] = None
            dictionary['learned'][word] = None
            return dictionary
        else:
            return 'no such word'
    elif language_match('v', word):
        dictionary = get_dictionary(id, database)
        found = False
        for eng, translates in dictionary['to_learn'].items():
            if word in translates:
                dictionary['to_learn'][eng].remove(word)
                found = True
        for eng, translates in dictionary['to_learn'].items():
            if word in translates:
                dictionary['to_learn'][eng].remove(word)
                found = True
        if found:
            return dictionary
        else:
            return 'no such word'
    else:
        return False #word is neither eng nor rus
    pass


def change_mode(mode, id, database):
    pass


def get_dictionary(id, database):

    eng_words = database.get_entry("users_info", ['eng_words'], {'request_id': id})[0][0].split("#$")
    words_to_learn = {}
    rus_words = database.get_entry("users_info", ['rus_words'], {'request_id': id})[0][0].split("#$")
    for i in range(len(eng_words)):
        words_to_learn[eng_words[i]] = rus_words[i].split("$%")

    learned_eng_words = database.get_entry("users_info", ['learned_eng_words'], {'request_id': id})[0][0].split("#$")
    learned_words = {}
    learned_rus_words = database.get_entry("users_info", ['learned_rus_words'], {'request_id': id})[0][0].split("#$")
    for i in range(len(learned_eng_words)):
        learned_words[learned_eng_words[i]] = learned_rus_words[i].split("$%")

    dct = {
        "to_learn": words_to_learn,
        "learned": learned_words
    }

    return dct


def get_progress_mode_x(x, id, database):
    pass


def get_stat(id, database, modes_count):
    for x in range(1, modes_count + 1):
        yield (x, get_progress_mode_x(x, id, database))
    dictionary = get_dictionary(id, database)
    yield ('learned', len(dictionary['learned'].keys()))
    yield ('to_learn', len(dictionary['to_learn'].keys()))
    pass

def update_dictionary(id, words_to_add):
    pass