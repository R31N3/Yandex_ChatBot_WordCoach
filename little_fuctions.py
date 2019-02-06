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
    pass
    #return {'learned': {word: [translate1, translate2], word: [translate1, translate2]},
    #        'to_learn': {word: [translate1, translate2], word: [translate1, translate2]}}


def get_progress_mode_x(x, id, database):
    pass


def get_stat(id, database):
    for x in range(1, len(modes) + 1):
        yield (x, get_progress_mode_x(x, id, database))
    dictionary = get_dictionary(id, database)
    yield ('learned', len(dictionary['learned'].keys()))
    yield ('to_learn', len(dictionary['to_learn'].keys()))
    pass

def update_dictionary(id, dictionary):
    pass