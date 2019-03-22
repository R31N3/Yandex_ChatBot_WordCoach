from little_fuctions import *
from random import randint
from random import choice

aliceAnswers = read_answers_data("data/answers_dict_example")

def get_ans(q, id, database):
    q = q.split('#')[0]
    dictionary = get_dictionary(id, database)
    for k in ['to_learn', 'learned']:
        if q in dictionary[k]:
            return ', '.join(dictionary[k][q])
        else:
            for key in dictionary[k].keys():
                if q in ', '.join(dictionary[k][key]):
                    return key
    return False


def revise(q, answer, q_type, id, database):
    print("q, answer, get_ans  ", q, answer, get_ans(q, id, database), answer.lower() == get_ans(q, id, database).lower(), sep = ' : ')
    if answer.lower().strip().replace(',', '') == get_ans(q, id, database).lower().strip().replace(',', '') or answer[0] == q[-1]:
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
        words = {'Рыба', 'Картошка', 'Трава', 'Макароны', 'Синяк', 'Ломоть', 'Машина', 'Фура', 'Тушь', 'Музыкальная труба'}
        for k in ('to_learn', 'learned'):
            for rus_words in dictionary[k].values():
                words.add(', '.join(rus_words))
        words = list(words)
        output = [words[randint(0, len(words) - 1)], words[randint(1, len(words) - 1)], words[randint(1, len(words) - 1)]]
        rand = randint(0, 3)
        while len(set(output)) != 3 or ans in output:
            output = [words[randint(0, len(words) - 1)], words[randint(0, len(words) - 1)],
                      words[randint(0, len(words) - 1)]]

        output.insert(rand, ans)
        update_q(id, '{}#{}'.format(q, rand + 1), database)
        return output + ['Изучено']
    elif language_match('f', q):
        words = {'Fish', 'Pot+ato', 'Grass', 'Pasta', 'Bruise', 'Hunk', 'Car', 'Trunk', 'Mascara', 'Bugle'}
        words = words.union(set(list(dictionary['to_learn'].keys())))
        words = words.union(set(list(dictionary['learned'].keys())))
        words = list(words)
        print("THIS: ", words, get_ans(q, id, database), q)
        words.remove(get_ans(q, id, database))
        output = [words[randint(1, len(words) - 1)], words[randint(1, len(words) - 1)],
                  words[randint(1, len(words) - 1)]]
        while len(set(output)) != 3:
            output = [words[randint(0, len(words) - 1)], words[randint(0, len(words) - 1)],
                      words[randint(0, len(words) - 1)]]
        rand = randint(0, 3)
        output.insert(rand, ans)
        update_q(id, '{}#{}'.format(q, rand + 1), database)
        return output + ['Изучено']

def get_question(id, database, request):
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
    noScreen = False if "screen" in request.interfaces.keys() else True
    if (randint(0, 1) == 0 or noScreen or get_mode(id, database) == 'trainingen') and (get_mode(id, database) != 'trainingru'):
        update_q(id, list(dictionary[key].keys())[index_word], database)
        return '\n pause ' + (list(dictionary[key].keys())[index_word]).upper()
    else:
        word = list(dictionary[key].keys())[index_word]
        update_q(id, ', '.join(dictionary[key][word]), database)
        return '\n pause ' + (', '.join(dictionary[key][word])).upper()


def random_true(id, database):
    name = get_name(id, database)
    if name != "Noname":
        return choice(aliceAnswers["random_true"]["gender"]).format(name)
    return choice(aliceAnswers["random_true"]["no_gender"])


def random_false(id, database):
    name = get_name(id, database)
    if name != "Noname":
        return choice(aliceAnswers["random_false"]["gender"]).format(name)
    return choice(aliceAnswers["random_false"]["no_gender"])


def main(q, answer, q_type, id, database, request):
    print("!!!!! ! ! ! ! ! " + get_mode(id, database))
    if answer == 'help' or answer == 'помощь':
        return inf()
    elif answer == 'end' or answer == 'закончить' or answer == 'закончить тренировку':
        update_mode(id, 'end_training', database)
        q_count, q_true = get_stat_session('training', id, database)
        if q_count != 0:
            q_count -= 1
        if q_count > 1:
            if q_true / q_count > 0.85:
                sound = ' - <speaker audio="alice-sounds-game-win-3.opus">'
            elif q_true /  q_count > 0.7:
                sound = ' - <speaker audio="alice-sounds-game-win-1.opus">'
            else:
                sound = ''
        else:
            sound = ''
        return sound + choice(['Хорошо поиграли! ', 'Хорошая игра!', "Неплохо потренеровались!"]) + \
               ' Вы ответили на {} из {} моих вопросов.'.format(q_true, q_count) * (q_count > 1)
    elif get_stat_session('training', id, database) == [0, 0]:
        stat_session = get_stat_session('training', id, database)
        dictionary = get_dictionary(id, database)
        if len(dictionary['to_learn'].keys()) + len(dictionary['learned'].keys()) == 0:
            update_q(id, '###empty', database)
            return 'Словарь пуст. Для начала добавьте в него слова.'
        stat_session[0] += 1
        update_stat_session('training', stat_session, id, database)
        noScreen = False if "screen" in request.interfaces.keys() else True
        return 'Отвечай правильно, чтобы слова становились изученными.\n' + 'С английским языком я пока не так хорошо дружу, так что лучше используй кнопки при переводе русских слов. ' * (not noScreen)+\
               'Поехали!\n'+ get_question(id, database, request)
    elif q_type == 'revise&next':
        stat_session = get_stat_session('training', id, database)
        stat_session[0] += 1
        answer = answer.capitalize()
        if answer.lower().startswith('изучен'):
            if language_match(q, 'f'):
                q = get_ans(q, id, database)
            score = get_progress_mode('training', id, database)
            score[q] = 4
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
            return 'Слово теперь изучено' + '\n' + get_question(id, database, request)
        if revise(q, answer, q_type, id, database):
            if language_match(q, 'f'):
                q = get_ans(q, id, database)
            stat_session[1] += 1
            update_stat_session('training', stat_session, id, database)
            score = get_progress_mode('training', id, database)
            if q in score:
                score[q] += 1
            else:
                score[q] = 1
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
            return random_true(id, database) + '\n' + get_question(id, database, request)
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
            return random_false(id, database) + '\nПравильный ответ: pause "{}"\n'.format(get_ans(q, id, database)) + get_question(id, database, request)
    else:
        return False