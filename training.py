from little_fuctions import *
from random import randint

def get_ans(q, id, database):
    q = q.split('#')[0]
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
    if answer == get_ans(q, id, database) or answer == q[-1]:
        return True
    else:
        return False

def inf():
    return 'Тренируй, не ной'

def get_buttons(q, id, database):
    if q == '###empty':
        update_mode(id, '', database)
        return ['add I Я', 'add Яблоко Apple', 'Наборы слов', 'В начало']
    ans = get_ans(q, id, database)
    dictionary = get_dictionary(id, database)
    if language_match(q, 'г'):
        words = {'Рыба', 'Картошка', 'Трава', 'Макароны'}
        for k in ('to_learn', 'learned'):
            for rus_words in dictionary[k].values():
                words = words.union(set(rus_words))
        words = list(words)
        output = [words[0], words[randint(1, len(words) - 1)], words[randint(1, len(words) - 1)]]
        while len(set(output)) != 3:
            output = [words[randint(0, len(words) - 1)], words[randint(0, len(words) - 1)],
                      words[randint(0, len(words) - 1)]]
        rand = randint(0, 3)
        output.insert(rand, (ans.split())[randint(0, len(ans.split()) - 1)])
        update_q(id, '{}#{}'.format(q, rand + 1), database)
        return output
    elif language_match('f', q):
        words = {'Fish', 'Potato', 'Grass', 'Pasta'}
        words = words.union(set(list(dictionary['to_learn'].keys())))
        words = words.union(set(list(dictionary['learned'].keys())))
        words = list(words)
        words.remove(get_ans(q, id, database))
        output = [words[randint(1, len(words) - 1)], words[randint(1, len(words) - 1)],
                  words[randint(1, len(words) - 1)]]
        while len(set(output)) != 3:
            output = [words[randint(0, len(words) - 1)], words[randint(0, len(words) - 1)],
                      words[randint(0, len(words) - 1)]]
        rand = randint(0, 3)
        output.insert(rand, ans)
        update_q(id, '{}#{}'.format(q, rand + 1), database)
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
        return '\n' + (list(dictionary[key].keys())[index_word]).upper()
    else:
        word = list(dictionary[key].keys())[index_word]
        update_q(id, ' '.join(dictionary[key][word]), database)
        return '\n' + (' '.join(dictionary[key][word])).upper()

def random_true(id, database):
    true_list = ['Правильно', 'Верно', 'Так держать', 'Вперед']
    name = ', ' + get_name(id, database).capitalize() if get_name(id, database).capitalize() != 'Noname' else False
    return true_list[randint(0, len(true_list) - 1)] + (name if name else '') * randint(0, 1) + '!'

def random_false(id, database):
    false_list = ['Не совсем так, но ты точно справишься в следующий раз', 'Неверно, но я в тебя верю', 'Попробуй еще', 'У тебя получится']
    name = ', ' + get_name(id, database).capitalize() if get_name(id, database).capitalize() != 'Noname' else False
    return false_list[randint(0, len(false_list) - 1)] + (name if name else '') * randint(0, 1) + '!'

def main(q, answer, q_type, id, database):
    if answer == 'help' or answer == 'помощь':
        return inf()
    elif answer == 'end' or answer == 'закончить' or answer == 'закончить тренировку':
        update_mode(id, 'end_training', database)
        q_count, q_true = get_stat_session('training', id, database)
        if q_count != 0:
            q_count -= 1
        return 'Хорошо поиграли! Вы ответили на {} из {} моих вопросов.'.format(q_true, q_count)
    elif get_stat_session('training', id, database) == [0, 0]:
        stat_session = get_stat_session('training', id, database)
        dictionary = get_dictionary(id, database)
        if len(dictionary['to_learn'].keys()) + len(dictionary['learned'].keys()) == 0:
            update_q(id, '###empty', database)
            return 'Словарь пуст. Для начала добавьте в него слова.'
        stat_session[0] += 1
        update_stat_session('training', stat_session, id, database)
        return 'В этом режиме нужно переводить слова из вашего словаря :)\n'\
               'Команда "Закончить тренировку" вернет тебя в главное меню\n'\
               'Ты можешь называть ответили номер варианта ответа. Поехали!\n'+ get_question(id, database)
    elif q_type == 'revise&next':
        stat_session = get_stat_session('training', id, database)
        stat_session[0] += 1
        answer = answer.capitalize()
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
                q_eng = get_ans(q, id, database)
            else:
                q_eng = q[:]
            if q_eng in score:
                score[q_eng] = max(0, score[q_eng] - 2)
            else:
                score[q_eng] = 0
            update_progress('training', id, score, database)
            if score[q_eng] < 4:
                dictionary = get_dictionary(id, database)
                updated = False
                if q_eng in dictionary['learned']:
                    dictionary['to_learn'][q_eng] = dictionary['learned'][q_eng]
                    dictionary['learned'].pop(q_eng)
                    updated = True
                if updated:
                    update_dictionary(id, dictionary, database)
            return random_false(id, database) + '\nПравильный ответ: "{}"\n'.format(get_ans(q, id, database)) + get_question(id, database)
    else:
        return False