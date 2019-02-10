from little_fuctions import *
from random import randint

def get_ans(q, id, database):
    dictionary = get_dictionary(id, database)
    for k in ['to_learn', 'learned']:
        if q in dictionary[k]:
            return ' '.join(dictionary[k][q])
        else:
            for key in dictionary[k].keys():
                if q in dictionary[k][key]:
                    return key
    return False


def revise(q, answer, q_type, id, database):
    if answer == get_ans(q, id, database):
        return True
    else:
        return False

def inf():
    return 'Тренируй, не ной'

def get_buttons(q, id, database):
    if q == '###empty':
        return ['add I Я', 'add Яблоко Apple', 'Закончить тренировку']
    ans = get_ans(q, id, database)
    dictionary = get_dictionary(id, database)
    if language_match(q, 'г'):
        words = {'рыба', 'картошка', 'трава', 'макароны'}
        for k in ('to_learn', 'learned'):
            for rus_words in dictionary[k].values():
                words = words.union(set(rus_words))
        words = list(words)
        output = [words[0], words[randint(1, len(words) - 1)], words[randint(1, len(words) - 1)]]
        while len(set(output)) != 3:
            output = [words[0], words[randint(1, len(words) - 1)], words[randint(1, len(words) - 1)]]
        output.insert(randint(0, 3), ans)
        return output
    elif language_match('f', q):
        words = {'fish', 'potato', 'grass', 'pasta'}
        words = words.union(set(list(dictionary['to_learn'].keys())))
        words = words.union(set(list(dictionary['learned'].keys())))
        words = list(words)
        words.remove(get_ans(q, id, database))
        output = [words[0], words[randint(1, len(words) // 2 - 1)], words[randint(1, len(words) - 1)]]
        output.insert(randint(0, 2), ans)
        return output

def get_question(id, database):
    dictionary = get_dictionary(id, database)
    k = randint(0, 10)
    if len(dictionary['learned']) == 0:
        k = 5
    elif len(dictionary['to_learn']) == 0:
        k = 1
    if k <= 2:
        key = 'learned'
    else:
        key = 'to_learn'
    index_word = randint(0, len(list(dictionary[key].keys())) - 1)
    if randint(0, 1) == 0:
        update_q(id, list(dictionary[key].keys())[index_word], database)
        return list(dictionary[key].keys())[index_word]
    else:
        word = list(dictionary[key].keys())[index_word]
        update_q(id, ' '.join(dictionary[key][word]), database)
        return ' '.join(dictionary[key][word])

def random_true(id, database):
    return ['Правильно', 'Верно', 'Так держать', 'Вперед'][randint(0, 3)] + (', ' + get_name(id, database)) * randint(0, 1) + '!'

def random_false(id, database):
    return ['Не совсем так, но ты точно справишься в следующий раз', 'Неверно, но я в тебя верю', 'Попробуй еще', 'У тебя получится'][randint(0, 3)] + (', ' + get_name(id, database)) * randint(0, 1) + '!'

def main(q, answer, q_type, id, database):
    if answer == 'help' or answer == 'помощь':
        return inf()
    elif answer == 'end' or answer == 'закончить' or answer == 'закончить тренировку':
        update_mode(id, 'end_training', database)
        q_count, q_true = get_stat_session('training', id, database)
        if q_count != 0:
            q_count -= 1
        return 'Хорошо поиграли! Вы ответили на {} из {} моих вопросов'.format(q_true, q_count)
    elif get_stat_session('training', id, database) == [0, 0]:
        stat_session = get_stat_session('training', id, database)
        dictionary = get_dictionary(id, database)
        if len(dictionary['to_learn'].keys()) + len(dictionary['learned'].keys()) == 0:
            update_q(id, '###empty', database)
            return 'Словарь пуст. Для начала - добавьте в него слова.'
        stat_session[0] += 1
        update_stat_session('training', stat_session, id, database)
        return 'В этом режиме нужно переводить слова из вашего словаря :)\n' + get_question(id, database)
    elif q_type == 'revise&next':
        stat_session = get_stat_session('training', id, database)
        stat_session[0] += 1
        if revise(q, answer, q_type, id, database):
            if language_match(q, 'f'):
                q = get_ans(q, id, database)
            stat_session[1] += 1
            update_stat_session('training', stat_session, id, database)
            score = get_progress_mode('training', id, database)
            if q in score:
                score[q] += 1
            else:
                score[q] = 0
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
            return random_true(id, database) + '\n' + get_question(id, database)
        else:
            update_stat_session('training', stat_session, id, database)
            score = get_progress_mode('training', id, database)
            if language_match(q, 'f'):
                q = get_ans(q, id, database)
            if q in score:
                score[q] = max(0, score[q] - 2)
            else:
                score[q] = 0
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
            return random_false(id, database) + '\nПравильный ответ: {}\n'.format(get_ans(q, id, database)) + get_question(id, database)
    else:
        return False