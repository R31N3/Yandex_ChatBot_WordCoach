from little_fuctions import *
from random import randint

def revise(q, answer, q_type, id, database):
    dictionary = get_dictionary(id, database)
    progress = get_progress_mode_x('training', id, database)
    if q_type == 'translate_to_rus':
        if answer in dictionary['to_learn'][q]:
            return True
        else:
            return False

def inf():
    return 'Тренируй, не ной'

def get_question(id, database):
    dictionary = get_dictionary(id, database)
    if randint(0, 10) <= 2:
        key = 'learned'
    else:
        key = 'to_learn'
    index_word = randint(0, len(list(dictionary[key].keys())) - 1)
    if randint(0, 1) == 0:
        return list(dictionary[key].keys())[index_word]
    else:
        word = list(dictionary[key].keys())[index_word]
        return ' '.join(dictionary[key][word])


def main(q, answer, q_type, id, database):
    if answer == 'help' or answer == 'помощь':
        return inf()
    elif q_type == 'begin':
        return get_question(id, database)
    elif q_type == 'revise&next':
        if revise(q, answer, q_type, id, database):
            score = get_progress_mode_x('training', id, database)
            score[q] += 1
            update_progress('training', id, score, database)
            if score[q] >= 4:
                dictionary = get_dictionary(id, database)
                updated = False
                if q not in dictionary['learned']:
                    dictionary['learned'][q] = dictionary['to_learn'][q]
                    updated = True
                if q in dictionary['to_learn']:
                    dictionary['to_learn'].pop(q, None)
                    updated = True
                if updated:
                    update_dictionary(id, dictionary, database)
            return 'Верно! ' + get_question(id, database)
        else:
            score = get_progress_mode_x('training', id, database)
            score[q] = max(0, score[q] - 2)
            update_progress('training', id, score, database)
            if score[q] < 4:
                dictionary = get_dictionary(id, database)
                updated = False
                if q in dictionary['learned']:
                    dictionary['to_learn'][q] = dictionary['learned'][q]
                    dictionary['learned'].pop(q)
                    updated = True
                if updated:
                    update_dictionary(id, dictionary, database)
            return 'Неверно' + get_question(id, database)
    elif q_type == 'end':
        return 'Хорошо поиграли!\nТы ответил на {} из {} моих вопросов'.format(*get_stat_session('training', id, database))
    else:
        return False