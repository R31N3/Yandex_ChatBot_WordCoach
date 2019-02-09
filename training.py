from little_fuctions import *

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

def main(q, answer, q_type, id, database):
    if answer == 'help' or answer == 'помощь':
        return inf()
    elif q_type == 'begin':
        return get_question(id, database)
    elif q_type == 'revise&next':
        if revise(q, answer, q_type, id, database):
            score = get_progress_mode_x('training', id, database)
            update_progress('training', id, score, database)
            return 'Верно! ' + get_question(id, database)
        else:
            return 'Неверно' + get_question(id, database)
    elif q_type == 'end':
        return 'Хорошо поиграли!\nТы ответил на {} из {} моих вопросов'.format(*get_stat_session('training', id, database))