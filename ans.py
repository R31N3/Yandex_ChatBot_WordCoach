def classify(text, mode):
    from little_fuctions import language_match
    if mode == '':
        mode = 0
    text = text.strip()
    text = text.lower()
    warning = True
    if text[0] == '+':
        add_word = True
        text = text[1:]
        text = text.strip()
    else:
        add_word = False
    if text[0] == '-':
        del_word = True
        text = text[1:]
        text = text.strip()
    else:
        del_word = False
    words = text.split()
    for i in range(len(text)):
        if text[i] == ' ':
            words = [text[:i], text[i + 1:]]
            if language_match(words[0], words[1]):
                break
    else:
        return {'warning': True, 'class': 'use_mode', 'answer': text}
    if (words[0].startswith('алиса') or words[0].startswith('alice')) and len(words) > 1:
        words = words[1:]
    if not words:
        return {'warning': True, 'class': 'use_mode', 'answer': text}
    if words[0].startswith('add') or words[0].startswith('добавь'):
        add_word = True
        if len(words) >= 2 and ((words[0].startswith('add') and words[1].startswith('word')) or (words[0].startswith('добавь') and words[1].startswith('слов'))):
            words = words[2:]
        else:
            words = words[1:]
    if not words:
        return {'warning': True, 'class': 'use_mode', 'answer': text}
    if words[0].startswith('delete') or words[0].startswith('del') or words[0].startswith('удали'):
        del_word = True
        words = words[1:]
    if not words:
        return {'warning': True, 'class': 'use_mode', 'answer': text}
    if add_word:
        if mode != 0:
            warning = True
        else:
            warning = False
        if del_word:
            answer = ''
            label = 'incorrect'
            warning = True
        elif len(words) == 1:
            label = 'translate&suggest_to_add'
            answer = words[0]
        elif len(words) == 2:
            label = 'add'
            answer = words[:]
        else:
            label = 'translate&suggest_to_add'
            answer = ' '.join(words)
    elif del_word:
        if mode != 0:
            warning = True
        else:
            warning = False
        label = 'del'
        answer = ' '.join(words)
    else:
        label = 'use_mode'
        answer = text
        warning = False

    return {'warning': warning, 'class': label, 'answer': answer}

print(classify('+ слово ebat blyat', 2))